"""
ПРОЄКТ: Розумний асистент "TechExpert AI"
КУРСОВА РОБОТА СТУДЕНТА ГРУПИ ІПЗ-111
РОЗРОБНИК: Дмитро Васильчук (Варіант №3)
ТЕХНОЛОГІЇ: Python 3.10+, aiogram 3.x, Google Gemini Pro API, aiohttp
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Final

try:
    from aiohttp import web
    from google import genai
    from aiogram import Bot, Dispatcher, F, types
    from aiogram.filters import Command
    from aiogram.types import (
        ReplyKeyboardMarkup, 
        KeyboardButton, 
        InlineKeyboardMarkup, 
        InlineKeyboardButton
    )
    from aiogram.enums import ChatAction
except ImportError as e:
    print(f"Помилка: Відсутні необхідні бібліотеки! {e}")
    sys.exit(1)


class BotConfig:
    """Клас для зберігання конфігураційних даних та констант"""
    
    TELEGRAM_TOKEN: Final[str] = "8358189004:AAGXHLxR-LIVK9IvB3tIiehQV6dJirms-vs"
    
    GEMINI_API_KEY: Final[str] = os.getenv("AI_TOKEN", "AIzaSyD6DrmbZUbHBVDAWc4qzJk82W97_OxybFQ") 
    
    SERVER_PORT: Final[int] = int(os.environ.get("PORT", 10000))
    SERVER_HOST: Final[str] = "0.0.0.0"


    LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    DEVELOPER_NAME: Final[str] = "Дмитро Васильчик"
    GROUP_CODE: Final[str] = "ІПЗ-111"
    VARIANT_NUM: Final[int] = 3

logging.basicConfig(level=logging.INFO, format=BotConfig.LOG_FORMAT)
logger = logging.getLogger("TechExpertBot")

ai_client = genai.Client(api_key=BotConfig.GEMINI_API_KEY)
dp = Dispatcher()
start_timestamp = datetime.now()


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Створення головного навігаційного меню"""
    buttons = [
        [KeyboardButton(text="💻 ПК"), KeyboardButton(text="📱 Телефон"), KeyboardButton(text="🎮 Консоль")],
        [KeyboardButton(text="🎯 Підібрати техніку"), KeyboardButton(text="💰 Оцінити техніку")],
        [KeyboardButton(text="ℹ️ Про розробника"), KeyboardButton(text="📊 Статус системи")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_inline_support() -> InlineKeyboardMarkup:
    """Створення інлайн-кнопок для підтримки та посилань"""
    inline_kb = [
        [InlineKeyboardButton(text="🔗 Порівняти на Hotline", url="https://hotline.ua/")],
        [InlineKeyboardButton(text="💬 Написати розробнику", url="tg://user?id=YOUR_ID")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)



async def health_check_handler(request):
    """Обробник запитів від сервісу Render для підтримки активності"""
    logger.info("Health check request received")
    uptime = str(datetime.now() - start_timestamp).split('.')[0]
    return web.Response(text=f"TechExpertBot is Live! System Uptime: {uptime}")

async def run_internal_server():
    """Запуск легкого веб-сервера паралельно з ботом"""
    app = web.Application()
    app.router.add_get("/", health_check_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, BotConfig.SERVER_HOST, BotConfig.SERVER_PORT)
    await site.start()
    logger.info(f"Внутрішній сервер моніторингу запущено на порту {BotConfig.SERVER_PORT}")

async def call_gemini_api(prompt_text: str) -> str:
    
    model_name = 'gemini-2.0-flash'
    
    system_context = "Ти професійний тех-експерт. Відповідай українською мовою."
    full_prompt = f"{system_context}\n\nКористувач запитує: {prompt_text}"

    try:
        
        await asyncio.sleep(1.5) 
        
        response = ai_client.models.generate_content(
            model=model_name,
            contents=full_prompt
        )
        if response and response.text:
            return response.text
    except Exception as e:
        error_str = str(e)
        if "429" in error_str:
            return "⚠️ **Сервер ШІ тимчасово перевантажений.** Спробуйте через 30-60 секунд."
        logger.error(f"Помилка ШІ: {e}")
            
    return "❌ На жаль, зараз не вдалося зв'язатися з ШІ. Спробуйте пізніше."

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    welcome_text = (
        f"🌟 **Вітаю, {message.from_user.full_name}!**\n\n"
        "Я — інтелектуальна система аналізу комп'ютерної техніки.\n"
        "Використовую Gemini AI для надання професійних порад.\n\n"
        "Оберіть категорію нижче для початку роботи:"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@dp.message(F.text == "📊 Статус системи")
async def status_handler(message: types.Message):
    current_uptime = str(datetime.now() - start_timestamp).split('.')[0]
    status_msg = (
        "📈 **ТЕХНІЧНИЙ МОНІТОР**\n"
        "--------------------------\n"
        f"✅ Статус: Працює коректно\n"
        f"🤖 Модель ШІ: Gemini Hybrid (2.0/1.5)\n"
        f"⏱ Час безперервної роботи: {current_uptime}\n"
        f"📅 Поточний час: {datetime.now().strftime('%H:%M:%S')}\n"
        "--------------------------"
    )
    await message.answer(status_msg, parse_mode="Markdown")

@dp.message(F.text == "ℹ️ Про розробника")
async def developer_info_handler(message: types.Message):
    info_card = (
        "🎓 **КАРТКА КУРСОВОГО ПРОЄКТУ**\n"
        "--------------------------\n"
        f"👤 Розробник: {BotConfig.DEVELOPER_NAME}\n"
        f"🏫 Навчальна група: {BotConfig.GROUP_CODE}\n"
        f"🔢 Варіант завдання: {BotConfig.VARIANT_NUM}\n"
        "📍 Місце розробки: Одеса, Україна\n"
        "--------------------------"
    )
    await message.answer(info_card, parse_mode="Markdown")

@dp.message(F.text.in_({"💻 ПК", "📱 Телефон", "🎮 Консоль", "🎯 Підібрати техніку", "💰 Оцінити техніку"}))
async def help_prompts_handler(message: types.Message):
    guide = {
        "💻 ПК": "📝 **ФОРМАТ:** ПК [Процесор, Відеокарта, ОЗП]\n*Приклад: ПК Core i7-13700, RTX 4070, 32GB*",
        "📱 Телефон": "📝 **ФОРМАТ:** Телефон [Модель]\n*Приклад: Телефон iPhone 15 Pro*",
        "🎮 Консоль": "📝 **ФОРМАТ:** Консоль [Назва]\n*Приклад: Консоль Steam Deck OLED*",
        "🎯 Підібрати техніку": "📝 **ФОРМАТ:** Підбери [що саме] [бюджет]\n*Приклад: Підбери ноутбук для програмування до 45000 грн*",
        "💰 Оцінити техніку": "📝 **ФОРМАТ:** Оціни [ваше залізо]\n*Приклад: Оціни відеокарту GTX 1060 6GB*"
    }
    await message.answer(guide[message.text], parse_mode="Markdown")

@dp.message(F.text.lower().startswith("пк "))
async def analyze_pc_handler(message: types.Message):
    user_input = message.text[3:].strip()
    if not user_input:
        return await message.answer("⚠️ Будь ласка, вкажіть параметри ПК!")
        
    loading = await message.answer("🔄 **Запуск глибокого аналізу архітектури...**")
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    
    prompt = f"Проаналізуй конфігурацію ПК: {user_input}. Оціни FPS у 5 сучасних іграх та порадь одну деталь для апгрейду."
    ai_response = await call_gemini_api(prompt)
    
    await loading.delete()
    await message.answer(f"🖥 **РЕЗУЛЬТАТИ ТЕСТУВАННЯ:**\n\n{ai_response}", 
                         reply_markup=get_inline_support(), 
                         disable_web_page_preview=True)

@dp.message(F.text.lower().startswith("підбери "))
async def picking_handler(message: types.Message):
    user_query = message.text[8:].strip()
    if len(user_query) < 5:
        return await message.answer("⚠️ Опишіть ваш запит детальніше (наприклад: 'ноутбук до 30к').")

    loading = await message.answer("🎯 **Шукаю найкращі пропозиції на ринку...**")
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    
    prompt = f"Підбери техніку за запитом: {user_query}. Вкажи 3 реальні моделі з цінами та короткими характеристиками."
    result = await call_gemini_api(prompt)
    
    await loading.delete()
    await message.answer(f"✅ **НАЙКРАЩІ ВАРІАНТИ:**\n\n{result}", disable_web_page_preview=True)

@dp.message(F.text.lower().startswith("оціни "))
async def valuation_handler(message: types.Message):
    item = message.text[6:].strip()
    if not item:
        return await message.answer("⚠️ Вкажіть, що саме треба оцінити!")

    loading = await message.answer("⚖️ **Вивчаю динаміку цін на вторинному ринку...**")
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    
    prompt = f"Оціни Б/В вартість: {item}. Назви реальну ціну продажу в гривнях та доларах станом на 2026 рік."
    valuation = await call_gemini_api(prompt)
    
    await loading.delete()
    await message.answer(f"💰 **РИНКОВА ОЦІНКА:**\n\n{valuation}")

@dp.message(F.text)
async def generic_ai_handler(message: types.Message):
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    response = await call_gemini_api(message.text)
    await message.answer(response)


async def main():
    """Головна функція запуску бота та супутніх сервісів"""
    
    asyncio.create_task(run_internal_server())
    

    bot = Bot(token=BotConfig.TELEGRAM_TOKEN)
    
    logger.info("==========================================")
    logger.info("Бот 'TechExpert' готовий до обробки повідомлень")
    logger.info(f"Розробник: {BotConfig.DEVELOPER_NAME}")
    logger.info("==========================================")
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as run_error:
        logger.critical(f"Критична помилка виконання: {run_error}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Бот зупинений адміністратором.")
