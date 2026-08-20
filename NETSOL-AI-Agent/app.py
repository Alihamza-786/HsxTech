from fastapi import FastAPI
from chainlit.utils import mount_chainlit
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.title = "NetBot"



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/app")
def read_main():
    return {"message": "Hello World from main app"}

mount_chainlit(
    app=app,
    target="chainlit_app.py",
    path="/chatbot",
)