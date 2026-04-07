import chainlit as cl
from chainlit import AskUserMessage, Message, on_chat_start, on_message, on_chat_resume, File
from langchain_core.messages import HumanMessage, AIMessage
from langgraph_chatbot import langgraph_app
import json
import os
import asyncio
from typing import Optional

SAVE_FILE = "final_states.json"
if not os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "w") as f:
        json.dump([], f)


def serialize_message(msg):
    if isinstance(msg, HumanMessage):
        return {"type": "human", "content": msg.content}
    # Handle other types as needed
    return str(msg)


def deserialize_messages(chat_id):
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)
    messages = data.get(chat_id, [])
    return [HumanMessage(content=m["content"]) if m["type"] == "human" else AIMessage(content=m["content"]) for m in messages]



@on_chat_start
async def main():
    cl.user_session.set("messages", [])
    await asyncio.sleep(2)
    await Message(
        content=f"Hello! I'm here to help you with any questions you have about 'Home Salon by Nooora'. How can I help you today?",
    ).send()


@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("messages")
    user_msg = {
        "messages": [HumanMessage(content=message.content)]
    }
    # if len(history) == 0:
    #     await set_chat_title("Booking Inquiry with Nooora")

    history.append(user_msg["messages"][0])
    state = {"messages": history}
    # print(user_msg["messages"][0])
    final_state = await langgraph_app.ainvoke(state)
    # final_state = await langgraph_app.ainvoke(user_msg)
    # print(final_state)
    final_answer = final_state.get("final_answer", "Sorry, I couldn't get an answer.")
    # q_result = final_state.get("query_result", "Sorry, I couldn't get an answer.")
    # if q_result == None:
    #     q_result = "No Answer found"

    # qry_result = AIMessage(content=q_result)   
    # history.append(qry_result)
    
    # print("history")
    # print(history)
    history.pop()
    # print()
    # print(history)
    ref_ques = final_state.get("rewritten_question")
    refined_question = HumanMessage(ref_ques)
    history.append(refined_question)
    history = history[-7:]
    # ai_msg = AIMessage(content=final_answer)
    # history.append(ai_msg)
    cl.user_session.set("messages", history)
    # print(history)
    with open(SAVE_FILE, "r+") as f:
        all_states = json.load(f)
        all_states.append(final_state)
        f.seek(0)
        json.dump(
            [serialize_message(msg) for msg in all_states],
            f,
            indent=2
        )

    file_type = final_state.get("save_to_file")

    file_name = None
    mime_type = None
    file_label = None

    if file_type:
        if "EXCEL" in file_type:
            file_name = "data.xlsx"
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            file_label = "📊 Here is your Excel file:"

        elif "CSV" in file_type:
            file_name = "data.csv"
            mime_type = "text/csv"
            file_label = "📄 Here is your CSV file:"

        

        # Send Excel or CSV file if needed
        if file_name:
            with open(file_name, "rb") as f:
                content_bytes = f.read()

            await cl.Message(
                content=file_label,
                elements=[
                    File(
                        name=file_name,
                        content=content_bytes,
                        mime=mime_type
                    )
                ]
            ).send()    

    # await cl.Message(content=final_answer).send()

# @cl.password_auth_callback
# def auth_callback(username: str, password: str) -> Optional[cl.User]:
#     if (username, password) == ("admin", "admin"):
#         return cl.User(identifier="admin", metadata={"role": "ADMIN"})
#     else:
#         return None


# @cl.on_chat_resume
# async def on_chat_resume(thread):
#     pass
@on_chat_resume
async def on_chat_resume(session_id: str):
    # Load saved chat history from disk (or DB)
    with open("final_states.json", "r") as f:
        all_states = json.load(f)

    # Example: use session_id to find a specific chat (if you're storing session ids per state)
    # For now, we'll just load the latest few messages
    messages = []
    for state in all_states[-7:]:  # load recent messages
        if state.get("rewritten_question"):
            messages.append(cl.Message(author="user", content=state["rewritten_question"]))
        if state.get("final_answer"):
            messages.append(cl.Message(author="assistant", content=state["final_answer"]))

    # Set them in user session so future messages build on this
    cl.user_session.set("messages", messages)

    # Replay messages to UI
    for msg in messages:
        await msg.send()

@cl.on_chat_end
def on_chat_end():
    # cl.user_session.clear()
    print("Session history cleared.", cl.user_session.get("id"))

@cl.on_stop
def on_stop():
    print("The user wants to stop the task!")

