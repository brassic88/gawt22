from aiogram import Router, F, types
from aiogram.filters import Command
from config import CHANNEL_ID, CHANNEL_LINK, ADMIN_ID
from keyboards import inline
from database.db import db

router = Router()

async def check_subscription(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status != "left"
    except:
        return False

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, <b>{message.from_user.full_name}</b>! ✨\nЯ бот для записи на маникюр. Выберите нужное действие:",
        reply_markup=inline.main_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "to_main") # Было callback_data
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text("Выберите действие:", reply_markup=inline.main_menu())

@router.callback_query(F.data == "show_prices")
async def show_prices(callback: types.CallbackQuery):
    text = "<b>💰 Наш прайс-лист:</b>\n\n" \
           "▫️ Френч — 1000₽\n" \
           "▫️ Квадрат — 500₽\n" \
           "▫️ Наращивание — от 2000₽"
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "show_portfolio")
async def show_portfolio(callback: types.CallbackQuery):
    await callback.message.answer("Мои работы в Pinterest:", reply_markup=inline.portfolio_kb())
    await callback.answer()

@router.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: types.CallbackQuery, bot):
    if await check_subscription(bot, callback.from_user.id):
        await callback.message.edit_text("✅ Подписка подтверждена! Теперь вы можете записаться.",
                                         reply_markup=inline.main_menu())
    else:
        await callback.answer("❌ Вы все еще не подписаны!", show_alert=True)