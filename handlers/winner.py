from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from keyboards import claim_kb

router = Router()


class ClaimForm(StatesGroup):
    name = State()
    agree = State()


@router.callback_query(F.data == "claim_prize")
async def start_claim(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text("👤 Напиши своё имя и фамилию:")
    await state.set_state(ClaimForm.name)


@router.message(ClaimForm.name)
async def get_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await msg.answer(
        "Согласен на передачу данных партнеру/билетному оператору?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Согласен", callback_data="agree_yes"),
             InlineKeyboardButton(text="Нет", callback_data="agree_no")]
        ])
    )
    await state.set_state(ClaimForm.agree)


@router.callback_query(ClaimForm.agree, F.data == "agree_yes")
async def agree_yes(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    import sqlite3
    with sqlite3.connect("bot.db") as conn:
        conn.execute("UPDATE users SET contact_name=?, contact_agreed=1 WHERE user_id=?",
                     (data['name'], cb.from_user.id))
        conn.commit()
    await state.clear()
    await cb.message.edit_text("Спасибо! Данные приняты. С тобой свяжутся в ближайшее время.")


@router.callback_query(ClaimForm.agree, F.data == "agree_no")
async def agree_no(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("Без согласия передать приз, к сожалению, не получится.")