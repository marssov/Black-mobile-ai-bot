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

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

SYSTEM_PROMPT = (
    "Ты — профессиональный и очень креативный пиар-менеджер мобильного игрового сервера BLACK MOBILE "
    "(проект в стиле SAMP/CRMP на Android). Твоя задача — превращать сырые мысли и идеи администратора "
    "в сочные, привлекательные, структурированные посты для Telegram-канала. "
    "Используй игровой сленг (вирты, донат, суета, лаунчер, сервер, тачки, обзвон, лидерка), "
    "красиво расставляй тематические эмодзи, делай абзацы и списки, выделяй важные слова жирным шрифтом. "
    "Пост должен вызывать дикое желание зайти в игру прямо сейчас. "
    "Вот сырой текст от администратора: "
)

def ask_ai(text_to_ai):
    try:
        response = requests.post("https://a0.dev", json={
            "prompt": f"{SYSTEM_PROMPT}\n{text_to_ai}"
        }, timeout=30)
        
        if response.status_code == 200:
            return response.json().get("output", "Ошибка генерации текста.")
        return "Не удалось связаться с ИИ-сервером. Попробуйте еще раз."
    except Exception as e:
        return f"Ошибка при запросе к ИИ: {str(e)}"

@dp.message(CommandStart(), F.from_user.id == ADMIN_ID)
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 Привет, Создатель! Я твой личный ИИ-помощник для BLACK MOBILE.\n\n"
        "Отправь мне любую сырую мысль, новость или задумку для поста (например: 'завтра раздача в пять вечера на 100кк и скин мелстроя'), "
        "и я сделаю из неё готовый пушечный пост!"
    )

@dp.message(F.text, F.from_user.id == ADMIN_ID)
async def handle_draft(message: types.Message):
    waiting_msg = await message.answer("⏳ *ИИ генерирует сочный пост для BLACK MOBILE, подожди немного...*", parse_mode="Markdown")
    
    ai_generated_post = ask_ai(message.text)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Опубликовать в канал", callback_data="publish_post")
    builder.button(text="🔄 Перегенерировать", callback_data="regenerate_post")
    builder.adjust(1)
    
    await waiting_msg.delete()
    
    await message.answer(
        f"{ai_generated_post}\n\n"
        f"————————————————————\n"
        f"🤖 *Выше представлен готовый вариант поста. Что делаем?*",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data == "publish_post")
async def publish_callback(callback: types.CallbackQuery):
    text_to_publish = callback.message.text.split("\n\n————————————————————\n")
    
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=text_to_publish[0], parse_mode="Markdown")
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("✅ Пост успешно опубликован в твой Telegram-канал!")
        await callback.answer()
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка публикации. Проверь, добавлен ли бот в админы канала. Инфо: {e}")
        await callback.answer()

@dp.callback_query(F.data == "regenerate_post")
async def regenerate_callback(callback: types.CallbackQuery):
    await callback.message.answer("📝 Отправь мне мысль заново или измени описание, и я попробую еще раз!")
    await callback.message.delete()
    await callback.answer()

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
