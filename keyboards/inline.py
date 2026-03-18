from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    buttons = [
        [InlineKeyboardButton(text="💅 Записаться", callback_data="start_booking")],
        [InlineKeyboardButton(text="❌ Отменить запись", callback_data="my_booking")],
        [InlineKeyboardButton(text="💰 Прайсы", callback_data="show_prices")],
        [InlineKeyboardButton(text="📸 Портфолио", callback_data="show_portfolio")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def sub_menu(link):
    buttons = [
        [InlineKeyboardButton(text="Подписаться", url=link)],
        [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_sub")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def portfolio_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Смотреть портфолио", url="https://ru.pinterest.com/crystalwithluv/_created/")]
    ])

def admin_menu():
    buttons = [
        [InlineKeyboardButton(text="➕ Добавить слот", callback_data="admin_add")],
        [InlineKeyboardButton(text="📅 Посмотреть расписание", callback_data="admin_view")],
        [InlineKeyboardButton(text="🚫 Закрыть день", callback_data="admin_close_day")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_dates_kb(dates):
    buttons = [[InlineKeyboardButton(text=d, callback_data=f"date_{d}")] for d in dates]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_times_kb(times):
    buttons = [[InlineKeyboardButton(text=t[1], callback_data=f"slot_{t[0]}")] for t in times]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="start_booking")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)