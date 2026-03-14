import asyncio

from python.helpers.api import ApiHandler, Request, Response

from python.helpers import process


class Restart(ApiHandler):
    async def process(self, input: dict, request: Request) -> dict | Response:
        # Schedule reload after response is sent to avoid ASGI 500.
        asyncio.get_event_loop().call_later(0.5, process.reload)
        return {"message": "Restarting..."}
