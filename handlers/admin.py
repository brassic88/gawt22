from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import ADMIN_ID
from database.db import db
from keyboards import inline
from utils.states import AdminStates

router = Router()

@router.message(Command("admin"))
async def admin_panel(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await state.clear()
    await message.answer("🔧 Админ-панель:", reply_markup=inline.admin_menu())

@router.callback_query(F.data == "admin_add")
async def adm_add(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Выберите дату:", reply_markup=inline.get_calendar_kb(prefix="admadd"))
    await state.set_state(AdminStates.adding_slot_date)

@router.callback_query(F.data.startswith("admadd_"), AdminStates.adding_slot_date)
async def adm_time(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(date=callback.data.split("_")[1])
    await callback.message.answer("Введите время (ЧЧ:ММ):")
    await state.set_state(AdminStates.adding_slot_time)

@router.message(AdminStates.adding_slot_time)
async def adm_fin(message: types.Message, state: FSMContext):
    if message.text.startswith('/'): return
    data = await state.get_data()
    db.add_slot(data['date'], message.text)
    await message.answer(f"Добавлено: {data['date']} {message.text}", reply_markup=inline.admin_menu())
    await state.clear()

@router.callback_query(F.data == "admin_close_day")
async def adm_close(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Закрыть день:", reply_markup=inline.get_calendar_kb(prefix="admclose"))
    await state.set_state(AdminStates.closing_day)

@router.callback_query(F.data.startswith("admclose_"), AdminStates.closing_day)
async def adm_close_fin(callback: types.CallbackQuery, state: FSMContext):
    date = callback.data.split("_")[1]
    db.close_day(date)
    await callback.message.edit_text(f"День {date} закрыт", reply_markup=inline.admin_menu())
    await state.clear()

@router.callback_query(F.data == "admin_view")
async def adm_view(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Просмотр даты:", reply_markup=inline.get_calendar_kb(prefix="admview"))
    await state.set_state(AdminStates.viewing_date)

@router.callback_query(F.data.startswith("admview_"), AdminStates.viewing_date)
async def adm_view_fin(callback: types.CallbackQuery, state: FSMContext):
    date = callback.data.split("_")[1]
    slots = db.get_all_slots_by_date(date)
    text = f"Записи на {date}:\n"
    for s in slots:
        text += f"{s[1]} - {'Занято ('+s[3]+')' if s[2] else 'Свободно'}\n"
    await callback.message.answer(text, reply_markup=inline.admin_menu())
    await state.clear()