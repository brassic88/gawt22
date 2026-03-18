from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore  # Исправленный импорт
from datetime import datetime, timedelta
from config import DB_NAME

# Для SQLite в APScheduler используется SQLAlchemyJobStore
jobstores = {
    'default': SQLAlchemyJobStore(url=f'sqlite:///jobs.sqlite')  # Отдельный файл для задач, чтобы не мешать основной БД
}

scheduler = AsyncIOScheduler(jobstores=jobstores)


async def send_reminder(bot, user_id, time_str):
    try:
        await bot.send_message(
            user_id,
            f"🔔 <b>Напоминание!</b>\n\nВы записаны на процедуру завтра в <b>{time_str}</b>. Ждём вас! ✨",
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Ошибка отправки напоминания пользователю {user_id}: {e}")


def schedule_reminder(bot, user_id, date_str, time_str, slot_id):
    # Пытаемся распарсить дату и время
    try:
        run_date = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M") - timedelta(hours=24)

        # Если до записи больше 24 часов — планируем
        if run_date > datetime.now():
            scheduler.add_job(
                send_reminder,
                'date',
                run_date=run_date,
                args=[bot, user_id, time_str],
                id=f"remind_{slot_id}",
                replace_existing=True
            )
    except Exception as e:
        print(f"Не удалось запланировать задачу: {e}")


def remove_reminder(slot_id):
    job_id = f"remind_{slot_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)