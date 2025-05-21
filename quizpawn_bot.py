from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
import random

BOT_TOKEN = "7656183181:AAFilkbWdCR-2L36VSdAh5UC0YP0jkM9aO8"
SUPPORT_CHANNEL = "https://t.me/quizpawn"
DEV_CONTACT = "https://t.me/ragequit3"

trivia_list = [
    "What is the only move where two pieces move at once? Answer: Castling.",
    "What is the term for a game that ends without a winner? Answer: Draw.",
    "Which piece starts next to the king? Answer: Bishop.",
    "What is en passant? A special pawn capture move.",
    "How many squares are on a chessboard? Answer: 64."
]
def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Start Quiz", callback_data='start')],
        [InlineKeyboardButton("About", callback_data='about')],
            ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
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

        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")


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
"\n➤ Easy to set up with the /settings command"

"Challenge your friends, sharpen your skills, and rule the 64 squares with brains and strategy."
"Let the game begin!",
            parse_mode="Markdown",
reply_markup=InlineKeyboardMarkup([
[InlineKeyboardButton("Back", callback_data="main_menu")]
])
            )
    elif query.data == "main_menu":
        await query.edit_message_text(
            text="Welcome back to main menu!",
            reply_markup=get_main_menu()
        )


async def send_trivia(context: ContextTypes.DEFAULT_TYPE):
    group_id = context.job.chat_id
    question = random.choice(trivia_list)
    await context.bot.send_message(chat_id=group_id, text=f"♟️ *Chess Trivia!*\n\n{question}", parse_mode="Markdown")

async def group_watcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type in ["group", "supergroup"]:
        context.job_queue.run_repeating(
            send_trivia, interval=1800, first=10, chat_id=chat.id, name=str(chat.id)
        )
        await update.message.reply_text("♟️ Quizpawn activated! I’ll send chess questions every 30 minutes!")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.ChatType.GROUPS, group_watcher))
app.run_polling()
