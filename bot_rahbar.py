"""
Nour English — Telegram бот «Рахбар»
Наставник, который определяет уровень английского и направляет студента.

Запуск:
    1. pip install -r requirements.txt
    2. Вставь токен своего бота в переменную BOT_TOKEN ниже
       (или задай переменную окружения BOT_TOKEN)
    3. python bot.py
"""

import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ──────────────────────────────────────────────
# НАСТРОЙКИ — поменяй под себя
# ──────────────────────────────────────────────

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8830833753:AAHQgjNEWR05uGHwdY3N8eJPMPu_S09uNYQ")

CHANNEL_LINK = "https://t.me/Nour_English_Edu"        # ссылка на твой канал
CHANNEL_NAME = "Nour English"
TEACHER_USERNAME = "https://t.me/@NalikeNy"          # замени на свой username для связи

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# РЕГИОНЫ (для часового пояса)
# ──────────────────────────────────────────────

REGIONS = {
    "ru_by_kz": "Россия / Беларусь / Казахстан",
    "europe": "Европа",
    "other": "Остальной мир",
}

# ──────────────────────────────────────────────
# НАПРАВЛЕНИЯ ОБУЧЕНИЯ
# ──────────────────────────────────────────────

DIRECTIONS = {
    "ege": "ЕГЭ / ОГЭ",
    "ielts": "IELTS / TOEFL",
    "relocate": "Английский для переезда",
    "speaking": "Разговорный английский",
    "scratch": "С нуля / для себя",
}

# ──────────────────────────────────────────────
# ВОПРОСЫ ТЕСТА — 30 штук, по возрастанию сложности
# level: 1 (легко) → 5 (сложно), используется для подсчёта итогового балла
# ──────────────────────────────────────────────

