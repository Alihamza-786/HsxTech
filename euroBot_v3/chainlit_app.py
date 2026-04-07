import os
import json
import uuid
import asyncio
import chainlit as cl
from langGraph_app import app
from langchain_core.messages import HumanMessage, AIMessage
import pandas as pd
from tabulate import tabulate
from typing import Dict, Any
from datetime import datetime

LOG_FILE = "conversation_logs.json"
HISTORY_MAX = 5
HISTORY_SQL_LAST_N = 2


def load_logs() -> list:
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_log(entry: Dict[str, Any]) -> None:
    logs = load_logs()
    logs.append(entry)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, default=str)


def update_history(state: dict, question: str, final_sql: str | None) -> list:
    """
    Keep last 5 questions.
    Only the last 2 entries keep their final SQL; older ones have sql=None.
    """
    history = state.get("history") or []
    history.append(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "question": question,
            "sql": final_sql,
        }
    )

    history = history[-HISTORY_MAX:]

    cutoff = max(0, len(history) - HISTORY_SQL_LAST_N)
    for i in range(0, cutoff):
        history[i]["sql"] = None

    return history        
# -------------------------------
# Chat session start
# -------------------------------

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set(
        "state",
        {
            "question": "",
            "sql": "",
            "rows": [],
            "error": None,
            "attempt": 1,
            "max_attempts": 2,
            "empty_ok": False,
            "output_mode": None,
            "human_answer": None,
            "dynamic_prompt": None,
            "labels": None,
            "history": [],  # ✅ NEW
            "elaboration": None,
        },
    )
    await cl.Message(content="👋 Hello! I'm your AI assistant. How can I help you today?").send()


# -------------------------------
# Chat message handler
# -------------------------------

# @cl.on_message
# async def on_message(msg: cl.Message):
#     state = cl.user_session.get("state")
#     state["question"] = msg.content
#     final_state = await app.ainvoke(state)

#     print("\n OUTPUT MODE: ", final_state)
#     if final_state.get("output_mode") != "HUMAN":
#         rows = final_state.get("rows", [])
#         if rows:
#             df = pd.DataFrame(rows)
#             elements = [cl.Dataframe(data=df, display="inline", name="Question Results")]
#             await cl.Message(content="Here are the results:", elements=elements).send()
#         else:
#             await cl.Message(content="No rows found.").send()

#     cl.user_session.set("state", {"question": "", "sql": "", "rows": [], "error": None, "attempt": 1, "max_attempts": 1, "empty_ok": False, "output_mode": None,"human_answer": None })
    
def clean_cell(x):
    """Convert dict/list/object-ish values to clean strings for display + CSV."""
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""

    # If it's already a simple scalar, keep it
    if isinstance(x, (int, float, bool, str)):
        return x

    # Handle dict like {'en_AU': 'SPARK PLUG ...'}
    if isinstance(x, dict):
        # Prefer common language keys first
        preferred_keys = ["en_US", "en_GB", "en_AU", "en", "name", "value", "label"]
        for k in preferred_keys:
            if k in x and isinstance(x[k], (str, int, float, bool)):
                return x[k]

        # Otherwise if dict has one key, return its value
        if len(x) == 1:
            v = next(iter(x.values()))
            return v if isinstance(v, (str, int, float, bool)) else json.dumps(v, ensure_ascii=False)

        # Fallback: JSON string
        return json.dumps(x, ensure_ascii=False)

    # Handle list/tuple/set
    if isinstance(x, (list, tuple, set)):
        # If list of scalars, join
        if all(isinstance(i, (str, int, float, bool)) or i is None for i in x):
            return ", ".join("" if i is None else str(i) for i in x)
        return json.dumps(list(x), ensure_ascii=False)

    # Pandas / numpy objects, or anything else
    return str(x)


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df.copy()

    # Normalize nested dicts to columns if you want (optional).
    # If you want to keep dicts as single cells, comment next line.
    # df2 = pd.json_normalize(df.to_dict(orient="records"), sep=".")

    for col in df2.columns:
        df2[col] = df2[col].map(clean_cell)

    return df2


def df_preview_text(df: pd.DataFrame, max_rows: int = 40, max_cols: int = 18) -> str:
    df2 = df.copy()

    # Limit columns (wide tables look bad in chat)
    if df2.shape[1] > max_cols:
        df2 = df2.iloc[:, :max_cols].copy()
        df2["..."] = "…"

    # Limit rows
    if len(df2) > max_rows:
        df2 = df2.head(max_rows)

    return tabulate(df2, headers="keys", tablefmt="github", showindex=False)


