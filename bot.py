import os
import asyncio
import random

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

games = {}

WORDS = [
    "olma", "banan", "tarvuz", "pizza", "mashina",
    "samolyot", "mushuk", "it", "uy", "telefon",
    "futbol", "gitara", "oy", "quyosh", "dengiz",
    "maktab", "kompyuter", "muzqaymoq", "velosiped",
    "televizor", "kitob", "qalam", "soat", "non",
    "hamburger", "tort", "kofe", "choy", "gul",
    "daraxt", "yomg'ir", "qor", "tog'", "daryo",
    "ko'prik", "avtobus", "poyezd", "velosiped",
    "kamera", "quloqchin", "klaviatura", "sichqoncha"
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🕵️ Spy Game botiga xush kelibsiz!\n\n"
        "🎮 Guruhda o‘yin boshlash uchun /game yozing."
    )


async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id in games:
        await update.message.reply_text(
            "🎮 Bu guruhda allaqachon o‘yin bor!"
        )
        return

    games[chat_id] = {
        "players": {},
        "status": "waiting"
    }

    keyboard = [
        [
            InlineKeyboardButton(
                "➕ O‘yinga qo‘shilish",
                callback_data="join"
            )
        ],
        [
            InlineKeyboardButton(
                "🚀 O‘yinni boshlash",
                callback_data="begin"
            )
        ]
    ]

    await update.message.reply_text(
        "🕵️ SPY GAME\n\n"
        "👥 O‘yinga qo‘shiling!\n"
        "Kerakli o‘yinchilar: 4–10 kishi.\n\n"
        "Pastdagi tugmani bosing 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id
    user = query.from_user

    if chat_id not in games:
        return

    game_data = games[chat_id]

    if query.data == "join":

        if game_data["status"] != "waiting":
            await query.answer(
                "❌ O‘yin allaqachon boshlangan!",
                show_alert=True
            )
            return

        if user.id in game_data["players"]:
            await query.answer(
                "Siz allaqachon qo‘shilgansiz!",
                show_alert=True
            )
            return

        if len(game_data["players"]) >= 10:
            await query.answer(
                "❌ O‘yinchilar soni 10 taga yetdi!",
                show_alert=True
            )
            return

        game_data["players"][user.id] = user.first_name

        names = "\n".join(
            f"👤 {name}"
            for name in game_data["players"].values()
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "➕ O‘yinga qo‘shilish",
                    callback_data="join"
                )
            ],
            [
                InlineKeyboardButton(
                    "🚀 O‘yinni boshlash",
                    callback_data="begin"
                )
            ]
        ]

        await query.edit_message_text(
            f"🕵️ SPY GAME\n\n"
            f"👥 O‘yinchilar "
            f"({len(game_data['players'])}/10):\n"
            f"{names}\n\n"
            f"Kamida 4 kishi kerak.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "begin":

        count = len(game_data["players"])

        if count < 4:
            await query.answer(
                "❌ Kamida 4 ta o‘yinchi kerak!",
                show_alert=True
            )
            return

        game_data["status"] = "started"

        word = random.choice(WORDS)
        spy_id = random.choice(
            list(game_data["players"].keys())
        )

        game_data["word"] = word
        game_data["spy"] = spy_id

        await query.edit_message_text(
            "🎮 O‘YIN BOSHLANDI!\n\n"
            f"👥 O‘yinchilar: {count} ta\n"
            "🕵️ Spy tasodifiy tanlandi.\n\n"
            "📩 Har bir o‘yinchiga maxfiy xabar yuborildi.\n"
            "🔄 3 ta raund bo‘ladi."
        )

        for player_id in game_data["players"]:

            try:
                if player_id == spy_id:
                    await context.bot.send_message(
                        chat_id=player_id,
                        text=(
                            "🕵️ SIZ — SPY!\n\n"
                            "❌ Sizga maxfiy so‘z berilmaydi.\n"
                            "👀 Boshqa o‘yinchilarning gaplarini "
                            "kuzating va so‘zni topishga harakat qiling."
                        )
                    )
                else:
                    await context.bot.send_message(
                        chat_id=player_id,
                        text=(
                            "🤫 MAXFIY SO‘Z:\n\n"
                            f"🔐 {word}\n\n"
                            "⚠️ Bu so‘zni guruhda aytmang!"
                        )
                    )

            except Exception:
                pass


def main():

    if not BOT_TOKEN:
        print("❌ BOT_TOKEN topilmadi!")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("game", game))
    app.add_handler(CallbackQueryHandler(button))

    print("🕵️ Spy Game bot ishga tushdi!")

    async def run():

        await app.initialize()
        await app.start()
        await app.updater.start_polling()

        try:
            await asyncio.Event().wait()

        finally:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()

    asyncio.run(run())


if __name__ == "__main__":
    main()