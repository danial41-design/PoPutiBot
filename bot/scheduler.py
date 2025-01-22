import asyncio
import aioschedule
from bot.database import Database

async def clear_database():
    Database.clear_deliveries()
    print("База данных очищена.")

async def scheduler():
    aioschedule.every().week.do(clear_database)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

def start_scheduler():
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler())