QUESTIONS = [
    # ---- Лёгкие (A1) ----
    {"q": "1/30. I ___ a student.", "options": ["am", "is", "are", "be"], "correct": 0, "level": 1},
    {"q": "2/30. This is ___ book.", "options": ["a", "an", "the", "—"], "correct": 0, "level": 1},
    {"q": "3/30. She ___ to school every day.", "options": ["go", "goes", "going", "gone"], "correct": 1, "level": 1},
    {"q": "4/30. There ___ many books on the table.", "options": ["is", "am", "are", "be"], "correct": 2, "level": 1},
    {"q": "5/30. ___ you like tea?", "options": ["Do", "Does", "Are", "Is"], "correct": 0, "level": 1},
    {"q": "6/30. My brother ___ football every weekend.", "options": ["play", "plays", "playing", "played"], "correct": 1, "level": 1},
    {"q": "7/30. They ___ at home now.", "options": ["is", "am", "are", "be"], "correct": 2, "level": 1},
    {"q": "8/30. I ___ a car. I walk to work.", "options": ["don't have", "doesn't have", "not have", "haven't"], "correct": 0, "level": 1},
    # ---- A2 ----
    {"q": "9/30. I have lived here ___ 2015.", "options": ["for", "since", "during", "from"], "correct": 1, "level": 2},
    {"q": "10/30. Yesterday I ___ to the cinema.", "options": ["go", "went", "gone", "going"], "correct": 1, "level": 2},
    {"q": "11/30. She is ___ than her sister.", "options": ["tall", "taller", "tallest", "more tall"], "correct": 1, "level": 2},
    {"q": "12/30. We ___ watching TV when you called.", "options": ["was", "were", "are", "be"], "correct": 1, "level": 2},
    {"q": "13/30. If it rains tomorrow, I ___ stay home.", "options": ["will", "would", "am", "was"], "correct": 0, "level": 2},
    {"q": "14/30. He has ___ finished his homework.", "options": ["already", "yet", "ago", "since"], "correct": 0, "level": 2},
    {"q": "15/30. Choose the closest meaning: 'huge'", "options": ["very small", "very large", "fast", "quiet"], "correct": 1, "level": 2},
    # ---- B1 ----
    {"q": "16/30. By the time we arrived, the film ___.", "options": ["already started", "had already started", "has already started", "was already starting"], "correct": 1, "level": 3},
    {"q": "17/30. She suggested ___ a different approach.", "options": ["to try", "trying", "try", "tried"], "correct": 1, "level": 3},
    {"q": "18/30. The report ___ by the team next week.", "options": ["will finish", "will be finished", "is finishing", "finishes"], "correct": 1, "level": 3},
    {"q": "19/30. I wish I ___ more time to prepare.", "options": ["have", "had", "has", "having"], "correct": 1, "level": 3},
    {"q": "20/30. He apologized ___ being late.", "options": ["for", "to", "about", "of"], "correct": 0, "level": 3},
    {"q": "21/30. Choose the closest meaning: 'reluctant'", "options": ["happy", "unwilling", "tired", "confident"], "correct": 1, "level": 3},
    {"q": "22/30. This task is ___ difficult than the last one.", "options": ["much", "very", "so", "too"], "correct": 0, "level": 3},
    # ---- B2 ----
    {"q": "23/30. Had I known about the traffic, I ___ earlier.", "options": ["would leave", "would have left", "left", "will leave"], "correct": 1, "level": 4},
    {"q": "24/30. The committee insisted that he ___ the form again.", "options": ["fills", "filled", "fill", "filling"], "correct": 2, "level": 4},
    {"q": "25/30. Choose the closest meaning: 'meticulous'", "options": ["careless", "very careful and precise", "fast", "lazy"], "correct": 1, "level": 4},
    {"q": "26/30. No sooner ___ home than the phone rang.", "options": ["I got", "had I got", "I had got", "did I got"], "correct": 1, "level": 4},
    {"q": "27/30. The new policy is likely to ___ significant changes.", "options": ["bring about", "bring up", "bring down", "bring out"], "correct": 0, "level": 4},
    # ---- C1 ----
    {"q": "28/30. Not only ___ late, but he also forgot the documents.", "options": ["he was", "was he", "he is", "is he"], "correct": 1, "level": 5},
    {"q": "29/30. Choose the closest meaning: 'ambiguous'", "options": ["very clear", "open to more than one interpretation", "boring", "urgent"], "correct": 1, "level": 5},
    {"q": "30/30. Were it not ___ his support, the project would have failed.", "options": ["for", "of", "with", "by"], "correct": 0, "level": 5},
]

# Уровни CEFR по итоговому количеству "очков уровня" (сумма level правильных ответов)
LEVEL_TABLE = [
    (0, 10, "A1 — Starter", "Базовый уровень. Начинаем с основ грамматики и словарного запаса."),
    (11, 24, "A2 — Elementary", "Знаешь основы, но нужно расширять словарь и закреплять грамматику."),
    (25, 44, "B1 — Intermediate", "Уверенный средний уровень. Готов к более сложным темам и практике."),
    (45, 64, "B2 — Upper-Intermediate", "Хороший уровень! Можно прицельно готовиться к экзаменам международного формата."),
    (65, 999, "C1 — Advanced", "Продвинутый уровень. Фокус на нюансах языка и экзаменационных стратегиях."),
]

# ──────────────────────────────────────────────
# СОСТОЯНИЕ ПОЛЬЗОВАТЕЛЯ (в памяти, без базы данных)
# ──────────────────────────────────────────────

user_state = {}  # user_id -> dict


def get_level(score: int):
    for low, high, name, desc in LEVEL_TABLE:
        if low <= score <= high:
            return name, desc
    return LEVEL_TABLE[-1][2], LEVEL_TABLE[-1][3]


# ──────────────────────────────────────────────
# СТАРТ / ВЫБОР РЕГИОНА
# ──────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_state[update.effective_user.id] = {}

    text = (
        "Ассаляму алейкум. 🌿\n\n"
        "Я — *Рахбар*, наставник школы *Nour English*. Помогаю каждому найти "
        "свой путь к английскому языку — определяю уровень, подбираю программу "
        "под цель и передаю заявку преподавателю.\n\n"
        "Сначала уточню — откуда ты пишешь? Это нужно, чтобы знать твой часовой пояс."
    )

    buttons = [
        [InlineKeyboardButton(label, callback_data=f"region:{key}")]
        for key, label in REGIONS.items()
    ]

    await update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown"
    )


