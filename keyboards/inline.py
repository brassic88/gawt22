import calendar
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💅 Записаться", callback_data="start_booking")],
        [InlineKeyboardButton(text="❌ Моя запись / Отмена", callback_data="my_booking")],
        [InlineKeyboardButton(text="💰 Прайсы", callback_data="show_prices"),
         InlineKeyboardButton(text="📸 Портфолио", callback_data="show_portfolio")]
    ])


def get_calendar_kb(month: int = None, year: int = None, prefix: str = "date"):
    now = datetime.now()
    month = month or now.month
    year = year or now.year

    kb = [[InlineKeyboardButton(text=f"{calendar.month_name[month]} {year}", callback_data="ignore")]]
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    kb.append([InlineKeyboardButton(text=d, callback_data="ignore") for d in days])

    month_calendar = calendar.monthcalendar(year, month)
    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                row.append(InlineKeyboardButton(text=str(day), callback_data=f"{prefix}_{date_str}"))
        kb.append(row)

    kb.append([InlineKeyboardButton(text="⬅️ В меню", callback_data="to_main")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_times_kb(times, back_data="start_booking"):
    buttons = []
    row = []
    for t in times:
        row.append(InlineKeyboardButton(text=t[1], callback_data=f"slot_{t[0]}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=back_data)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def portfolio_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Смотреть портфолио", url="https://ru.pinterest.com/crystalwithluv/_created/")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="to_main")]
    ])


def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить время", callback_data="admin_add")],
        [InlineKeyboardButton(text="📅 Просмотр записей", callback_data="admin_view")],
        [InlineKeyboardButton(text="🚫 Закрыть весь день", callback_data="admin_close_day")],
        [InlineKeyboardButton(text="⬅️ Выход", callback_data="to_main")]
    ])