from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton

from database.db import db
from keyboards import inline
from utils.states import BookingStates
from utils.scheduler import schedule_reminder, remove_reminder
from config import ADMIN_ID, REPORT_CHANNEL_ID, CHANNEL_LINK
from handlers.common import check_subscription

router = Router()


@router.callback_query(F.data == "start_booking")
async def start_booking(callback: types.CallbackQuery, state: FSMContext, bot):
    # 1. Проверка подписки
    if not await check_subscription(bot, callback.from_user.id):
        await callback.message.edit_text(
            "Для записи необходимо подписаться на наш канал!",
            reply_markup=inline.sub_menu(CHANNEL_LINK)
        )
        return

    # 2. Проверка, нет ли уже активной записи
    if db.check_user_booking(callback.from_user.id):
        await callback.answer("У вас уже есть активная запись!", show_alert=True)
        return

    dates = db.get_available_dates()
    if not dates:
        await callback.message.edit_text("К сожалению, свободных дат нет.", reply_markup=inline.main_menu())
        return

    await callback.message.edit_text("Выберите дату:", reply_markup=inline.get_dates_kb(dates))
    await state.set_state(BookingStates.choosing_date)


@router.callback_query(F.data.startswith("date_"), BookingStates.choosing_date)
async def choose_time(callback: types.CallbackQuery, state: FSMContext):
    date = callback.data.split("_")[1]
    await state.update_data(chosen_date=date)
    times = db.get_available_times(date)
    await callback.message.edit_text(f"Выбрана дата: {date}\nВыберите время:", reply_markup=inline.get_times_kb(times))
    await state.set_state(BookingStates.choosing_time)


@router.callback_query(F.data.startswith("slot_"), BookingStates.choosing_time)
async def input_name(callback: types.CallbackQuery, state: FSMContext):
    slot_id = callback.data.split("_")[1]
    await state.update_data(slot_id=slot_id)
    await callback.message.edit_text("Введите ваше имя:")
    await state.set_state(BookingStates.input_name)


@router.message(BookingStates.input_name)
async def input_phone(message: types.Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await message.answer("Введите ваш номер телефона:")
    await state.set_state(BookingStates.input_phone)


@router.message(BookingStates.input_phone)
async def confirm_booking(message: types.Message, state: FSMContext, bot):
    data = await state.get_data()
    db.book_slot(data['slot_id'], message.from_user.id, data['user_name'], message.text)

    slot = db.get_slot_by_id(data['slot_id'])  # [id, date, time, ...]

    # Планируем напоминание
    schedule_reminder(bot, message.from_user.id, slot[1], slot[2], slot[0])

    report = f"✅ <b>Новая запись!</b>\n👤 Имя: {data['user_name']}\n📞 Тел: {message.text}\n📅 Дата: {slot[1]}\n⏰ Время: {slot[2]}"

    # Уведомление админу и в канал
    await bot.send_message(ADMIN_ID, report, parse_mode="HTML")
    await bot.send_message(REPORT_CHANNEL_ID, report, parse_mode="HTML")

    await message.answer(f"Вы успешно записаны на {slot[1]} в {slot[2]}!", reply_markup=inline.main_menu())
    await state.clear()


@router.callback_query(F.data == "my_booking")
async def show_my_booking(callback: types.CallbackQuery):
    booking = db.get_user_booking(callback.from_user.id)
    if not booking:
        await callback.answer("У вас нет активных записей.", show_alert=True)
        return

    text = f"Ваша запись:\n📅 Дата: {booking[1]}\n⏰ Время: {booking[2]}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить запись", callback_data=f"cancel_{booking[0]}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="to_main")]
    ])
    await callback.message.edit_text(text, reply_markup=kb)


@router.callback_query(F.data.startswith("cancel_"))
async def cancel_booking_handler(callback: types.CallbackQuery):
    slot_id = callback.data.split("_")[1]
    db.cancel_booking(slot_id)
    remove_reminder(slot_id)
    await callback.message.edit_text("Запись успешно отменена.", reply_markup=inline.main_menu())