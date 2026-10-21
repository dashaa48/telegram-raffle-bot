from aiogram import Router, F
from aiogram.types import Message
from database import get_chances, get_user_partners

router = Router()


@router.message(F.text == "Мои шансы")
async def my_chances(msg: Message):
    chances = get_chances(msg.from_user.id)
    partners = get_user_partners(msg.from_user.id)
    partners_str = ", ".join(partners) if partners else "пока нет"
    await msg.answer(
        f"<b>Твой фестивальный пропуск</b>\n\n"
        f"Накоплено шансов: <b>{chances} / 10</b>\n"
        f"Партнеры: {partners_str}\n\n"
        f"Чем больше дней розыгрыша ты посетишь, тем выше вероятность выиграть главный приз",
        parse_mode="HTML"
    )