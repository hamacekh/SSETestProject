# backend_server.py

from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
import asyncio
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('backend_server')


@app.get('/stream')
async def backend_stream(request: Request):
    logger.info('Client connected to backend stream.')

    async def event_generator():
        for i in range(1, 10):
            # Check if client has disconnected
            if await request.is_disconnected():
                logger.info('Client disconnected from backend stream.')
                break

            await asyncio.sleep(1)  # Simulate delay between events
            data = f'Event {i}'
            logger.info(f'Sending data: {data}')
            yield {'data': data}
        else:
            logger.info('Completed sending all events.')

    return EventSourceResponse(event_generator())


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('backend_server:app', host='0.0.0.0', port=8001, reload=True)
