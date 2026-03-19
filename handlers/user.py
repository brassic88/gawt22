from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from database.db import db
from keyboards import inline
from utils.states import BookingStates
from utils.scheduler import schedule_reminder, remove_reminder
from config import ADMIN_ID, CHANNEL_LINK
from handlers.common import check_subscription

router = Router()


@router.callback_query(F.data == "start_booking")
async def start_booking(callback: types.CallbackQuery, state: FSMContext, bot):
    if not await check_subscription(bot, callback.from_user.id):
        await callback.message.edit_text("Для записи подпишитесь на канал!",
                                         reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                             [types.InlineKeyboardButton(text="Подписаться", url=CHANNEL_LINK)],
                                             [types.InlineKeyboardButton(text="✅ Проверить", callback_data="check_sub")]
                                         ]))
        return

    if db.check_user_booking(callback.from_user.id):
        await callback.answer("У вас уже есть запись!", show_alert=True)
        return

    await callback.message.edit_text("Выберите дату:", reply_markup=inline.get_calendar_kb())
    await state.set_state(BookingStates.choosing_date)


@router.callback_query(F.data.startswith("date_"), BookingStates.choosing_date)
async def choose_time(callback: types.CallbackQuery, state: FSMContext):
    date = callback.data.split("_")[1]
    times = db.get_available_times(date)
    if not times:
        await callback.answer("Нет свободных окон!", show_alert=True)
        return
    await state.update_data(chosen_date=date)
    await callback.message.edit_text(f"Дата: {date}. Время:", reply_markup=inline.get_times_kb(times))
    await state.set_state(BookingStates.choosing_time)


@router.callback_query(F.data.startswith("slot_"), BookingStates.choosing_time)
async def input_name(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(slot_id=callback.data.split("_")[1])
    await callback.message.edit_text("Введите ваше имя:")
    await state.set_state(BookingStates.input_name)


@router.message(BookingStates.input_name)
async def input_phone(message: types.Message, state: FSMContext):
    if message.text.startswith('/'): return
    await state.update_data(user_name=message.text)
    await message.answer("Введите номер телефона:")
    await state.set_state(BookingStates.input_phone)


@router.message(BookingStates.input_phone)
async def confirm_booking(message: types.Message, state: FSMContext, bot):
    if message.text.startswith('/'): return
    data = await state.get_data()
    db.book_slot(data['slot_id'], message.from_user.id, data['user_name'], message.text)
    slot = db.get_slot_by_id(data['slot_id'])

    schedule_reminder(bot, message.from_user.id, slot[1], slot[2], slot[0])
    await bot.send_message(ADMIN_ID, f"✅ Новая запись!\n{data['user_name']} ({message.text})\n{slot[1]} {slot[2]}")
    await message.answer("✅ Вы успешно записаны!", reply_markup=inline.main_menu())
    await state.clear()


@router.callback_query(F.data == "my_booking")
async def my_booking(callback: types.CallbackQuery):
    b = db.get_user_booking(callback.from_user.id)
    if not b:
        await callback.answer("Нет записей", show_alert=True)
        return
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_{b[0]}")],
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="to_main")]
    ])
    await callback.message.edit_text(f"Запись: {b[1]} в {b[2]}", reply_markup=kb)


@router.callback_query(F.data.startswith("cancel_"))
async def cancel_handler(callback: types.CallbackQuery):
    slot_id = callback.data.split("_")[1]
    db.cancel_booking(slot_id)
    remove_reminder(slot_id)
    await callback.message.edit_text("Запись отменена", reply_markup=inline.main_menu())