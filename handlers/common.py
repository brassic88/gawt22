from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import CHANNEL_ID, CHANNEL_LINK
from keyboards import inline

router = Router()

async def check_subscription(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status != "left"
    except: return False

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(f"Привет, <b>{message.from_user.full_name}</b>! ✨", reply_markup=inline.main_menu(), parse_mode="HTML")

@router.callback_query(F.data == "to_main")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Выберите действие:", reply_markup=inline.main_menu())

@router.callback_query(F.data == "show_prices")
async def show_prices(callback: types.CallbackQuery):
    text = "<b>💰 Наш прайс-лист:</b>\n\n▫️ Френч — 1000₽\n▫️ Квадрат — 500₽"
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "show_portfolio")
async def show_portfolio(callback: types.CallbackQuery):
    await callback.message.edit_text("Мои работы:", reply_markup=inline.portfolio_kb())