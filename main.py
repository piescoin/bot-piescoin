import logging
import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.dispatcher.router import Router
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN")

# Initialize bot and router
bot = Bot(token=TOKEN)
router = Router()

# Example user data structure
users = {}

# Базова папка для GIF-файлів та зображень
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
DOG_ANIMATION_PATH = os.path.join(BASE_DIR, "images", "dog_level_1_animated_slow.gif")

# Часовий проміжок для енергії та кліків
DOUBLE_CLICK_WINDOW = 0.5  # 500 мілісекунд
ENERGY_RECOVERY_RATE = 10  # Відновлення енергії кожні 10 секунд
MAX_ENERGY = 5000

# Функція для створення основного інтерфейсу гри
def get_main_screen(user_data):
    caption = (
        f"<b>🐕 Ваш Пес (Рівень {user_data['level']})</b>

"
        f"<b>🔹 Рівень:</b> {user_data['level']}
"
        f"<b>🔹 Енергія:</b> {user_data['energy']} / {MAX_ENERGY}
"
        f"<b>🔹 Монети:</b> {user_data['coins']}"
    )

    # Клавіатура з кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💏 Натиснути на собаку!", callback_data="touch_dog")],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="open_menu")],
    ])

    return caption, keyboard

# Асинхронна функція для відновлення енергії
async def energy_recovery():
    while True:
        await asyncio.sleep(10)
        for user_id in users:
            users[user_id]["energy"] = min(MAX_ENERGY, users[user_id]["energy"] + ENERGY_RECOVERY_RATE)

@router.message(Command("start"))
async def send_welcome(message: Message):
    user_id = message.from_user.id

    # Ініціалізація даних користувача
    if user_id not in users:
        users[user_id] = {
            "coins": 0,
            "energy": MAX_ENERGY,
            "level": 1,
            "last_click_time": 0
        }

    # Привітальне повідомлення
    caption, keyboard = get_main_screen(users[user_id])
    await message.answer_animation(
        animation=InputFile(DOG_ANIMATION_PATH),
        caption=caption,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(lambda c: c.data == "touch_dog")
async def touch_dog(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_data = users[user_id]
    current_time = time.time()

    if user_data["energy"] <= 0:
        await callback_query.answer("⚡ У вас закінчилася енергія!", show_alert=True)
        return

    # Логіка кліків і монет
    coins_to_add = 20 if current_time - user_data["last_click_time"] <= DOUBLE_CLICK_WINDOW else 10
    user_data["coins"] += coins_to_add
    user_data["energy"] -= 10
    user_data["last_click_time"] = current_time

    # Перевірка на підвищення рівня
    if user_data["coins"] >= user_data["level"] * 100:
        user_data["level"] += 1
        await callback_query.answer(f" Вітаємо! Ви досягли рівня {user_data['level']}!", show_alert=True)

    caption, keyboard = get_main_screen(user_data)
    await callback_query.message.edit_caption(
        caption=caption,
        reply_markup=keyboard
    )

@router.callback_query(lambda c: c.data == "open_menu")
async def open_menu(callback_query: CallbackQuery):
    # Меню з інформацією або іншими функціями
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Повернутися до гри", callback_data="back_to_game")]
    ])
    await callback_query.message.edit_text("Меню

Оберіть опцію:", reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "back_to_game")
async def back_to_game(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_data = users[user_id]

    caption, keyboard = get_main_screen(user_data)
    await callback_query.message.edit_caption(
        caption=caption,
        reply_markup=keyboard
    )

async def main():
    dp = Dispatcher()
    dp.include_router(router)

    # Запуск відновлення енергії
    asyncio.create_task(energy_recovery())

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