async def region_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    region_key = query.data.split(":")[1]

    user_state.setdefault(user_id, {})
    user_state[user_id]["region"] = region_key

    await show_main_menu(query, edit=True)


# ──────────────────────────────────────────────
# ГЛАВНОЕ МЕНЮ
# ──────────────────────────────────────────────

async def show_main_menu(query_or_update, edit: bool = False):
    text = (
        "Чем могу помочь?\n\n"
        "📜 *Узнать свой уровень* — испытание из 30 вопросов, итог по шкале CEFR (A1–C1)\n"
        "💰 *Цены и программы* — все направления и пакеты\n"
        "🤝 *Записаться на пробный* — свяжется лично преподаватель\n"
        "✍️ *Написать преподавателю* — если хочешь сразу в личку"
    )

    buttons = [
        [InlineKeyboardButton("📜 Узнать свой уровень", callback_data="menu:test")],
        [InlineKeyboardButton("💰 Цены и программы", callback_data="menu:prices")],
        [InlineKeyboardButton("🤝 Записаться на пробный", callback_data="menu:trial")],
        [InlineKeyboardButton("✍️ Написать преподавателю", url=TEACHER_USERNAME)],
    ]
    markup = InlineKeyboardMarkup(buttons)

    if edit:
        await query_or_update.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")
    else:
        await query_or_update.message.reply_text(text, reply_markup=markup, parse_mode="Markdown")


async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action = query.data.split(":")[1]

    if action == "test":
        await show_test_intro(query)
    elif action == "prices":
        await show_prices(query)
    elif action == "trial":
        await show_trial_form(query)
    elif action == "back":
        await show_main_menu(query, edit=True)


# ──────────────────────────────────────────────
# ИНТРО К ТЕСТУ
# ──────────────────────────────────────────────

async def show_test_intro(query):
    text = (
        "📜 *Испытание уровня — 30 вопросов*\n\n"
        "Если не уверен — выбирай ближайший вариант. Не возвращайся назад. "
        "Займёт около 8–10 минут.\n\n"
        "Отвечай по чутью, не подглядывай — мне нужен чистый срез.\n\n"
        "В конце узнаешь свой уровень по шкале CEFR (A1–C1) и получишь "
        "рекомендацию по программе."
    )

    buttons = [
        [InlineKeyboardButton("Начать", callback_data="test:begin")],
        [InlineKeyboardButton("← Назад", callback_data="menu:back")],
    ]

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")


async def begin_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user_state.setdefault(user_id, {})
    user_state[user_id]["q_index"] = 0
    user_state[user_id]["score"] = 0

    await query.edit_message_text("Хорошо. Начинаем испытание. 🌿")
    await send_question(query.message.chat_id, user_id, context)


async def send_question(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE):
    state = user_state.get(user_id)
    if state is None or "q_index" not in state:
        return

    q_index = state["q_index"]

    if q_index >= len(QUESTIONS):
        await finish_test(chat_id, user_id, context)
        return

    question = QUESTIONS[q_index]
    buttons = [
        [InlineKeyboardButton(opt, callback_data=f"ans:{i}")]
        for i, opt in enumerate(question["options"])
    ]

    await context.bot.send_message(
        chat_id=chat_id,
        text=question["q"],
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def answer_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    state = user_state.get(user_id)

    if state is None or "q_index" not in state:
        await query.edit_message_text("Испытание сброшено. Напиши /start, чтобы начать заново.")
        return

    chosen_index = int(query.data.split(":")[1])
    q_index = state["q_index"]
    question = QUESTIONS[q_index]

    if chosen_index == question["correct"]:
        state["score"] += question["level"]

    await query.edit_message_text(question["q"])

    state["q_index"] += 1
    await send_question(query.message.chat_id, user_id, context)


async def finish_test(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE):
    state = user_state.get(user_id, {})
    score = state.get("score", 0)

    level_name, level_desc = get_level(score)

    text = (
        "🎉 *Испытание завершено!*\n\n"
        f"📊 Твой уровень: *{level_name}*\n"
        f"{level_desc}\n\n"
        "Теперь выбери направление, которое тебе ближе — и переходи на канал, "
        "там тебя ждут материалы под твой уровень и цель."
    )

    buttons = [
        [InlineKeyboardButton(label, callback_data=f"dir:{key}")]
        for key, label in DIRECTIONS.items()
    ]

    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown",
    )

    user_state[user_id] = {"region": state.get("region")}


