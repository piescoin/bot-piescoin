import logging
import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.filters import Command
from aiogram.dispatcher.router import Router

# Telegram bot token
TOKEN = "7826649604:AAF7T4pSAAaf99ThPlfCDWSkkBPvXXBImhQ"

# Initialize bot and router
bot = Bot(token=TOKEN, parse_mode="HTML")
router = Router()

# Example user data structure
users = {}

# Base constants
MAX_ENERGY = 5000
DOG_IMAGES = {
    1: "https://raw.githubusercontent.com/piescoin/bot-piescoin/main/images/dog_level_1.jpg",  # Рівні 1-30
    2: "https://raw.githubusercontent.com/piescoin/bot-piescoin/main/images/dog_level_2.jpg",  # Рівні 31-65
    3: "https://raw.githubusercontent.com/piescoin/bot-piescoin/main/images/dog_level_3.jpg",  # Рівні 66-100
}

# Function to generate the main game screen
def get_main_screen(user_data):
    caption = (
        f"<b>🐕 Ваш Пес</b>\n"
        f"<b>🔋 Енергія:</b> {user_data['energy']} / {MAX_ENERGY}\n\n"
        "Натискайте на пса, щоб зібрати монети!"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Меню", callback_data="open_menu")]
    ])

    return caption, keyboard

# Function to determine the correct image based on level
def get_dog_image(level):
    if 1 <= level <= 30:
        return DOG_IMAGES[1]
    elif 31 <= level <= 65:
        return DOG_IMAGES[2]
    else:
        return DOG_IMAGES[3]

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
    dog_image = get_dog_image(user_data["level"])
    caption, keyboard = get_main_screen(user_data)

    try:
        await message.answer_photo(photo=dog_image, caption=caption, reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Помилка при надсиланні фото: {str(e)}")
        await message.reply(f"⚠️ Сталася помилка: {str(e)}")

@router.callback_query(lambda c: c.data == "open_menu")
async def open_menu(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in users:
        await callback_query.answer("❌ Помилка: Користувач не знайдений.", show_alert=True)
        return

    caption = (
        f"<b>📋 Меню</b>\n\n"
        "Оберіть дію:"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💪 Вдосконалення", callback_data="upgrade")],
        [InlineKeyboardButton(text="👥 Реферали", callback_data="referrals")],
        [InlineKeyboardButton(text="💎 Донат", callback_data="donate")],
        [InlineKeyboardButton(text="🔙 Назад до гри", callback_data="back_to_game")]
    ])

    await callback_query.message.edit_text(caption, reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "back_to_game")
async def back_to_game(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in users:
        await callback_query.answer("❌ Помилка: Користувач не знайдено.", show_alert=True)
        return

    user_data = users[user_id]
    dog_image = get_dog_image(user_data["level"])
    caption, keyboard = get_main_screen(user_data)

    try:
        await callback_query.message.edit_media(media=InputMediaPhoto(dog_image))
        await callback_query.message.edit_caption(caption=caption, reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Помилка при оновленні фото: {str(e)}")
        await callback_query.message.reply(f"⚠️ Сталася помилка: {str(e)}")

async def main():
    dp = Dispatcher()
    dp.include_router(router)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.info("Бот запущений та готовий приймати команди.")

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.critical(f"Критична помилка запуску: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
