from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
import random

BOT_TOKEN = "7656183181:AAFilkbWdCR-2L36VSdAh5UC0YP0jkM9aO8"
SUPPORT_CHANNEL = "https://t.me/quizpawn"
DEV_CONTACT = "https://t.me/ragequit3"

# ✅ Trivia data with options
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

# Main menu
def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Start Quiz", callback_data='start')],
        [InlineKeyboardButton("About", callback_data='about')],
    ])

# Welcome text and buttons
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
    reply_markup = InlineKeyboardMarkup(keyboard)
    return welcome_text, reply_markup

# /start for private chats
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        welcome_text, reply_markup = get_welcome_text_and_markup()
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# /startquiz for groups
async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type in ["group", "supergroup"]:
        job_name = str(chat.id)
        # Prevent duplicate jobs
        existing_jobs = context.job_queue.get_jobs_by_name(job_name)
        if existing_jobs:
            await update.message.reply_text("⚠️ Quiz is already running in this group.")
            return
        context.job_queue.run_repeating(
            send_trivia,
            interval=60,
            first=5,
            chat_id=chat.id,
            name=job_name
        )
        await update.message.reply_text("✅ Quizpawn activated! I’ll send chess questions every 1 minute!")

# Callback handler for buttons
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "about":
        await query.edit_message_text(
            text="*About Quizpawn Bot*(@quizpawnbot)\n\n🧠"
                 "Welcome to ThinkChessy, your ultimate chess quiz companion \n"
                 "♟️We bring the world of chess to life through fun, engaging, and challenging quizzes — perfect for casual players, learners, and chess masters alike!\n"
                 "\n➤ Sends automatic chess quizzes every 30 minutes in group chats"
                 "\n➤ Covers everything from classic tactics to modern legends"
                 "\n➤ Easy to set up with the /settings command\n\n"
                 "Challenge your friends, sharpen your skills, and rule the 64 squares with brains and strategy.\n"
                 "Let the game begin!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Back", callback_data="main_menu")]
            ])
        )

    elif query.data == "main_menu":
        welcome_text, reply_markup = get_welcome_text_and_markup()
        await query.edit_message_text(
            text=welcome_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    elif query.data.startswith("answer|"):
        _, selected, correct = query.data.split("|")
        if selected == correct:
            reply_text = "✅ Correct!"
        else:
            reply_text = f"❌ Wrong! The correct answer was *{correct}*."
        await query.edit_message_text(text=reply_text, parse_mode="Markdown")

# Trivia sender function
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
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=group_id,
        text=f"♟️ *Chess Trivia!*\n\n*{question}*",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# Start the bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))  # for private chats
app.add_handler(CommandHandler("startquiz", start_quiz))  # for group quiz start
app.add_handler(CallbackQueryHandler(button_handler))
app.run_polling()
