from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database import register_for_raffle, add_chance

router = Router()

CURRENT_PARTNER = "PartnerX"
CHANNEL = "partner_channel"  # username канала партнера


@router.message(F.text == "Участвовать в розыгрыше")
async def enter_raffle_msg(msg: Message):
    from keyboards import raffle_kb
    await msg.answer(
        f"Чтобы попасть в розыгрыш призов от <b>{CURRENT_PARTNER}</b>, подпишись на аккаунт партнера",
        reply_markup=raffle_kb(CURRENT_PARTNER, CHANNEL),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "enter_raffle")
async def enter_raffle_cb(cb: CallbackQuery):
    from keyboards import raffle_kb
    await cb.message.edit_text(
        f"Чтобы попасть в розыгрыш призов от <b>{CURRENT_PARTNER}</b>, подпишись на аккаунт партнера",
        reply_markup=raffle_kb(CURRENT_PARTNER, CHANNEL),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("check_sub:"))
async def check_sub(cb: CallbackQuery):
    partner = cb.data.split(":")[1]
    is_subscribed = True  # заменить на реальную проверку

    if is_subscribed:
        registered = register_for_raffle(cb.from_user.id, partner)
        if registered:
            chances = add_chance(cb.from_user.id)
            await cb.message.edit_text(
                f"Ты в лайнапе!\n\n"
                f"Заявка на розыгрыш призов от <b>{partner}</b> зарегистрирована.\n"
                f"Накоплено шансов: <b>{chances}/10</b>\n\n"
                f"Возвращайся завтра — на сцену выйдет новый партнер",
                parse_mode="HTML"
            )
        else:
            await cb.message.edit_text(
                "Ты уже участвуешь в сегодняшнем розыгрыше\n"
                "Результаты сообщим после подведения итогов."
            )
    else:
        from keyboards import check_again_kb
        await cb.message.edit_text(
            f"Пока не вижу подписку\n\n"
            f"Подпишись на аккаунт <b>{partner}</b>, вернись в бот и попробуй еще раз.",
            reply_markup=check_again_kb(partner, CHANNEL),
            parse_mode="HTML"
        )