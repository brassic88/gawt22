import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import common, user, admin
from utils.scheduler import scheduler, schedule_reminder
from database.db import db

async def on_startup(bot: Bot):
    bookings = db.get_all_active_bookings()
    for b in bookings:
        schedule_reminder(bot, b[3], b[1], b[2], b[0])
    scheduler.start()

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_routers(common.router, admin.router, user.router)
    await on_startup(bot)
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())