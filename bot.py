"""
CYBER NEXUS — Telegram Bot v3 starter
School search flow: user sends school name, then EIIN/code; project validates and
accepts both inputs. Actual school records require an official/authorized data API.
"""
import logging
import os
import re
from urllib.parse import urlparse

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, ContextTypes, MessageHandler, filters
)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
BOT_DISPLAY_NAME = os.getenv("BOT_DISPLAY_NAME", "CYBER NEXUS")
FACEBOOK_PAGE_URL = os.getenv(
    "FACEBOOK_PAGE_URL", "https://www.facebook.com/profile.php?id=61591259447085"
).strip()
SUPPORT_FACEBOOK_URL = os.getenv(
    "SUPPORT_FACEBOOK_URL", "https://www.facebook.com/share/14pUW7eCkaP/"
).strip()
ADMIN_IDS = {
    int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
}
# Optional exact school API endpoint/token; keep credentials in environment variables.
SCHOOL_API_URL = os.getenv("SCHOOL_API_URL", "").strip()
SCHOOL_API_KEY = os.getenv("SCHOOL_API_KEY", "").strip()

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("cyber_nexus")

MENU = [
    [KeyboardButton("🎬 ভিডিও ডাউনলোড"), KeyboardButton("🏫 স্কুলের তথ্য")],
    [KeyboardButton("📢 Telegram Channel"), KeyboardButton("🌐 IP তথ্য")],
    [KeyboardButton("🔎 TikTok তথ্য"), KeyboardButton("▶️ YouTube তথ্য")],
    [KeyboardButton("🔳 QR তৈরি"), KeyboardButton("✉️ Email যাচাই")],
    [KeyboardButton("📱 নম্বর ফরম্যাট"), KeyboardButton("🧰 Extra Tools")],
    [KeyboardButton("📘 Facebook Page"), KeyboardButton("🆘 সাহায্য")],
    [KeyboardButton("🛠️ Admin Panel"), KeyboardButton("ℹ️ বট সম্পর্কে")],
]

def is_url(value: str) -> bool:
    try:
        p = urlparse(value.strip())
        return p.scheme in {"http", "https"} and bool(p.netloc)
    except Exception:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["verified"] = False
    keyboard = [
        [{"text": "📘 Facebook Page", "url": FACEBOOK_PAGE_URL}],
        [{"text": "✅ ফলো করেছি — যাচাইয়ের অনুরোধ", "callback_data": "verify_request"}],
        [{"text": "🆘 সাহায্য", "url": SUPPORT_FACEBOOK_URL}],
    ]
    # Telegram inline URL buttons cannot be built from raw dicts in ReplyKeyboard;
    # use normal inline keyboard markup.
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    verify_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("📘 Facebook Page খুলুন", url=FACEBOOK_PAGE_URL)],
        [InlineKeyboardButton("✅ ফলো করেছি — যাচাইয়ের অনুরোধ", callback_data="verify_request")],
        [InlineKeyboardButton("🆘 সাহায্য নিন", url=SUPPORT_FACEBOOK_URL)],
    ])
    await update.effective_message.reply_text(
        f"স্বাগতম {BOT_DISPLAY_NAME}-এ!\n\n"
        "বটের সব ফিচার চালুর আগে Facebook Page-এ যাওয়ার অনুরোধ দেখানো হচ্ছে।\n"
        "⚠️ শুধু Facebook লিংক দিয়ে আপনি সত্যিই Follow করেছেন কি না, Telegram bot "
        "স্বয়ংক্রিয়ভাবে নিশ্চিত করতে পারে না। তাই 'যাচাইয়ের অনুরোধ' চাপলে অ্যাডমিন "
        "ম্যানুয়ালি যাচাই করবেন। যাচাইয়ের আগে সীমিত মেনু দেখানো হবে।",
        reply_markup=verify_markup,
    )
    await update.effective_message.reply_text(
        "সাহায্যের জন্য নিচের লিংক:\n" + SUPPORT_FACEBOOK_URL
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "কমান্ড:\n/start — শুরু\n/id — আপনার Telegram ID\n/help — সাহায্য\n"
        "/admin — অ্যাডমিন প্যানেল\n/approve USER_ID — ফলো ম্যানুয়ালি যাচাই করে অনুমোদন (অ্যাডমিন)"
    )

