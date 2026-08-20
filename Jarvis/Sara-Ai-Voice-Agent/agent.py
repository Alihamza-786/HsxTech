# Jarvis/livekit-support-agent/.venv/bin/activate
# (livekit-support-agent) ali@ali:~/AI/12.Jarvis/livekit-support-agent$ uv run agent.py dev
import os
from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import google
from prompts import AGENT_INSTRUCTIONS
from tools import unblock_user
from livekit.plugins import (
    bey,
    noise_cancellation,
    google
)

load_dotenv(".env.local")

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=AGENT_INSTRUCTIONS,
        tools=[unblock_user]
        )

server = AgentServer()

@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    session = AgentSession(
        # llm=openai.realtime.RealtimeModel(
        #     voice="coral"
        # )
        llm=google.beta.realtime.RealtimeModel(
            voice="Aoede"
        )
    )

    avatar = bey.AvatarSession(
    avatar_id=os.getenv("BEY_AVATAR_ID"),
    )
    
    # Start the avatar and wait for it to join
    await avatar.start(session, room=ctx.room)
    
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony() if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP else noise_cancellation.BVC(),
               
            ),
            video_input=True,
        ),
    )

    await session.generate_reply(
        instructions="Greet the user and offer your assistance. You should start by speaking in URDU."
    )


if __name__ == "__main__":
    agents.cli.run_app(server)