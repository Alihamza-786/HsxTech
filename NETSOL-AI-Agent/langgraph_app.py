from zoneinfo import ZoneInfo
from datetime import datetime
from dotenv import load_dotenv
from prompts import AGENT_PROMPT

from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from typing import Annotated, Sequence, TypedDict
from langgraph.graph import StateGraph, START, END
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, BaseMessage
from tools import tools,  google_search, rag_retrieval #create_fresh_calendar_service,

load_dotenv(override=True)

# for tool in tools:
#     if hasattr(tool, "_run"):
#         original_run = tool._run
        
#         def make_safe_run(original_run, tool_obj=tool):
#             def safe_run(*args, **kwargs):
#                 # Force fresh service before every API call
#                 fresh_service = create_fresh_calendar_service()
                
#                 # Patch the resource if it exists
#                 if hasattr(tool_obj, "api_resource"):
#                     tool_obj.api_resource = fresh_service
                
#                 # Some tools store it as _service or similar
#                 if hasattr(tool_obj, "_service"):
#                     tool_obj._service = fresh_service
                
#                 return original_run(*args, **kwargs)
#             return safe_run
        
#         tool._run = make_safe_run(original_run)


tools.append(google_search)
tools.append(rag_retrieval)

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     temperature=0,
#     streaming = True
# ).bind_tools(tools)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    # model = 'gpt-4o',
    temperature=0,
    streaming=True
).bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


async def agent_node(state: AgentState) -> AgentState:
    """It is the agent node"""
    print("********AGENT********")

    now = datetime.now(ZoneInfo("Asia/Karachi"))
    now_time = f"Time zone: Asia/Karachi, Date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    system_prompt = SystemMessage(
        content=f"{AGENT_PROMPT}\n----- CURRENT_DATE_TIME: {now_time}"
    )
    response = await llm.ainvoke([system_prompt] + state["messages"][-10:])
    
    return {"messages": [response]}


def should_continue(state):
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        print("\n🔍 ROUTER DEBUG")
        print("TOOL CALLS:", getattr(last, "tool_calls", None))
        return "tool_call"

    return "end"
    
# Graph Builder
graph_builder = StateGraph(AgentState)
graph_builder.add_node("agent", agent_node)
tool_node = ToolNode(tools = tools)
graph_builder.add_node("tools", tool_node)


graph_builder.add_edge(START, "agent")
graph_builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tool_call": "tools",
        "end": END
    }
)
graph_builder.add_edge("tools", "agent")

my_graph = graph_builder.compile()