from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import ADMIN_ID
from database.db import db
from keyboards import inline
from utils.states import AdminStates

router = Router()

@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Панель администратора:", reply_markup=inline.admin_menu())

@router.callback_query(F.data == "admin_add")
async def admin_add_date(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите дату в формате ГГГГ-ММ-ДД (например 2026-03-20):")
    await state.set_state(AdminStates.adding_slot_date)

@router.message(AdminStates.adding_slot_date)
async def admin_add_time(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer("Введите время слота (например 14:00):")
    await state.set_state(AdminStates.adding_slot_time)

@router.message(AdminStates.adding_slot_time)
async def admin_finish_add(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db.add_slot(data['date'], message.text)
    await message.answer(f"Слот на {data['date']} в {message.text} успешно добавлен!", reply_markup=inline.admin_menu())
    await state.clear()

@router.callback_query(F.data == "admin_view")
async def admin_view_date(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("На какую дату показать расписание? (ГГГГ-ММ-ДД)")
    await state.set_state(AdminStates.closing_day) # Используем то же состояние для ввода даты

@router.message(AdminStates.closing_day)
async def view_schedule(message: types.Message, state: FSMContext):
    slots = db.get_all_slots_by_date(message.text)
    if not slots:
        await message.answer("На этот день записей нет.")
    else:
        text = f"Расписание на {message.text}:\n"
        for s in slots:
            status = f"✅ Занято ({s[3]})" if s[2] else "🆓 Свободно"
            text += f"{s[1]} - {status}\n"
        await message.answer(text)
    await state.clear()