import os
import chainlit as cl
from langgraph_app import my_graph
from chainlit.types import ThreadDict
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from langchain_core.messages import HumanMessage, AIMessage
from typing import Dict, Optional

from dotenv import load_dotenv
load_dotenv(override=True)

@cl.oauth_callback
def oauth_callback(
    provider_id: str,
    token: str,
    raw_user_data: Dict[str, str],
    default_user: cl.User,
) -> Optional[cl.User]:
    return default_user

#chat start
@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("state", {
        "messages": []
    })


#OnMessage
@cl.on_message
async def on_message(msg: cl.Message):
    seen_tool_calls = set()
    state = cl.user_session.get("state")
    state["messages"].append(HumanMessage(content=msg.content))
    msg_out = cl.Message(content="")
    await msg_out.send()

    final_text = ""
    try: 
        async for chunk in my_graph.astream(
            {"messages": state["messages"]},
            stream_mode="messages",
            version = 'v2'
        ):
            message_chunk, metadata = chunk['data']
            if hasattr(message_chunk, "tool_calls") and message_chunk.tool_calls:
                for tc in message_chunk.tool_calls:
                    tool_id = tc.get("id")

                    if tool_id in seen_tool_calls:
                        continue

                    seen_tool_calls.add(tool_id)

                    tool_name = tc.get("name")

                    if not tool_name:
                        continue

                    await msg_out.stream_token(
                        f"🔧 Calling tool: `{tool_name}`\n"
                    )

            if metadata.get("langgraph_node") != "agent":
                continue
            
            if not message_chunk.content:
                continue
            
            content = message_chunk.content

            if isinstance(content, str):
                final_text += content
                await msg_out.stream_token(content)

            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text = item.get("text", "")
                        final_text += text
                        await msg_out.stream_token(text)
                        
    except Exception as e:
        print("Stopped:", e)
    finally:
        if final_text: 
            msg_out.content = final_text
            await msg_out.update()

            state["messages"].append(AIMessage(content=final_text))
            cl.user_session.set("state", state)


# Resume chat
@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    try:
        steps = thread.get("steps", [])
        
        messages = []
        for step in steps:
            step_type = step.get("type")
            content = (step.get("output") or "").strip()
            if not content:
                continue 
        
            if step_type == "user_message":
                messages.append(HumanMessage(content=content))
            elif step_type == "assistant_message":
                messages.append(AIMessage(content=content))
        cl.user_session.set("state", {"messages": messages})
        print("\n\nMESSAGES LOADED: ", len(messages))
    except Exception as e:
        print(f"\nError resuming chat: {e}")
        cl.user_session.set("state", {"messages": []})

# # Authentication
# @cl.password_auth_callback
# def auth_callback(username: str, password: str):
#     if username == "admin" and password == "admin":
#         return cl.User(identifier="admin", metadata={"role": "admin"})
#     return None

# Data Layer
@cl.data_layer
def get_data_layer():
    conninfo = os.getenv("DATABASE_URL")
    
    if not conninfo:
        print("\nDATABASE_URL not found in environment variables.")
        return None

    try:
        data_layer = SQLAlchemyDataLayer(conninfo=conninfo)
        return data_layer
    except Exception as e:
        print(f"\n\nFailed to initialize SQLAlchemyDataLayer: {e}")
        return None

@cl.set_starters
async def set_starters():
    return [
    cl.Starter(
        label="💼 What is NETSOL Technologies?",
        message="What is NETSOL Technologies and what does the company do?",
    ),

    cl.Starter(
        label="🤖 NETSOL AI & Web3 solutions",
        message="What AI, blockchain, Web3, and emerging technology solutions does NETSOL provide?",
    ),

    cl.Starter(
        label="🌦️ Weather in Lahore",
        message="What is the current weather and forecast in Lahore, Pakistan?",
    ),

    cl.Starter(
        label="📧 Report Ready Email",
        message="Send an email to thehamzalog@gmail.com informing them that the report is ready and available for review.",
    ),

    cl.Starter(
        label="📅 Book a meeting",
        message="Schedule a meeting with Ahmed for tomorrow.",
    ),

    cl.Starter(
        label="🗓️ View today's meetings",
        message="What meetings do I have scheduled for today?",
    ),

    
]