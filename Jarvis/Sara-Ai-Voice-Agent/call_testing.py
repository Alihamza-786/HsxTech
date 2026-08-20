import asyncio
import json
import logging
import os
import sys
import time
from livekit.agents.voice import TurnHandlingOptions
from dotenv import load_dotenv
from livekit import api
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    # TurnHandlingOptions,
    cli,
    room_io,
)

from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.plugins import ai_coustics, silero, google
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv(".env.local")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger("call-testing")

CUSTOMERS_FILE = "customers.json"


def load_customers():
    with open(CUSTOMERS_FILE, "r") as f:
        return json.load(f)


def build_agent_prompt(customer):
    products = ", ".join(customer["products_bought_previously"])

    return f"""
    You are a friendly customer care calling agent.

    Customer name: {customer["name"]}
    City: {customer["city"]}
    Previous purchases: {products}

    Rules:
    - Speak naturally.
    - Keep answers short.
    - Be polite.
    - If customer speaks Urdu, respond naturally in Urdu.
    - Never sound robotic.
    """


class SalesAgent(Agent):

    def __init__(self, customer):
        self.customer = customer
        super().__init__(
            instructions=build_agent_prompt(customer)
        )

    async def on_enter(self):

        first_name = self.customer["name"].split()[0]

        await self.session.generate_reply(
            instructions=(
                f"Say: Hello {first_name}, "
                f"this is a quick follow-up call from customer care. "
                f"How are you today?"
            ),
            allow_interruptions=True,
        )


server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session()
async def entrypoint(ctx: JobContext):

    await ctx.connect()

    customers = load_customers()

    customer = customers[0]

    room_name = ctx.room.name

    for c in customers:

        normalized = (
            c["contact"]
            .replace("+", "")
            .replace("-", "")
        )

        if normalized in room_name:
            customer = c
            break

    logger.info(f"Starting call for: {customer['name']}")

    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            voice="Aoede",
        ),

        turn_handling=TurnHandlingOptions(
            turn_detection=MultilingualModel()
        ),
        # turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
    )

    await session.start(
        room=ctx.room,

        agent=SalesAgent(customer),

        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=ai_coustics.audio_enhancement(
                    model=ai_coustics.EnhancerModel.QUAIL_VF_L,
                ),
            ),
        ),
    )


async def dial_customer(customer, trunk_id):

    async with api.LiveKitAPI(
        url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET"),
    ) as lk:

        phone = (
            customer["contact"]
            .replace("+", "")
            .replace("-", "")
        )

        room_name = f"call-{phone}-{int(time.time())}"

        await lk.room.create_room(
            api.CreateRoomRequest(name=room_name,
                                  empty_timeout=10,
                                  departure_timeout=5)
        )

        logger.info(f"Dialing {phone}")

        participant = await lk.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                sip_trunk_id=trunk_id,

                sip_call_to=phone,

                room_name=room_name,

                participant_identity=f"customer-{phone}",

                participant_name=customer["name"],

                #play_dialtone=True,
                play_ringtone=True,
                wait_until_answered=False,
            )
        )

        logger.info(
            f"Call initiated: "
            f"{participant.participant_identity}"
        )


if __name__ == "__main__":

    if len(sys.argv) >= 2 and sys.argv[1] == "dial":

        trunk_id = sys.argv[2]

        index = int(sys.argv[3]) if len(sys.argv) > 3 else 0

        customers = load_customers()

        asyncio.run(
            dial_customer(customers[index], trunk_id)
        )

    else:
        cli.run_app(server)