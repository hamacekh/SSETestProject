# client.py

import aiohttp
import asyncio
import logging
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)s] %(message)s')
logger = logging.getLogger('client')

# Parse command-line arguments
parser = argparse.ArgumentParser(description='SSE Client')
parser.add_argument('--disconnect_at', type=int, default=None, help='Event number to disconnect at.')
parser.add_argument('--url', type=str, default='http://localhost:8000/stream', help='URL to connect to.')
args = parser.parse_args()

async def consume_stream():
    url = args.url

    logger.info(f'Connecting to {url}')

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                async for line in resp.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data:'):
                        data = line[5:].strip()
                        logger.info(f'Received data: {data}')
                        if args.disconnect_at is not None:
                            # Extract event number
                            try:
                                event_number = int(data.split(' ')[1])
                                if event_number == args.disconnect_at:
                                    logger.info(f'Disconnecting at event {event_number}')
                                    return
                            except (IndexError, ValueError):
                                logger.warning(f'Unexpected data format: {data}')
                    elif line == '':
                        continue  # Ignore keep-alive
                    else:
                        logger.info(f'Received non-data line: {line}')
        except Exception as e:
            logger.error(f'Error: {e}')

    logger.info('Session closed.')

if __name__ == '__main__':
    asyncio.run(consume_stream())
