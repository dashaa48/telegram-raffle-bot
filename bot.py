import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from config import Config
from database import init_db
from handlers import start, promo, raffle, chances, admin, winner


async def main():
    init_db()
    bot = Bot(token=Config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    dp.include_routers(
        start.router,
        promo.router,
        raffle.router,
        chances.router,
        admin.router,
        winner.router,
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())