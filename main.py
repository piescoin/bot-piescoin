# Repository: https://github.com/piescoin/bot-piescoin.git

import logging
import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.dispatcher.router import Router
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN", "7826649604:AAF7T4pSAAaf99ThPlfCDWSkkBPvXXBImhQ")

# Initialize bot and router
bot = Bot(token=TOKEN)
router = Router()

# Example user data structure
users = {}

# Base constants
MAX_ENERGY = 5000
DOG_IMAGES = {
    1: "images/dog_level_1.jpg",
    2: "images/dog_level_2.jpg",
    3: "images/dog_level_3.jpg",
}
ENERGY_ICON = "images/menu_icon.png"

# Function to generate the main game screen
def get_main_screen(user_data):
    caption = (
        f"<b>🐕 Ваш Пес</b>
"
        f"<b>🔋 Енергія:</b> {user_data['energy']} / {MAX_ENERGY}

"
        "Натискайте на пса, щоб зібрати монети!"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Меню", callback_data="open_menu")]
    ])

    return caption, keyboard

@router.message(Command("start"))
async def send_welcome(message: Message):
    user_id = message.from_user.id

    # Initialize user data if not exists
    if user_id not in users:
        users[user_id] = {
            "coins": 0,
            "energy": MAX_ENERGY,
            "level": 1,
        }

    # Show initial screen with the dog image
    user_data = users[user_id]
    dog_image = DOG_IMAGES.get(user_data["level"], DOG_IMAGES[1])
    caption, keyboard = get_main_screen(user_data)

    await message.answer_photo(
        photo=open(dog_image, "rb"),
        caption=caption,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(lambda c: c.data == "open_menu")
async def open_menu(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_data = users[user_id]

    caption = (
        f"<b>📋 Меню</b>

"
        "Оберіть дію:"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💪 Вдосконалення", callback_data="upgrade")],
        [InlineKeyboardButton(text="👥 Реферали", callback_data="referrals")],
        [InlineKeyboardButton(text="💎 Донат", callback_data="donate")],
        [InlineKeyboardButton(text="🔙 Назад до гри", callback_data="back_to_game")]
    ])

    await callback_query.message.edit_text(caption, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(lambda c: c.data == "back_to_game")
async def back_to_game(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_data = users[user_id]

    dog_image = DOG_IMAGES.get(user_data["level"], DOG_IMAGES[1])
    caption, keyboard = get_main_screen(user_data)

    await callback_query.message.edit_caption(
        caption=caption,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback_query.message.edit_media(
        media={"type": "photo", "media": open(dog_image, "rb")}
    )

async def main():
    dp = Dispatcher()
    dp.include_router(router)

    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
