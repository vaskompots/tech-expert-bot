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


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TechExpertBot")

TG_TOKEN = "8358189004:AAGXHLxR-LIVK9IvB3tIiehQV6dJirms-vs"
AI_TOKEN = "AIzaSyBptOgsF6jpdVXTSCNVkUKKprlyAno-7cQ"

ai_client = genai.Client(api_key=AI_TOKEN)
dp = Dispatcher()
start_time = datetime.now()



main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💻 ПК"), 
            KeyboardButton(text="📱 Телефон"), 
            KeyboardButton(text="🎮 Консоль")
        ],
        [
            KeyboardButton(text="🎯 Підібрати техніку"),
            KeyboardButton(text="💰 Оцінити техніку")
        ],
        [KeyboardButton(text="ℹ️ Про розробника"), KeyboardButton(text="📊 Статус")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Оберіть режим аналізу..."
)

inline_links = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Маркетплейс Hotline", url="https://hotline.ua/")],
        [InlineKeyboardButton(text="📂 GitHub Репозиторій", url="https://github.com/")]
    ]
)


@dp.message(Command("start"))
async def cmd_start(msg):
    welcome_text = (
        f"👋 Вітаю, {msg.from_user.first_name}!\n\n"
        "Я — твій інтелектуальний AI-асистент у світі заліза.\n"
        "Я можу перевірити твій ПК на ігри, підібрати новий гаджет "
        "або навіть оцінити твою стару техніку для продажу!\n\n"
        "🚀 Обирай категорію нижче, щоб почати:"
    )
    await msg.answer(welcome_text, reply_markup=main_menu)
    logger.info(f"User {msg.from_user.id} started the bot session.")

@dp.message(F.text == "📊 Статус")
async def cmd_status(msg):
    current_uptime = datetime.now() - start_time
    status_text = (
        "⚙️ **Технічний статус системи:**\n\n"
        f"✅ Зв'язок з Telegram: OK\n"
        f"🧠 Модель ШІ: Gemini 2.5 Flash\n"
        f"⏱ Час роботи: {str(current_uptime).split('.')[0]}\n"
        "🌐 Сервер: Активний"
    )
    await msg.answer(status_text, parse_mode="Markdown")

@dp.message(F.text == "ℹ️ Про розробника")
async def cmd_about(msg):
    about_text = (
        "🎓 **Звіт про розробку проєкту**\n\n"
        "👤 **Розробник:** Дмитро Васильчик\n"
        "🏫 **Група:** ІПЗ-111\n"
        "🔢 **Варіант завдання:** 3\n"
        "📍 **Регіон:** Одеська область\n\n"
        "💻 **Технології:**\n"
        "- Aiogram 3.4 (Async Telegram API)\n"
        "- Google Generative AI API (Gemini)\n"
        "- Python 3.10+ & Asyncio"
    )
    await msg.answer(about_text, parse_mode="Markdown", reply_markup=inline_links)


@dp.message(F.text.in_({"💻 ПК", "📱 Телефон", "🎮 Консоль", "🎯 Підібрати техніку", "💰 Оцінити техніку"}))
async def handle_hints(msg):
    hints = {
        "💻 ПК": "Напиши залізо у форматі: **ПК [Процесор, Відеокарта, ОЗП]**\nПриклад: ПК i5-12400, RTX 4060, 16GB",
        "📱 Телефон": "Напиши модель у форматі: **Телефон [Модель]**\nПриклад: Телефон Samsung S23 Ultra",
        "🎮 Консоль": "Напиши назву у форматі: **Консоль [Назва]**\nПриклад: Консоль Steam Deck",
        "🎯 Підібрати техніку": "Напиши задачі та бюджет.\nФормат: **Підбери [задачі] [бюджет]**\nПриклад: Підбери ноут для програмування до 30000 грн",
        "💰 Оцінити техніку": "Напиши свою стару техніку для оцінки.\nФормат: **Оціни [модель/характеристики]**\nПриклад: Оціни ПК Ryzen 5 3600, GTX 1660 Super, 16GB"
    }
    await msg.answer(hints[msg.text], parse_mode="Markdown")



@dp.message(F.text.lower().startswith("пк "))
async def process_pc_analysis(msg):
    await msg.bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.TYPING)
    status = await msg.answer("🔍 AI аналізує системні вимоги 18 ігор...")
    specifications = msg.text[3:]
    prompt = f"""
    Ти - експерт з комп'ютерного заліза. Оціни конфігурацію: {specifications}.
    Перевір сумісність для 60 FPS на ULTRA налаштуваннях для ігор:
    Dota 2, CS2, Fortnite, Elden Ring, Black Myth: Wukong, Arma Reforger, Resident Evil 4 Remake, 
    Hearts of Iron IV, GTA V, GTA IV, Red Dead Redemption 2, Cyberpunk 2077, Apex Legends, 
    Ready or Not, Minecraft, Battlefield 2042, Battlefield V, Battlefield 1.
    
    Використовуй емодзі: ✅ (тягне), ⚠️ (знизити налаштування), ❌ (не тягне).
    В кінці напиши "💡 Рекомендація з апгрейду": назви деталь та дай коротке посилання Hotline: 
    https://hotline.ua/sr/?q=[коротка_назва_деталі_через_плюс]
    """
    try:
        response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        await status.edit_text(response.text[:4000], disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"AI Error (PC): {e}")
        await status.edit_text("❌ Помилка AI API. Спробуйте пізніше.")