@cl.on_message
async def on_message(msg: cl.Message):
    state = cl.user_session.get("state") or {}
    state["question"] = msg.content

    final_state = await app.ainvoke(state)

    output_mode = final_state.get("output_mode")
    rows = final_state.get("rows", [])
    elaboration = final_state.get("elaboration")

    # ✅ Store history every turn
    final_sql_for_history = final_state.get("sql") if output_mode != "HUMAN" else None
    state["history"] = update_history(
        state=state,
        question=final_state.get("question") or msg.content,
        final_sql=final_sql_for_history,
    )

    # ✅ Log (also store history snapshot)
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "question": final_state.get("question"),
        "sql": final_state.get("sql"),
        "row_count": len(rows),
        "rows_preview": rows[:3],
        "error": final_state.get("error"),
        "output_mode": output_mode,
        "human_answer": final_state.get("human_answer"),
        "history_last_5": state["history"],
        "elaboration": elaboration,
    }
    save_log(log_entry)

    if output_mode != "HUMAN":
        if not rows:
            await cl.Message(content="No rows found.").send()
        else:
            MAX_ROWS = 150

            df_full = pd.DataFrame(rows)
            df_full = clean_df(df_full)

            total_rows = len(df_full)
            truncated = total_rows > MAX_ROWS

            # ✅ Apply hard limit only if needed
            df = df_full.head(MAX_ROWS) if truncated else df_full

            # ✅ Clear user-facing message
            if truncated:
                notice = (
                    f"⚠ Showing **first {MAX_ROWS} records** out of **{total_rows}** total records.\n\n"
                    "Download the full CSV for complete data."
                )
            else:
                notice = f"Showing **{total_rows}** rows."

            elements = [
                cl.Dataframe(
                    data=df,
                    display="inline",
                    name="Question Results",
                )
            ]

            await cl.Message(
                content=f"### 📊 Query Results\n{notice}",
                elements=elements,
            ).send()

            # --------------------
            # CSV export options
            # --------------------

            out_dir = os.path.join(os.getcwd(), "exports")
            os.makedirs(out_dir, exist_ok=True)
            csv_path = os.path.join(out_dir, "query_results.csv")

            # OPTION A (recommended): CSV = FULL DATA
            df_full.to_csv(csv_path, index=False, encoding="utf-8-sig")

            # OPTION B (if you want CSV to match UI exactly):
            # df.to_csv(csv_path, index=False, encoding="utf-8-sig")

            await cl.Message(
                content="📥 Download results:",
                elements=[
                    cl.File(
                        name=os.path.basename(csv_path),
                        path=csv_path,
                        display="inline",
                    )
                ],
            ).send()

    # ✅ Reset state BUT KEEP history
    cl.user_session.set(
        "state",
        {
            "question": "",
            "sql": "",
            "rows": [],
            "error": None,
            "attempt": 1,
            "max_attempts": 2,
            "empty_ok": False,
            "output_mode": None,
            "human_answer": None,
            "dynamic_prompt": None,
            "labels": None,
            "history": state.get("history", []),
            "elaboration": None,
        },
    )


# @cl.on_message
# async def on_message(msg: cl.Message):
#     state = cl.user_session.get("state") or {}
#     state["question"] = msg.content

#     final_state = await app.ainvoke(state)

#     output_mode = final_state.get("output_mode")
#     rows = final_state.get("rows", [])
#     elaboration = final_state.get("elaboration")  

#     # ✅ Store history every turn
#     final_sql_for_history = final_state.get("sql") if output_mode != "HUMAN" else None
#     state["history"] = update_history(
#         state=state,
#         question=final_state.get("question") or msg.content,
#         final_sql=final_sql_for_history,
#     )

#     # ✅ Log (also store history snapshot)
#     log_entry = {
#         "timestamp": datetime.utcnow().isoformat(),
#         "question": final_state.get("question"),
#         "sql": final_state.get("sql"),
#         "row_count": len(rows),
#         "rows_preview": rows[:3],
#         "error": final_state.get("error"),
#         "output_mode": output_mode,
#         "human_answer": final_state.get("human_answer"),
#         "history_last_5": state["history"],
#         "elaboration": elaboration,
#     }
#     save_log(log_entry)

#     if output_mode != "HUMAN":
#         if not rows:
#             await cl.Message(content="No rows found.").send()
#         else:
#             df = pd.DataFrame(rows)
#             df = clean_df(df)
#             df = df.head(200)
#             elements = [cl.Dataframe(data=df, display="inline", name="Question Results", pagination=False,)]
#             await cl.Message(content="Here are the results Question Results :", elements=elements).send()

#             out_dir = os.path.join(os.getcwd(), "exports")
#             os.makedirs(out_dir, exist_ok=True)
#             csv_path = os.path.join(out_dir, "query_results.csv")
#             df.to_csv(csv_path, index=False, encoding="utf-8-sig")

#             await cl.Message(
#                 content="📥 Download full results:", 
#                 elements=[cl.File(name=os.path.basename(csv_path), path=csv_path, display="inline")],
#             ).send()
#     # else:
#     #     await cl.Message(content=final_state.get("human_answer") or "").send()

#     # ✅ Reset state BUT KEEP history
#     cl.user_session.set(
#         "state",
#         {
#             "question": "",
#             "sql": "",
#             "rows": [],
#             "error": None,
#             "attempt": 1,
#             "max_attempts": 2,
#             "empty_ok": False,
#             "output_mode": None,
#             "human_answer": None,
#             "dynamic_prompt": None,
#             "labels": None,
#             "history": state.get("history", []),
#             "elaboration": None,
#         },
#     )



# -------------------------------
# Chat stop & end
# -------------------------------

@cl.on_stop
def on_stop():
    print("\nThe user wants to stop the task!")

@cl.on_chat_end
def on_chat_end():
    print("The user disconnected!")