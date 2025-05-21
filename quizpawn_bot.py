from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
import logging
import random

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

BOT_TOKEN = "7656183181:AAFilkbWdCR-2L36VSdAh5UC0YP0jkM9aO8"
SUPPORT_CHANNEL = "https://t.me/quizpawn"
DEV_CONTACT = "https://t.me/ragequit3"
GROUP_CHAT_ID = -1002492210221  # Replace with your actual group chat ID

trivia_list = [
    {
        "question": "What is the only move where two pieces move at once?",
        "options": ["Castling", "Promotion", "En Passant", "Check"],
        "answer": "Castling"
    },
    {
        "question": "What is the term for a game that ends without a winner?",
        "options": ["Draw", "Checkmate", "Resign", "Stalemate"],
        "answer": "Draw"
    },
    {
        "question": "Which piece starts next to the king?",
        "options": ["Bishop", "Queen", "Rook", "Knight"],
        "answer": "Bishop"
    },
    {
        "question": "What is en passant?",
        "options": [
            "A special pawn capture move",
            "A type of check",
            "A queen promotion",
            "An opening strategy"
        ],
        "answer": "A special pawn capture move"
    },
    {
        "question": "How many squares are on a chessboard?",
        "options": ["64", "32", "100", "81"],
        "answer": "64"
    }
]

def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Start Quiz", callback_data='start')],
        [InlineKeyboardButton("About", callback_data='about')],
    ])

def get_welcome_text_and_markup():
    welcome_text = (
        "♟️ *Welcome to Quizpawn Bot!* 🧠\n\n"
        "Your ultimate Chess Quiz companion for group battles!\n\n"
        "👥 *Add me to your group* and I will:\n"
        "🔁 Drop a new chess question every 30 minutes\n"
        "♟️ Sharpen your skills with fun and tricky puzzles\n"
        "🧠 Make your group smarter, one move at a time!\n\n"
        "🏁 *Ready to play?* Just add me to your group now!"
    )

    keyboard = [
        [InlineKeyboardButton("Join Support Channel", url=SUPPORT_CHANNEL)],
        [InlineKeyboardButton("About", callback_data="about")],
        [InlineKeyboardButton("Contact Developer", url=DEV_CONTACT)]
    ]
    return welcome_text, InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    logger.info(f"/start called in {chat.type} chat ID: {chat.id}")

    if chat.type == "private":
        text, markup = get_welcome_text_and_markup()
        await update.message.reply_text(text, reply_markup=markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(
            "✅ Quizpawn is active in this group! Use /startquiz to begin the 30-minute question cycle."
        )

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    job_name = str(chat.id)

    existing_jobs = context.job_queue.get_jobs_by_name(job_name)
    if existing_jobs:
        await update.message.reply_text("⚠️ Quiz is already running in this group.")
        return

    context.job_queue.run_repeating(
        send_trivia,
        interval=1800,
        first=5,
        chat_id=chat.id,
        name=job_name
    )
    logger.info(f"Started quiz in group ID: {chat.id}")
    await update.message.reply_text("✅ Quizpawn activated! I’ll send chess questions every 30 minutes!")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "about":
        await query.edit_message_text(
            text="*About Quizpawn Bot* (@quizpawnbot)\n\n"
                 "🧠 The ultimate chess quiz bot for group battles!\n"
                 "♟️ Automatic quizzes every 30 minutes\n"
                 "➤ Fun, tricky questions for players of all levels\n\n"
                 "Challenge friends, learn, and enjoy chess together!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Back", callback_data="main_menu")]
            ])
        )
    elif query.data == "main_menu":
        text, markup = get_welcome_text_and_markup()
        await query.edit_message_text(text=text, reply_markup=markup, parse_mode="Markdown")
    elif query.data.startswith("answer|"):
        _, selected, correct = query.data.split("|")
        response = "✅ Correct!" if selected == correct else f"❌ Wrong! The correct answer was *{correct}*."
        await query.edit_message_text(text=response, parse_mode="Markdown")

async def send_trivia(context: ContextTypes.DEFAULT_TYPE):
    group_id = context.job.chat_id
    trivia = random.choice(trivia_list)
    question = trivia["question"]
    options = trivia["options"]
    correct_answer = trivia["answer"]

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=f"answer|{opt}|{correct_answer}")]
        for opt in options
    ]

    await context.bot.send_message(
        chat_id=group_id,
        text=f"♟️ *Chess Trivia!*\n\n*{question}*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def startup_quiz(context: ContextTypes.DEFAULT_TYPE):
    context.job_queue.run_repeating(
        send_trivia,
        interval=120,
        first=5,
        chat_id=GROUP_CHAT_ID,
        name="auto_quiz"
    )
    logger.info("Auto quiz started at bot launch.")

# Launch bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("startquiz", start_quiz))
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()
