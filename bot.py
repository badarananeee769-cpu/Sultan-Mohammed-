from telethon import TelegramClient
from telethon.errors import FloodWaitError
import asyncio

api_id = 27463772
api_hash = '173b628effb7d799253071c6bb3ebf62'

SOURCE_ID = -1003786409645
TARGET_ID = -1003973218247

SAVE_FILE = 'last_id.txt'


def get_last_id():
    try:
        with open(SAVE_FILE, 'r') as f:
            return int(f.read().strip())
    except:
        return 0


def save_last_id(msg_id):
    with open(SAVE_FILE, 'w') as f:
        f.write(str(msg_id))


async def send_batch(client, new_channel, batch, count):
    try:
        await client.forward_messages(new_channel, batch)

        save_last_id(batch[-1].id)
        count += len(batch)

        print(f'{count} | last_id: {batch[-1].id}')

        # ⬇️ تم التعديل هنا إلى 1 ثانية
        await asyncio.sleep(1)

    except FloodWaitError as e:
        print(f'flood: waiting {e.seconds}s')
        await asyncio.sleep(e.seconds + 1)

        return await send_batch(client, new_channel, batch, count)

    except Exception as e:
        print(f'error: {e}')
        await asyncio.sleep(5)

    return count


async def main():
    last_id = get_last_id()
    count = 0

    async with TelegramClient('session', api_id, api_hash) as client:

        old_channel = None
        new_channel = None

        dialogs = await client.get_dialogs()

        for d in dialogs:
            if d.id == SOURCE_ID:
                old_channel = d.entity
            if d.id == TARGET_ID:
                new_channel = d.entity

        if not old_channel or not new_channel:
            print('channel not found in dialogs')
            return

        print('started...')

        while True:
            try:
                batch = []

                async for msg in client.iter_messages(
                    old_channel,
                    min_id=last_id,
                    reverse=True,
                    limit=None
                ):
                    batch.append(msg)

                    if len(batch) == 1:
                        count = await send_batch(client, new_channel, batch, count)
                        batch = []

                if batch:
                    count = await send_batch(client, new_channel, batch, count)

                print(f'done: {count}')
                break

            except Exception as e:
                print(f'connection lost: {e}')
                await asyncio.sleep(10)
                continue


asyncio.run(main())