async def show_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        f"আপনার Telegram numeric ID: {update.effective_user.id}\n"
        "এটি ADMIN_IDS-এ বসানোর জন্য; এটি bot token নয়।"
    )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.effective_message.reply_text("⛔ এই কমান্ড শুধু অ্যাডমিনদের জন্য।")
        return
    await update.effective_message.reply_text(
        "🛠️ CYBER NEXUS Admin Panel\n"
        "/stats — বটের অবস্থা\n"
        "/approve USER_ID — Facebook follow ম্যানুয়ালি যাচাই করে অনুমোদন\n"
        "নোট: এই starter-এ persistent database নেই; restart হলে approval state হারাবে।"
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.effective_message.reply_text("⛔ অনুমতি নেই।")
        return
    await update.effective_message.reply_text("✅ CYBER NEXUS চলছে।")

async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.effective_message.reply_text("⛔ অনুমতি নেই।")
        return
    if not context.args or not context.args[0].isdigit():
        await update.effective_message.reply_text("ব্যবহার: /approve USER_ID")
        return
    target_id = int(context.args[0])
    # In-memory approval for this running process only.
    context.application.bot_data.setdefault("approved_users", set()).add(target_id)
    try:
        await context.bot.send_message(
            chat_id=target_id,
            text="✅ অ্যাডমিন আপনার অনুরোধ অনুমোদন করেছেন। এখন /start দিন।"
        )
    except Exception:
        pass
    await update.effective_message.reply_text(
        f"User ID {target_id} অনুমোদিত হয়েছে (বট চালু থাকা পর্যন্ত)।"
    )

async def school_name_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["school_step"] = "name"
    await update.effective_message.reply_text(
        "🏫 প্রথমে স্কুলের পুরো নাম লিখুন।\n"
        "তারপর আমি EIIN/ছোট কোড চাইব। দুইটি তথ্য পাওয়ার পর নির্ভরযোগ্য ডেটাসোর্স "
        "সংযুক্ত থাকলে স্কুলের তথ্য দেখানো যাবে।"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    text = (msg.text or "").strip()
    uid = update.effective_user.id
    approved = uid in context.application.bot_data.get("approved_users", set())

    # Only basic navigation/support is available until manual approval.
    if not approved:
        if text in {"🆘 সাহায্য", "📘 Facebook Page"}:
            await msg.reply_text(
                "Facebook Page:\n" + FACEBOOK_PAGE_URL + "\n\n"
                "সাহায্য:\n" + SUPPORT_FACEBOOK_URL
            )
        elif text == "🏫 স্কুলের তথ্য":
            await msg.reply_text("ফিচার চালুর আগে Facebook follow যাচাই দরকার। /start থেকে নির্দেশনা দেখুন।")
        else:
            await msg.reply_text(
                "🔒 সব ফিচার চালুর আগে Facebook Page follow যাচাই করতে হবে।\n"
                "Page: " + FACEBOOK_PAGE_URL + "\n"
                "Follow করার পর /start খুলে যাচাইয়ের অনুরোধ পাঠান। "
                "এই starter-এ অ্যাডমিন ম্যানুয়ালি যাচাই করবেন।"
            )
        return

    if text == "🏫 স্কুলের তথ্য":
        context.user_data["school_step"] = "name"
        await msg.reply_text("প্রথমে স্কুলের নাম লিখুন।")
    elif context.user_data.get("school_step") == "name":
        context.user_data["school_name"] = text
        context.user_data["school_step"] = "code"
        await msg.reply_text(
            f"স্কুলের নাম: {text}\nএবার EIIN বা ছোট কোডটি লিখুন।"
        )
    elif context.user_data.get("school_step") == "code":
        code = text.strip()
        school_name = context.user_data.get("school_name", "অজানা")
        context.user_data.pop("school_step", None)
        context.user_data.pop("school_name", None)
        if not re.fullmatch(r"\d{4,8}", code):
            await msg.reply_text("EIIN/কোডটি সঠিক মনে হচ্ছে না। ৪–৮ সংখ্যার কোড দিন।")
        else:
            await msg.reply_text(
                f"🔎 স্কুলের নাম: {school_name}\nEIIN/কোড: {code}\n\n"
                "এই প্রকল্পে এখনও কোনো সরকারি/অনুমোদিত স্কুল ডেটাবেস API সংযুক্ত নেই, "
                "তাই যাচাইকৃত স্কুলের সব তথ্য এখনই দেখানো সম্ভব নয়। "
                "API/ডেটাসোর্স যুক্ত হলে এখানে নাম, ঠিকানা, প্রতিষ্ঠান-সংক্রান্ত "
                "প্রকাশ্য তথ্য দেখানো যাবে। ব্যক্তিগত শিক্ষকের গোপন তথ্য দেখানো হবে না।"
            )
    elif text == "🎬 ভিডিও ডাউনলোড":
        await msg.reply_text("সমর্থিত পাবলিক ভিডিও URL পাঠান। বাস্তব ডাউনলোডের জন্য অনুমোদিত integration দরকার।")
    elif text in {"📢 Telegram Channel", "🌐 IP তথ্য", "🔎 TikTok তথ্য", "▶️ YouTube তথ্য"}:
        await msg.reply_text("পাবলিক URL বা তথ্য পাঠান। লাইভ ফলাফলের জন্য সংশ্লিষ্ট অনুমোদিত API দরকার।")
    elif text == "🔳 QR তৈরি":
        await msg.reply_text("QR-এ রাখতে চান এমন লেখা/URL পাঠান। QR PNG তৈরি করতে generator library যোগ করতে হবে।")
    elif text == "✉️ Email যাচাই":
        await msg.reply_text("শুধু ইমেইলের ফরম্যাট যাচাইয়ের সুবিধা যোগ করা যাবে; গোপন account lookup নয়।")
    elif text == "📱 নম্বর ফরম্যাট":
        await msg.reply_text("নম্বরের ফরম্যাট যাচাই করা যাবে; মালিকের পরিচয়/ঠিকানা খোঁজা হবে না।")
    elif text == "🧰 Extra Tools":
        await msg.reply_text("/help এবং /id ব্যবহার করুন।")
    elif text == "📘 Facebook Page":
        await msg.reply_text(FACEBOOK_PAGE_URL)
    elif text == "🆘 সাহায্য":
        await msg.reply_text("সাহায্যের জন্য Facebook: " + SUPPORT_FACEBOOK_URL)
    elif text == "🛠️ Admin Panel":
        await admin_command(update, context)
    elif text == "ℹ️ বট সম্পর্কে":
        await msg.reply_text("CYBER NEXUS — বাংলা Telegram bot starter।")
    elif is_url(text):
        await msg.reply_text("URL পেয়েছি। এই starter-এ live download/lookup integration নেই।")
    else:
        await msg.reply_text("মেনু থেকে একটি অপশন বেছে নিন অথবা /help লিখুন।")

async def verify_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # No automatic follow check possible from a URL alone; alert admin for manual review.
    admin_ids = ADMIN_IDS
    for admin_id in admin_ids:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"📩 Facebook follow যাচাইয়ের অনুরোধ\nUser ID: {query.from_user.id}\n"
                     f"ম্যানুয়ালি যাচাই করে /approve {query.from_user.id} দিন।"
            )
        except Exception:
            pass
    await query.edit_message_text(
        "আপনার যাচাইয়ের অনুরোধ পাঠানো হয়েছে। অ্যাডমিন Facebook Page follow যাচাই করে "
        "অনুমোদন দিলে ফিচার চালু হবে।"
    )

def main():
    if not BOT_TOKEN or BOT_TOKEN == "PASTE_YOUR_BOTFATHER_TOKEN_HERE":
        raise SystemExit("BOT_TOKEN সেট করা হয়নি। .env.example কপি করে .env বানিয়ে token বসান।")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("id", show_id))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("approve", approve_command))
    from telegram import CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(verify_request, pattern="^verify_request$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    log.info("%s starting", BOT_DISPLAY_NAME)
    app.run_polling()

if __name__ == "__main__":
    main()