@dp.message(F.text.lower().startswith("телефон "))
async def process_phone_analysis(msg):
    await msg.bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.TYPING)
    status = await msg.answer("📱 AI перевіряє мобільний процесор та GPU...")
    model = msg.text[8:]
    prompt = f"""
    Ти мобільний аналітик. Оціни смартфон {model} для ігор: PUBG Mobile, Genshin Impact, CoD Mobile.
    Дай вердикт по FPS, нагріву та актуальності SOC на 2026 рік.
    Відповідай структуровано, коротко і без складного форматування.
    """
    try:
        response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        await status.edit_text(response.text[:4000])
    except Exception as e:
        logger.error(f"AI Error (Phone): {e}")
        await status.edit_text("❌ Помилка аналізу смартфона.")

@dp.message(F.text.lower().startswith("підбери "))
async def process_recommendation(msg):
    await msg.bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.TYPING)
    status = await msg.answer("🎯 AI аналізує твій запит та бюджет...")
    tasks = msg.text[8:]
    prompt = f"""
    Ти IT-консультант. Запит клієнта: "{tasks}".
    1. Визначити, ЯКИЙ САМЕ пристрій шукає клієнт. Якщо не вказано - запропонуй оптимальний.
    2. ФІНАНСИ: Якщо є бюджет - СУВОРО дотримуйся його.
    3. Пропонуй ТІЛЬКИ реально існуючі моделі.
    4. ПРАВИЛО ПОСИЛАНЬ: використовуй ТІЛЬКИ коротку комерційну назву в лінку (напр. "Acer Nitro 5").
    
    Структура відповіді:
    📱/💻/🖥️ **Рекомендація:** [Повна назва]
    🔗 **Посилання:** https://hotline.ua/sr/?q=[коротка_назва_через_плюс]
    📝 **Чому це ідеальний вибір:** [Опис під задачі клієнта]
    💡 **Експертна порада:** [Одне речення]
    """
    try:
        response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        await status.edit_text(response.text[:4000], disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"AI Error (Recommendation): {e}")
        await status.edit_text("❌ Не вдалося підібрати техніку. Спробуйте змінити запит.")

@dp.message(F.text.lower().startswith("оціни "))
async def process_valuation(msg):
    await msg.bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.TYPING)
    status = await msg.answer("⚖️ AI оцінює ринкову вартість на вторинному ринку...")
    hardware = msg.text[6:]
    prompt = f"""
    Ти експерт-оцінювач техніки. Клієнт просить оцінити: "{hardware}".
    
    Завдання:
    1. Зрозумій, що це (ПК, Ноутбук чи Телефон).
    2. Оціни актуальність заліза на 2026 рік.
    3. Назви АДЕКВАТНУ ціну продажу на Б/В ринку (в грн та $). Не завищуй ціни.
    4. Якщо це ПК: напиши 1-2 деталі під заміну. Якщо це телефон/ноутбук: порадь, продавати зараз чи залишити.
    5. Для апгрейду ПК генеруй коротке посилання Hotline.
    
    Структура:
    📊 **Актуальність (на 2026):** [Оцінка з 10 + коротке пояснення]
    💵 **Орієнтовна Б/В ціна:** [Сума грн / $]
    🛠 **Що замінити (Апгрейд):** [Порада + лінк (якщо ПК)]
    """
    try:
        response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        await status.edit_text(response.text[:4000], disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"AI Error (Valuation): {e}")
        await status.edit_text("❌ Не вдалося оцінити техніку.")

@dp.message(F.text.lower().startswith("консоль "))
async def process_console(msg):
    await msg.bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.TYPING)
    status = await msg.answer("🎮 Аналізую ігрову платформу...")
    console = msg.text[8:]
    prompt = f"Зроби огляд консолі {console}: FPS, роздільна здатність, 3 топ-ексклюзиви та актуальність."
    try:
        response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        await status.edit_text(response.text[:4000])
    except Exception as e:
        logger.error(f"AI Error (Console): {e}")
        await status.edit_text("❌ Помилка аналізу консолі.")

@dp.message()
async def fallback_handler(msg):
    error_text = (
        "🤔 Я не впізнав твій запит.\n\n"
        "Почни повідомлення з ключового слова:\n"
        "• **ПК** (аналіз ігор)\n"
        "• **Телефон** (мобільний геймінг)\n"
        "• **Консоль** (огляд приставки)\n"
        "• **Підбери** (пошук нової техніки)\n"
        "• **Оціни** (оцінка Б/В техніки та апгрейд)"
    )
    await msg.answer(error_text, parse_mode="Markdown")



async def main():
    bot = Bot(token=TG_TOKEN)
    logger.info("Бот успішно ініціалізований та готовий до роботи.")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Робота бота зупинена адміністратором.")