from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, CommandHandler, CallbackQueryHandler,MessageHandler, filters, ContextTypes)
from telegram.ext import JobQueue
import random

# Replace with your actual bot token and links
BOT_TOKEN = "YOUR_BOT_TOKEN"
SUPPORT_CHANNEL = "https://t.me/YOUR_CHANNEL"
DEV_CONTACT = "https://t.me/YOUR_USERNAME"

# Sample trivia questions
trivia_list = ["What is the only move where two pieces move at once? Answer: Castling.","What is the term for a game that ends without a winner? Answer: Draw.","Which piece starts next to the king? Answer: Bishop.","What is en passant? A special pawn capture move.","How many squares are on a chessboard? Answer: 64."]

# Start command for private chat
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):if update.effective_chat.type == "private":welcome_text = ("♟️ *Welcome to Quizpawn Bot!* 🧠\n\n""Your ultimate Chess Quiz companion for group battles!\n\n""👥 *Add me to your group* and I will:\n""🔁 Drop a new chess question every 30 minutes\n""♟️ Sharpen your skills with fun and tricky puzzles\n""🧠 Make your group smarter, one move at a time!\n\n""🏁 *Ready to play?* Just add me to your group now!") keyboard = [[InlineKeyboardButton("Join Support Channel", url=SUPPORT_CHANNEL)],[InlineKeyboardButton("About", callback_data="about")],[InlineKeyboardButton("Contact Developer", url=DEV_CONTACT)]]reply_markup = InlineKeyboardMarkup(keyboard)
await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# Respond to "About" button
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):query = update.callback_query await query.answer()
if query.data == "about":
        await query.edit_message_text(
            text=(
                "*About Quizpawn Bot*\n\n"
                "I drop chess trivia and quiz questions in groups every 30 minutes.\n"
                "Perfect for fun group challenges and learning!"
            ),
            parse_mode="Markdown"
        )

# Auto-send trivia to group every 30 minutes
async def send_trivia(context: ContextTypes.DEFAULT_TYPE):
    group_id = context.job.chat_id
    question = random.choice(trivia_list)
    await context.bot.send_message(chat_id=group_id, text=f"♟️ *Chess Trivia!*\n\n{question}", parse_mode="Markdown")

# When bot is added to a group or any message in a group
async def group_watcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    # Only proceed if it's a group or supergroup
    if chat.type in ["group", "supergroup"]:
        # Start auto-trivia if not already started
        context.job_queue.run_repeating(
            send_trivia, interval=1800, first=10, chat_id=chat.id, name=str(chat.id)
        )
        await update.message.reply_text("♟️ Quizpawn activated! I’ll send chess questions every 30 minutes!")

# Build app
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.ChatType.GROUPS, group_watcher))

# Run bot
app.run_polling()