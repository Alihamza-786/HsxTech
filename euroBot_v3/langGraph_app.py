from __future__ import annotations
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END
from typing import Any, Dict, List, Optional, Tuple, TypedDict
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from prompts_secret import narrator_system_prompt, router_system_prompt, CORE_ODOO_SQL_PROMPT, RULES_BY_TYPE, CLASSIFIER_SYSTEM_PROMPT, elaboration_system_prompt
from all_functions import make_history_user_block, extract_text
from db_helper import db_url
from dotenv import load_dotenv
import chainlit as cl
import asyncio
from langchain.chat_models import init_chat_model
load_dotenv()

# SQL_SYSTEM_PROMPT = init_prompt()
ROUTER_SYSTEM_PROMPT = router_system_prompt()
NARRATOR_SYSTEM_PROMPT = narrator_system_prompt()
ELABORATION_SYSTEM_PROMPT = elaboration_system_prompt()


# -----------------------------
# Agent state 
# -----------------------------
class AgentState(TypedDict):
    question: str
    labels: List[str]
    dynamic_prompt: str
    sql: str
    rows: List[Dict[str, Any]]
    error: Optional[str]
    attempt: int
    max_attempts: int
    empty_ok: bool
    output_mode: Optional[str]
    human_answer: Optional[str]
    history: List[Dict[str, Any]]  
    elaboration: Optional[str] 



# -----------------------------
# 2) DB EXECUTION
# -----------------------------