async def direction_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    direction_key = query.data.split(":")[1]
    direction_label = DIRECTIONS.get(direction_key, "С нуля / для себя")

    text = (
        f"Хорошо, направление записано: *{direction_label}*. 🌿\n\n"
        "Переходи на канал — там уроки и материалы под твою цель:\n\n"
        f"👉 [{CHANNEL_NAME}]({CHANNEL_LINK})\n\n"
        "BaarakAllaahu Feekum!"
    )

    button = InlineKeyboardMarkup(
        [[InlineKeyboardButton(f"Перейти в {CHANNEL_NAME}", url=CHANNEL_LINK)]]
    )

    await query.edit_message_text(text, reply_markup=button, parse_mode="Markdown")
    user_state.pop(query.from_user.id, None)


# ──────────────────────────────────────────────
# ЦЕНЫ И ПРОГРАММЫ
# ──────────────────────────────────────────────

async def show_prices(query):
    text = (
        "💰 *Цены и программы Nour English*\n\n"
        "Заполни этот раздел своими актуальными пакетами и ценами — "
        "например:\n\n"
        "📌 ЕГЭ / ОГЭ — индивидуально / в группе\n"
        "📌 IELTS / TOEFL — подготовка к экзамену\n"
        "📌 Английский для переезда\n"
        "📌 Разговорный клуб\n\n"
        "Для уточнения цен и формата напиши преподавателю напрямую."
    )

    buttons = [
        [InlineKeyboardButton("✍️ Написать преподавателю", url=TEACHER_USERNAME)],
        [InlineKeyboardButton("← Назад", callback_data="menu:back")],
    ]

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")


# ──────────────────────────────────────────────
# ЗАПИСЬ НА ПРОБНЫЙ
# ──────────────────────────────────────────────

async def show_trial_form(query):
    text = (
        "🤝 *Запись на пробное занятие*\n\n"
        "Чтобы записаться — напиши преподавателю напрямую и укажи:\n\n"
        "1. Твой уровень (если проходил тест — напиши результат)\n"
        "2. Направление, которое интересует\n"
        "3. Удобное время для занятия\n\n"
        "Преподаватель свяжется с тобой лично."
    )

    buttons = [
        [InlineKeyboardButton("✍️ Написать преподавателю", url=TEACHER_USERNAME)],
        [InlineKeyboardButton("← Назад", callback_data="menu:back")],
    ]

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


# ──────────────────────────────────────────────
# ЗАПУСК
# ──────────────────────────────────────────────

def main():
    if BOT_TOKEN == "ВСТАВЬ_СЮДА_СВОЙ_ТОКЕН_ОТ_BOTFATHER":
        print("⚠️  Сначала вставь токен бота в переменную BOT_TOKEN!")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CallbackQueryHandler(region_chosen, pattern="^region:"))
    app.add_handler(CallbackQueryHandler(begin_test, pattern="^test:begin"))
    app.add_handler(CallbackQueryHandler(menu_router, pattern="^menu:"))
    app.add_handler(CallbackQueryHandler(answer_chosen, pattern="^ans:"))
    app.add_handler(CallbackQueryHandler(direction_chosen, pattern="^dir:"))

    print("Бот Рахбар запущен. Нажми Ctrl+C для остановки.")
    app.run_polling()


if __name__ == "__main__":
    main()
