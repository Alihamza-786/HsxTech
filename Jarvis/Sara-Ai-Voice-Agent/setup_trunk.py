import asyncio
import os
import sys

from dotenv import load_dotenv
from livekit import api

load_dotenv(".env.local")

# Public IP of your VM
ASTERISK_PUBLIC_IP = os.getenv('ASTERISK_PUBLIC_IP')

# MUST match /etc/asterisk/pjsip.conf
ASTERISK_SIP_USERNAME = os.getenv('AUTH_USERNAME')
ASTERISK_SIP_PASSWORD = os.getenv('AUTH_PASSWORD')

async def create_trunk():

    async with api.LiveKitAPI(
        url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET"),
    ) as lk:

        trunk = await lk.sip.create_outbound_trunk(
            api.CreateSIPOutboundTrunkRequest(
                trunk=api.SIPOutboundTrunkInfo(

                    name="livekit-via-asterisk",

                    address=ASTERISK_PUBLIC_IP,

                    transport=api.SIPTransport.SIP_TRANSPORT_UDP,

                    auth_username=ASTERISK_SIP_USERNAME,

                    auth_password=ASTERISK_SIP_PASSWORD,

                    numbers=
                        "04232468232"
                )
            )
        )

        print("\nSIP trunk created successfully!")
        print(f"Trunk ID: {trunk.sip_trunk_id}")
        print("\nSIP trunk created successfully!")
        print(f"Trunk Name : {trunk.name}")
        print(f"Trunk ID   : {trunk.sip_trunk_id}")

        print("\nUse this command to test calls:")
        print(f"uv run call_testing.py dial {trunk.sip_trunk_id} 0")


async def list_trunks():
    async with api.LiveKitAPI(
        url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET"),
    ) as lk:

        result = await lk.sip.list_sip_outbound_trunk(
            api.ListSIPOutboundTrunkRequest()
        )

        if not result.items:
            print("No SIP trunks found.")
            return

        print("\nExisting SIP Trunks:\n")

        for trunk in result.items:
            print(f"ID      : {trunk.sip_trunk_id}")
            print(f"Name    : {trunk.name}")
            print(f"Address : {trunk.address}")
            print("-" * 50)


async def delete_trunk(trunk_id: str):
    async with api.LiveKitAPI(
        url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET"),
    ) as lk:

        await lk.sip.delete_sip_trunk(
            api.DeleteSIPTrunkRequest(
                sip_trunk_id=trunk_id
            )
        )

        print(f"Deleted trunk: {trunk_id}")


if __name__ == "__main__":

    if len(sys.argv) >= 2 and sys.argv[1] == "list":
        asyncio.run(list_trunks())

    elif len(sys.argv) >= 3 and sys.argv[1] == "delete":
        asyncio.run(delete_trunk(sys.argv[2]))

    else:
        asyncio.run(create_trunk())