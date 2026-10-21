from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from config import Config
from database import draw_daily_winners, draw_final_winners, get_stats, init_db

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in Config.ADMIN_IDS


@router.message(Command("stats"))
async def stats(msg: Message):
    if not is_admin(msg.from_user.id):
        return
    s = get_stats()
    await msg.answer(
        f"<b>Статистика</b>\n\n"
        f"Всего запустили бот: {s['started']}\n"
        f"Новых сегодня: {s['new_today']}\n"
        f"Запросов промокода: {s['promo_requests']}\n"
        f"Выдано промокодов: {s['promo_issued']}\n"
        f"Участников сегодня: {s['today_participants']}\n"
        f"Остатки по партнерам: {s['partners_left']}",
        parse_mode="HTML"
    )


@router.message(Command("draw_daily"))
async def draw_daily(msg: Message):
    if not is_admin(msg.from_user.id):
        return
    # /draw_daily PartnerX Приз 3
    args = msg.text.split(maxsplit=3)
    if len(args) < 4:
        return await msg.answer("Использование: /draw_daily <partner> <prize_name> <count>")
    _, partner, prize, count = args
    winners = draw_daily_winners(partner, prize, int(count))
    text = f"Победители розыгрыша {partner}:\n" + "\n".join(f"• {uid}" for uid in winners)
    await msg.answer(text or "Нет участников")


@router.message(Command("draw_final"))
async def draw_final(msg: Message):
    if not is_admin(msg.from_user.id):
        return
    winners = draw_final_winners()
    text = "Победители главного розыгрыша:\n" + "\n".join(f"• {uid}" for uid in winners)
    await msg.answer(text or "Нет участников")


@router.message(Command("add_promo"))
async def add_promo(msg: Message):
    if not is_admin(msg.from_user.id):
        return
    args = msg.text.split(maxsplit=2)
    if len(args) < 3:
        return await msg.answer("Использование: /add_promo <partner> <code>")
    import sqlite3
    with sqlite3.connect("bot.db") as conn:
        conn.execute("INSERT INTO promo_codes (partner, code) VALUES (?, ?)", (args[1], args[2]))
        conn.commit()
    await msg.answer(f"Промокод {args[2]} добавлен для {args[1]}")