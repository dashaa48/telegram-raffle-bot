from aiogram import Router, F
from aiogram.types import Message
from database import issue_promo, promo_left

router = Router()

CURRENT_PARTNER = "PartnerX"  # подставляется из БД/админки в реальности


@router.message(F.text == "Получить промокод")
async def get_promo(msg: Message):
    partner = CURRENT_PARTNER
    result = issue_promo(msg.from_user.id, partner)

    if result[0] == 'ok':
        await msg.answer(
            f"Твой фестивальный бонус от <b>{partner}</b> готов!\n\n"
            f"Промокод: <code>{result[1]}</code>\n\n"
            f"Используй его до конца акции на сайте партнера.\n"
            f"Теперь можешь принять участие в розыгрыше призов дня",
            parse_mode="HTML"
        )
    elif result[0] == 'already':
        await msg.answer(
            f"Твой промокод от {partner} на сегодня:\n<code>{result[1]}</code>",
            parse_mode="HTML"
        )
    else:
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        await msg.answer(
            f"Промокоды от {partner} уже закончились — их разобрали быстрее всех!\n\n"
            "Но ты всё ещё можешь подписаться на партнера и принять участие в розыгрыше призов дня.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Участвовать в розыгрыше", callback_data="enter_raffle")]
            ])
        )