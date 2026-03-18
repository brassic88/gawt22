import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import common, user, admin
from utils.scheduler import scheduler, schedule_reminder
from database.db import db


async def on_startup(bot: Bot):
    # Восстановление напоминаний при перезагрузке
    active_bookings = db.get_all_active_bookings()
    for booking in active_bookings:
        # booking: (id, date, time, user_id)
        schedule_reminder(bot, booking[3], booking[1], booking[2], booking[0])

    scheduler.start()


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_routers(common.router, user.router, admin.router)

    # Запуск
    print("Бот запущен!")
    await on_startup(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")