def run_sql(engine: Engine, sql: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    try:
        with engine.begin() as conn:
            result = conn.execute(text(sql))
            # print(result)
            if result.returns_rows:
                cols = list(result.keys())
                rows = [dict(zip(cols, row)) for row in result.fetchall()]
                # print("\n\nROWS", rows, "\n\n")
                return rows, None
            return [], None
    except SQLAlchemyError as e:
        print("Failed SQL:", e)
        
        return [], f"{e.__class__.__name__}: {e}"


# -----------------------------
# 3) LLM HELPERS
# -----------------------------

def llm(model: str = "gpt-5-mini"):
    return init_chat_model(model = model, timeout=120)

def llm_reasoning(model: str = "gpt-5-mini", reasoning: str =  "minimal"):
    return init_chat_model(model = model, timeout=120, reasoning={"effort": reasoning})

final_llm = ChatOpenAI(model="gpt-5-nano", streaming = True, reasoning_effort= "minimal")
elaboration_llm = ChatOpenAI(model="gpt-5-nano", streaming=True, reasoning_effort= "minimal")

def parse_labels(raw: str) -> List[str]:
    if not raw:
        return ["other"]

    parts = [p.strip() for p in raw.split(",") if p.strip()]
    seen = set()
    out: List[str] = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            out.append(p)

    # Validate labels against RULES_BY_TYPE keys + special labels
    allowed = set(RULES_BY_TYPE.keys()) | {"greeting", "other"}
    out = [x for x in out if x in allowed]
    return out or ["other"]



def classify_question(question: str, history_block: str) -> List[str]:
    print("----------------------INITIAL CLASSIFICATION----------------------")
    msg = f"""
    History (Questions along with their SQL):
    {history_block}

    Current Question: 
    {question}
    """
    resp = llm_reasoning(model="gpt-5-mini", reasoning= "minimal").invoke(
        [
            SystemMessage(content=CLASSIFIER_SYSTEM_PROMPT),
            HumanMessage(content=msg),
        ]
    )
    text = resp.text if hasattr(resp, "text") else extract_text(resp)
    print(resp)
    # print("#################################")
    # print(resp.content)
    return parse_labels((text or "").strip())
    # return parse_labels((resp.content or "").strip())


def build_sql_system_prompt(labels: List[str]) -> str:
    """
    Build system prompt from CORE + all matched question-specific rule blocks.
    If multiple labels => merge their rules (dedup via join).
    """
    blocks: List[str] = []
    for lab in labels:
        extra = RULES_BY_TYPE.get(lab, "")
        if extra:
            blocks.append(extra.strip())

    if blocks:
        return CORE_ODOO_SQL_PROMPT + "\n\nQUESTION-SPECIFIC RULES:\n" + "\n\n".join(blocks)

    return CORE_ODOO_SQL_PROMPT


# -----------------------------
# 4) Nodes
# -----------------------------
def node_classify(state: AgentState) -> AgentState:
    print("----------------------CLASSIFY----------------------")
    history_block = make_history_user_block(state)
    labels = classify_question(state["question"], history_block)
    print(labels)
    state["labels"] = labels
    return state


def should_generate_or_greet(state: AgentState) -> str:
    # If greeting detected, skip SQL entirely
    if "greeting" in (state.get("labels") or []):
        return "greet"
    return "generate"


def node_greet(state: AgentState) -> AgentState:
    print("----------------------GREET----------------------")
    # Short-circuit: produce a human answer and finish.
    # Keep it simple and deterministic.
    state["output_mode"] = "HUMAN"
    state["human_answer"] = "Hi! Ask me a question about sales, customers, warehouses, or inventory, and I’ll answer about those."
    state["elaboration"] = None 
    return state


def node_generate(state: AgentState) -> AgentState:
    print("----------------------GENERATE SQL----------------------")
    labels = state.get("labels") or ["other"]
    dynamic_prompt = build_sql_system_prompt(labels)

    history_block = make_history_user_block(state)
    user_msg = f"""
    History (Questions along with their SQL):
    {history_block}

    Current User Question:
    {state["question"]}
    """

    resp = llm_reasoning(model= "gpt-5.1", reasoning= "low").invoke(
        [
            SystemMessage(content=dynamic_prompt),
            HumanMessage(content=user_msg),
        ]
    )

    text = resp.text if hasattr(resp, "text") else extract_text(resp)
    print(resp)
    print("#############################################################")
    # print(resp.content)
    state["dynamic_prompt"] = dynamic_prompt
    # state["sql"] = (resp.content or "").strip()
    state["sql"] = (text or "").strip()
    state["attempt"] = state.get("attempt", 1)
    # print(state["sql"])
    return state



def node_execute(engine: Engine):
    def _inner(state: AgentState) -> AgentState:
        print("----------------------EXECUTE SQL----------------------")
        print(state["sql"])
        rows, err = run_sql(engine, state["sql"])
        state["rows"] = rows
        state["error"] = err
        return state

    return _inner



def repair_sql(
    question: str,
    dynamic_prompt: str,
    previous_sql: str,
    error: Optional[str],
    was_empty: bool,
    history_block: str,
) -> str:
    msg = f"""
    History (Questions along with their SQL):
    {history_block}

    Current User Question:
    {question}

    Errored SQL:
    {previous_sql}

    Failure:
    - Error: {error if error else "None"}
    - Empty result: {"Yes" if was_empty else "No"}

    Fix the SQL for Odoo 16 PostgreSQL. Return SQL only.
    """.strip()

    resp = llm(model="gpt-5.1").invoke(
        [
            SystemMessage(content=dynamic_prompt),
            HumanMessage(content=msg),
        ]
    )
    print(resp)
    return (resp.content or "").strip()




def node_repair(state: AgentState) -> AgentState:
    print("----------------------REPAIR SQL----------------------")
    was_empty = (state.get("error") is None) and (len(state.get("rows", [])) == 0)
    history_block = make_history_user_block(state)

    state["sql"] = repair_sql(
        question=state["question"],
        dynamic_prompt=state.get("dynamic_prompt", CORE_ODOO_SQL_PROMPT),
        previous_sql=state["sql"],
        error=state.get("error"),
        was_empty=was_empty,
        history_block=history_block,
    )
    state["attempt"] = state.get("attempt", 1) + 1
    state["error"] = None
    state["rows"] = []
    return state


def should_retry(state: AgentState) -> str:
    if state.get("attempt", 1) >= state.get("max_attempts", 2):
        return "stop"

    if state.get("error") is not None:
        return "repair"

    if (len(state.get("rows", [])) == 0) and (not state.get("empty_ok", False)):
        return "repair"

    return "ok"


def node_route_output(state: AgentState) -> AgentState:
    print("----------------------ROUTE OUTPUT----------------------")
    rows = state.get("rows", [])
    preview = rows[:3]

    history_block = make_history_user_block(state, keep_sql_last_n=0)

    payload = {
        "current question": state["question"],
        "row_count": len(rows),
        "preview_rows": preview,
        "history (Questions along with their SQL)": history_block,
    }

    resp = llm_reasoning(model="gpt-5-mini", reasoning= "minimal").invoke(
        [
            SystemMessage(content=ROUTER_SYSTEM_PROMPT),
            HumanMessage(content=json.dumps(payload, default=str)),
        ]
    )

    print(resp)
    text = resp.text if hasattr(resp, "text") else extract_text(resp)
    # decision = (resp.content or "").strip().upper()
    decision = (text or "").strip().upper()
    state["output_mode"] = "HUMAN" if decision == "HUMAN" else "TABLE"
    return state



def route_to_narrator(state: AgentState) -> str:
    return "narrate" if state.get("output_mode") == "HUMAN" else "elaborate"



# Streaming
async def stream_llm_response(messages: List[BaseMessage]) -> AIMessage:
    msg = cl.Message(content="")
    await msg.send()

    content = ""
    try:
        async for chunk in final_llm.astream(messages):
            if chunk.content:
                content += chunk.content
                await msg.stream_token(chunk.content)
    except asyncio.CancelledError:
        pass

    await msg.update()
    return AIMessage(content=content)



# NEW: Streaming for elaboration
async def stream_elaboration_response(messages: List[BaseMessage]) -> AIMessage:
    """Stream elaboration response with a distinct message"""
    msg = cl.Message(content="")
    await msg.send()

    content = ""
    try:
        async for chunk in elaboration_llm.astream(messages):
            if chunk.content:
                content += chunk.content
                await msg.stream_token(chunk.content)
    except asyncio.CancelledError:
        pass

    await msg.update()
    return AIMessage(content=content)



async def node_narrate(state: AgentState) -> AgentState:
    print("----------------------NARRATE----------------------")
    rows = state.get("rows", [])

    history_block = make_history_user_block(state)

    payload = {
        "current question": state["question"],
        "sql": state.get("sql", ""),
        "row_count": len(rows),
        "rows": rows[:30],
        "history (Questions along with their SQL)": history_block,
    }

    prompt = [
        SystemMessage(content=NARRATOR_SYSTEM_PROMPT),
        HumanMessage(content=json.dumps(payload, default=str)),
    ]
    resp = await stream_llm_response(prompt)
    state["human_answer"] = (resp.content or "").strip()
    state["elaboration"] = None 
    return state



# NEW: Elaboration node for TABLE output mode
async def node_elaborate(state: AgentState) -> AgentState:
    """
    Generate a human-readable elaboration of the SQL query and results.
    This runs for TABLE output mode to explain what data was fetched.
    """
    print("----------------------ELABORATE----------------------")
    rows = state.get("rows", [])
    sql = state.get("sql", "")
    history_block = make_history_user_block(state)

    # Prepare payload with query info and sample results
    payload = {
        "current_user_question": state["question"],
        "current_question_sql": sql,
        "row_count": len(rows),
        "preview_rows": rows[:3] if rows else [],  # Show first 2-3 rows as sample
        "history (Questions along with their SQL)": history_block,
    }

    prompt = [
        SystemMessage(content=ELABORATION_SYSTEM_PROMPT),
        HumanMessage(content=json.dumps(payload, default=str)),
    ]
    
    resp = await stream_elaboration_response(prompt)
    state["elaboration"] = (resp.content or "").strip()
    return state

# -----------------------------
# 5) Graph
# -----------------------------
def build_graph(engine: Engine):
    g = StateGraph(AgentState)

    g.add_node("classify", node_classify)
    g.add_node("greet", node_greet)
    g.add_node("generate", node_generate)
    g.add_node("execute", node_execute(engine))
    g.add_node("repair", node_repair)
    g.add_node("route_output", node_route_output)
    g.add_node("narrate", node_narrate)
    g.add_node("elaborate", node_elaborate)

    g.set_entry_point("classify")

    g.add_conditional_edges(
        "classify",
        should_generate_or_greet,
        {
            "greet": "greet",
            "generate": "generate",
        },
    )

    g.add_edge("greet", END)

    g.add_edge("generate", "execute")

    g.add_conditional_edges(
        "execute",
        should_retry,
        {
            "repair": "repair",
            "ok": "route_output",
            "stop": "route_output",
        },
    )

    g.add_edge("repair", "execute")

    g.add_conditional_edges(
        "route_output",
        route_to_narrator,
        {
            "narrate": "narrate",
            "elaborate": "elaborate",
        },
    )

    g.add_edge("narrate", END)
    g.add_edge("elaborate", END)

    return g.compile()



# -----------------------------
# 5) RUNNER
# -----------------------------

DB_URL = db_url()
engine = create_engine(DB_URL, pool_pre_ping=True, future=True)
app = build_graph(engine)
