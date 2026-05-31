#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# ============================================================
# ⚙️ الإعدادات
# ============================================================

BOT_TOKEN = "8955994559:AAHl5sFqatbeA-5nWQ7cBg_EXbGyITLCYCs"
ADMIN_ID = "8553407440"

DATA_DIR = os.path.join(os.path.dirname(__file__), "@wolf_data")
os.makedirs(DATA_DIR, exist_ok=True)

# ============================================================
# 📝 Logging
# ============================================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================================
# 📁 أدوات الملفات
# ============================================================

def read_list(name):
    path = os.path.join(DATA_DIR, f"{name}.txt")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [x.strip() for x in f.readlines() if x.strip()]

def write_item(name, item):
    item = str(item)
    items = read_list(name)
    if item not in items:
        with open(os.path.join(DATA_DIR, f"{name}.txt"), "a", encoding="utf-8") as f:
            f.write(item + "\n")

def remove_item(name, item):
    items = read_list(name)
    if item in items:
        items.remove(item)
        with open(os.path.join(DATA_DIR, f"{name}.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(items))

# ============================================================
# 🔐 حالات المستخدم
# ============================================================

def is_banned(uid):
    return str(uid) in read_list("b")

def is_vip(uid):
    return str(uid) in read_list("vip")

def add_member(uid):
    write_item("m", uid)

# ============================================================
# 🎛️ الكيبوردات
# ============================================================

ADMIN_KB = InlineKeyboardMarkup([
    [InlineKeyboardButton("🛑 إيقاف البوت", callback_data="off"),
     InlineKeyboardButton("▶️ تشغيل البوت", callback_data="on")],
    [InlineKeyboardButton("🚫 الحظر", callback_data="ban_sec"),
     InlineKeyboardButton("📨 رسالة", callback_data="msg_sec")],
    [InlineKeyboardButton("👑 VIP", callback_data="vip_sec")],
    [InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")]
])

MAIN_KB = InlineKeyboardMarkup([
    [InlineKeyboardButton("❤️ تفاعل", callback_data="cr_interaction"),
     InlineKeyboardButton("🌐 أرقام", callback_data="cr_numbers")],
    [InlineKeyboardButton("🗑 منع تصفية", callback_data="cr_filter"),
     InlineKeyboardButton("👍 لايكات", callback_data="cr_likes")],
    [InlineKeyboardButton("♻️ ويب هوك", callback_data="cr_webhook")],
    [InlineKeyboardButton("👑 VIP", callback_data="buy_vip")]
])

# ============================================================
# 🛠️ أوامر البوت
# ============================================================

def start(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    name = update.effective_user.first_name

    if is_banned(uid):
        update.message.reply_text("🚫 أنت محظور.")
        return

    add_member(uid)

    if uid == ADMIN_ID:
        update.message.reply_text(
            f"⚙️ لوحة التحكم\nالحالة: ✅ يعمل",
            reply_markup=ADMIN_KB
        )
    else:
        status = "👑 VIP" if is_vip(uid) else "👤 عادي"
        update.message.reply_text(
            f"مرحباً {name} 👋\n\nحسابك: {status}",
            reply_markup=MAIN_KB
        )

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    uid = str(query.from_user.id)

    if uid == ADMIN_ID:
        if query.data == "on":
            query.edit_message_text("✅ تم تشغيل البوت.", reply_markup=ADMIN_KB)
        elif query.data == "off":
            query.edit_message_text("❌ تم إيقاف البوت.", reply_markup=ADMIN_KB)
        elif query.data == "stats":
            users = len(read_list("m"))
            vips = len(read_list("vip"))
            banned = len(read_list("b"))
            query.edit_message_text(
                f"📊 الإحصائيات\n\n👥 المستخدمين: {users}\n👑 VIP: {vips}\n🚫 المحظورين: {banned}",
                reply_markup=ADMIN_KB
            )
        elif query.data == "ban_sec":
            # مثال: حظر مستخدم معين
            target_id = "123456789"
            write_item("b", target_id)
            query.answer("🚫 تم الحظر.")
        elif query.data == "vip_sec":
            target_id = "123456789"
            write_item("vip", target_id)
            query.answer("👑 تمت إضافة VIP.")
    else:
        if is_banned(uid):
            query.answer("🚫 أنت محظور.")
        else:
            query.answer("✅ تم تسجيل تفاعلك.")

# ============================================================
# 🚀 التشغيل
# ============================================================

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
