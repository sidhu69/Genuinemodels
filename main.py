import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
import sqlite3
from models import MODELS  # Import your model data

# ---------------- LOGGING ----------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("reviews.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER,
    user_id INTEGER,
    rating INTEGER,
    review_text TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# ---------------- /START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📋 Available Models", callback_data="available_models")],
        [InlineKeyboardButton("⭐ Top Ranking Models", callback_data="top_models")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Hey 👋\n"
        "Genuine Model Bot mein aapka swagat hai.\n\n"
        "Please choose as per your requirement:",
        reply_markup=reply_markup
    )

# ---------------- BUTTON HANDLER ----------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # --- Available Models ---
    if query.data == "available_models":
        keyboard = []
        for model in MODELS:
            keyboard.append([InlineKeyboardButton(
                f"{model['name']} • {model['age']}",
                callback_data=f"model_{model['id']}"
            )])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("📋 Available Models:", reply_markup=reply_markup)

    # --- Top Ranking Models (placeholder) ---
    elif query.data == "top_models":
        await query.edit_message_text("⭐ Top Ranking Models will be shown here soon.")

    # --- Model Profile ---
    elif query.data.startswith("model_"):
        model_id = int(query.data.split("_")[1])
        model = next((m for m in MODELS if m["id"] == model_id), None)

        if not model:
            await query.edit_message_text("❌ Model not found.")
            return

        text = (
            f"👩 Name: {model['name']}\n"
            f"🎂 Age: {model['age']}\n"
            f"✅ Verified: {'Yes' if model['verified'] else 'No'}\n\n"
            "💰 Services:\n"
        )

        for service, price in model["services"].items():
            text += f"- {service}: ₹{price}\n"

        buttons = [
            [
                InlineKeyboardButton("📝 Give Review", callback_data=f"review_{model_id}"),
                InlineKeyboardButton("⭐ Watch Reviews", callback_data=f"watch_{model_id}")
            ],
            [InlineKeyboardButton("⬅ Back", callback_data="available_models")]
        ]

        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token("8479369659:AAEBNkqU1isZjJ1CXi8_84sks7erD_qO_ms").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
