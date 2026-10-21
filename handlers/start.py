from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from database import register_user
from keyboards import main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(msg: Message):
    register_user(msg.from_user.id, msg.from_user.username, msg.from_user.first_name)
    await msg.answer(
        "<b>Добро пожаловать в Бот розыгрышей!</b>\n\n"
        "Здесь тебя ждут промокоды от партнеров фестиваля и ежедневные розыгрыши призов.",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )


@router.message(F.text == "Как участвовать")
async def how_to(msg: Message):
    await msg.answer(
        "<b>Как участвовать:</b>\n\n"
        "1. Получи промокод от партнера.\n"
        "2. Подпишись на канал партнера.\n"
        "3. Нажми «Участвовать в розыгрыше».\n"
        "4. Каждый активный день = +1 шанс в финальном розыгрыше (макс. 10).\n"
        "5. Результаты — в личных сообщениях."
    )


@router.message(F.text == "Правила акции")
async def rules(msg: Message):
    await msg.answer(
        "<b>Правила:</b>\n\n"
        "• 1 промокод в день от каждого партнера.\n"
        "• 1 заявка в ежедневном розыгрыше от партнера.\n"
        "• Максимум 10 шансов в финальном розыгрыше.\n"
        "• Победители определяются случайным образом.\n"
        "• Приз нужно подтвердить в течение 24 часов."
    )