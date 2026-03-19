from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime, timedelta

scheduler = AsyncIOScheduler(jobstores={'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')})

async def send_reminder(bot, user_id, time_str):
    try:
        await bot.send_message(user_id, f"🔔 <b>Напоминание!</b>\nВы записаны на завтра в {time_str}. Ждем вас! ✨", parse_mode="HTML")
    except: pass

def schedule_reminder(bot, user_id, date_str, time_str, slot_id):
    try:
        run_date = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M") - timedelta(hours=24)
        if run_date > datetime.now():
            scheduler.add_job(send_reminder, 'date', run_date=run_date, args=[bot, user_id, time_str], id=f"remind_{slot_id}", replace_existing=True)
    except: pass

def remove_reminder(slot_id):
    if scheduler.get_job(f"remind_{slot_id}"):
        scheduler.remove_job(f"remind_{slot_id}")