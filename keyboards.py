from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Получить промокод")],
        [KeyboardButton(text="Участвовать в розыгрыше")],
        [KeyboardButton(text="Как участвовать")],
        [KeyboardButton(text="Мои шансы")],
        [KeyboardButton(text="Правила акции")],
    ], resize_keyboard=True)


def raffle_kb(partner, channel_username):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Подписаться на {partner}", url=f"https://t.me/{channel_username}")],
        [InlineKeyboardButton(text="Проверить подписку", callback_data=f"check_sub:{partner}")],
    ])


def check_again_kb(partner, channel_username):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подписаться", url=f"https://t.me/{channel_username}")],
        [InlineKeyboardButton(text="Проверить еще раз", callback_data=f"check_sub:{partner}")],
    ])


def claim_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Получить приз", callback_data="claim_prize")]
    ])