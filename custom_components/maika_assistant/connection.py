import logging
import asyncio
import websockets
import json
import aiohttp
from websockets.exceptions import ConnectionClosed, InvalidStatusCode
from .const import WS_HASS_URL

_LOGGER = logging.getLogger(__name__)

def combine_buffer_message(bufMsg, bufData):
    bufLenMsg = (len(bufMsg)).to_bytes(4, byteorder='big')
    bufLenData = (len(bufData)).to_bytes(4, byteorder='big')
    return bufLenMsg + bufLenData + bufMsg + bufData

async def ws_send(queue, msg):
    await queue.put(msg)

async def ws_consumer_handler(websocket, ws_queue, url):
    session = aiohttp.ClientSession(auto_decompress=False)
    while True:
        try:
            message = await websocket.recv()
            data = json.loads(message)
            if data['topic'] == 'access_token':
                if data['status'] != 0:
                    _LOGGER.info("No reconnect, force close Maika connection")
            elif data['topic'] == 'http_request':
                _url = "{url}{path}".format(url = url, path = data['data']['path'])
                headers = data['data']['headers']
                method = data['data']['method']
                if 'body' in data['data']:
                    if data['data']['headers']['content-type'] == "application/x-www-form-urlencoded":
                        payload = data['data']['body']
                    elif data['data']['headers']['content-type'] == "text/plain;charset=UTF-8":
                        payload = json.dumps(data['data']['body'])
                    elif data['data']['headers']['content-type'] == "application/json":
                        payload = json.dumps(data['data']['body'])
                    else:
                        payload = str(data['data']['body']).encode('utf-8')
                else:
                    payload = None

                if method == 'POST':
                    if data['data']['path'].find('/auth/login_flow') != -1:
                        headers = {}
                        headers["Content-Type"] = data['data']['headers']['content-type']

                response = await session.request(method, _url, headers=headers, data=payload, ssl=False)

                body = await response.read()

                message = {
                    "topic": "http_response",
                    "requestId": data['requestId'],
                    "payload": {
                        "status": 0,
                        "statusCode": response.status,
                        "headers": dict(response.headers)
                    },
                }
                bufMsg = bytes(json.dumps(message),'UTF-8')
                buf_full = combine_buffer_message(bufMsg, body)
                await ws_send(ws_queue, buf_full)
        except (Exception):
            _LOGGER.warning("Maika connection is Closed")
            break

async def ws_producer_handler(websocket, ws_queue):
    while True:
        message = await ws_queue.get()
        await websocket.send(message)

async def ws_async_processing(api_key, url):
    ws_queue = asyncio.Queue()
    while True:
        _LOGGER.info(">Start Maika connection")
        try:
            async with websockets.connect(WS_HASS_URL) as websocket:
                consumer_task = asyncio.ensure_future(ws_consumer_handler(websocket, ws_queue, url))
                producer_task = asyncio.ensure_future(ws_producer_handler(websocket, ws_queue))
                message = {
                    "topic": "access_token",
                    "payload": {
                        "token": api_key
                    }
                }
                bufMsg = bytes(json.dumps(message),'UTF-8')
                bufData = bytes([])
                buf_full = combine_buffer_message(bufMsg, bufData)
                await ws_send(ws_queue, buf_full)
                done, pending = await asyncio.wait(
                    [producer_task, consumer_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )
                for task in pending:
                    task.cancel()
                await asyncio.sleep(10)
                _LOGGER.info("Restart Maika connection>")
        except (Exception):
            _LOGGER.warning("Maika server rejected connection")
            await asyncio.sleep(10)
            _LOGGER.info("Restart Maika connection>")
            pass