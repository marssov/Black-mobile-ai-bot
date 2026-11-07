import os
import logging
import requests
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "9292859091:AAEmSzadHzwvjbMkfuvUhSTgvKRTSE9UDAM"
ADMIN_ID = 6668312138
CHANNEL_ID = "@Black_Mobilez"
OPENROUTER_KEY = "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"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

SYSTEM_PROMPT = (
    "Ты — профессиональный и очень креативный пиар-менеджер мобильного игрового сервера BLACK MOBILE "
    "(проект в стиле SAMP/CRMP на Android). Твоя задача — превращать сырые мысли и идеи администратора "
    "в сочные, привлекательные, структурированные посты для Telegram-канала. "
    "Используй игровой сленг (вирты, донат, суета, лаунчер, сервер, тачки, обзвон, лидерка), "
    "красиво расставляй тематические эмодзи, делай абзацы и списки, выделяй важные слова жирным шрифтом."
)

def ask_ai(text_to_ai):
    try:
        response = requests.post(
            url="https://openrouter.ai",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct:free",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Вот сырой текст: {text_to_ai}"}
                ]
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Ошибка ИИ (Код {response.status_code})"
    except Exception as e:
        return f"Ошибка запроса: {str(e)}"

@dp.message(CommandStart(), F.from_user.id == ADMIN_ID)
async def start_cmd(message: types.Message):
    await message.answer("👋 Привет! Отправь мне сырую мысль для поста.")

@dp.message(F.text, F.from_user.id == ADMIN_ID)
async def handle_draft(message: types.Message):
    waiting_msg = await message.answer("⏳ Генерирую пост...")
    ai_generated_post = ask_ai(message.text)
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 В канал", callback_data="publish")
    builder.adjust(1)
    await waiting_msg.delete()
    await message.answer(f"{ai_generated_post}", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "publish")
async def publish_callback(callback: types.CallbackQuery):
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=callback.message.text)
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.answer("✅ Опубликовано!")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")

async def main():
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
