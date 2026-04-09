"""
ПРОЄКТ: AI PC Power & Tech Expert Bot
РОЗРОБНИК: Дмитро Васильчик (Група ІПЗ-111, Варіант 3)
ОПИС: Асинхронний Telegram-бот з інтеграцією Google Gemini 2.5 Flash 
для аналізу заліза, підбору техніки та оцінки її ринкової вартості.
"""

import asyncio
import logging
import os
from datetime import datetime
from aiohttp import web  
from google import genai
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from aiogram.enums import ChatAction


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TechExpertBot")

# ВПИШИ СВОЇ ТОКЕНИ ТУТ
TG_TOKEN = "ТВІЙ_ТОКЕН_ТЕЛЕГРАМ"
AI_TOKEN = "ТВІЙ_ТОКЕН_ШІ"

ai_client = genai.Client(api_key=AI_TOKEN)
dp = Dispatcher()
start_time = datetime.now()



main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💻 ПК"), KeyboardButton(text="📱 Телефон"), KeyboardButton(text="🎮 Консоль")],
        [KeyboardButton(text="🎯 Підібрати техніку"), KeyboardButton(text="💰 Оцінити техніку")],
        [KeyboardButton(text="ℹ️ Про розробника"), KeyboardButton(text="📊 Статус")]
    ],
    resize_keyboard=True
)

inline_links = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Маркетплейс Hotline", url="https://hotline.ua/")]
    ]
)


async def handle(request):
    return web.Response(text="Bot is running! Technical Expert system active.")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Веб-сервер запущено на порту {port}")


@dp.message(Command("start"))
async def cmd_start(msg):
    await msg.answer(
        f"👋 Вітаю, {msg.from_user.first_name}!\nЯ твій AI-експерт у світі техніки. Оберіть категорію:", 
        reply_markup=main_menu
    )

@dp.message(F.text == "📊 Статус")
async def cmd_status(msg):
    uptime = str(datetime.now() - start_time).split('.')[0]
    status_text = f"⚙️ **Статус:** Активний\n🧠 **AI:** Gemini 2.5 Flash\n⏱ **Uptime:** {uptime}"
    await msg.answer(status_text, parse_mode="Markdown")

@dp.message(F.text == "ℹ️ Про розробника")
async def cmd_about(msg):
    about_text = "👤 **Розробник:** Дмитро Васильчик\n🏫 **Група:** ІПЗ-111\n🔢 **Варіант:** 3"
    await msg.answer(about_text, parse_mode="Markdown")

@dp.message(F.text.in_({"💻 ПК", "📱 Телефон", "🎮 Консоль", "🎯 Підібрати техніку", "💰 Оцінити техніку"}))
async def handle_hints(msg):
    hints = {
        "💻 ПК": "Напиши: **ПК [Процесор, Відеокарта, ОЗП]**\nПриклад: ПК i5-12400, RTX 4060, 16GB",
        "📱 Телефон": "Напиши: **Телефон [Модель]**\nПриклад: Телефон Samsung S24",
        "🎮 Консоль": "Напиши: **Консоль [Назва]**\nПриклад: Консоль PS5 Slim",
        "🎯 Підібрати техніку": "Напиши: **Підбери [задачі] [бюджет]**\nПриклад: Підбери телефон для ігор до 20000 грн",
        "💰 Оцінити техніку": "Напиши: **Оціни [модель/залізо]**\nПриклад: Оціни ПК Ryzen 5 3600, GTX 1660"
    }
    await msg.answer(hints[msg.text], parse_mode="Markdown")



@dp.message(F.text.lower().startswith("пк "))
async def process_pc(msg):
    await msg.bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.TYPING)
    status = await msg.answer("🔍 Аналізую залізо на 18 топ-ігор...")
    prompt = f"""
    Ти експерт. Оціни ПК: {msg.text[3:]}. Перевір 18 ігор (Dota2, Cyberpunk, GTA V тощо).
    Використовуй ✅/⚠️/❌. Наприкінці порадь ОДНУ деталь для апгрейду з посиланням:
    https://hotline.ua/sr/?q=[назва_деталі_через_плюс]
    """
    try:
        res = ai_client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
        await status.edit_text(res.text[:4000], disable_web_page_preview=True)
    except: await status.edit_text("❌ Помилка AI API.")

@dp.message(F.text.lower().startswith("підбери "))
async def process_pick(msg):
    await msg.bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.TYPING)
    status = await msg.answer("🎯 Шукаю найкращі варіанти під твій бюджет...")
    prompt = f"""
    Ти IT-консультант. Запит: {msg.text[8:]}. 
    1. Тільки реально існуючі моделі 2024-2026 років. 
    2. Суворо дотримуйся бюджету. 
    3. Посилання Hotline ТІЛЬКИ на коротку назву моделі.
    """
    try:
        res = ai_client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
        await status.edit_text(res.text[:4000], disable_web_page_preview=True)
    except: await status.edit_text("❌ Помилка підбору.")

@dp.message(F.text.lower().startswith("оціни "))
async def process_val(msg):
    await msg.bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.TYPING)
    status = await msg.answer("⚖️ Вираховую ринкову вартість...")
    prompt = f"Ти оцінювач Б/В техніки. Оціни: {msg.text[6:]}. Назви ціну в грн та $ на вторинному ринку 2026 року."
    try:
        res = ai_client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
        await status.edit_text(res.text[:4000])
    except: await status.edit_text("❌ Помилка оцінки.")

# Обробники для телефонів та консолей
@dp.message(F.text.lower().startswith(("телефон ", "консоль ")))
async def process_simple_ai(msg):
    await msg.bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.TYPING)
    prompt = f"Ти експерт. Проаналізуй цей гаджет коротко (актуальність, FPS в іграх): {msg.text}"
    try:
        res = ai_client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
        await msg.answer(res.text)
    except: await msg.answer("❌ Помилка аналізу.")


async def main():

    asyncio.create_task(start_web_server())
    
    bot = Bot(token=TG_TOKEN)
    logger.info("Бот готовий до роботи!")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
