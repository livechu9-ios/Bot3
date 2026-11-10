# -*- coding: utf-8 -*-
"""
VC UDID VERIFY - Telegram Bot
Chuyen tu Discord (2.py) sang Telegram
"""

import telebot
from telebot import types

# =================================
# CONFIG
# =================================

BOT_TOKEN = "9093083128:AAEN_pqXRabqdnRK159MXy2nN6tngpdu9J8"   # <-- Thay token bot Telegram
UDID_URL = "https://udid.tech"

bot = telebot.TeleBot(BOT_TOKEN)

# Lưu user đã xác minh UDID
verified_users = set()


# =================================
# KEYBOARD BUILDERS
# =================================

def udid_keyboard():
    """Menu chính: LẤY UDID (link) + ĐÃ XÁC MINH UDID"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("LẤY UDID", url=UDID_URL),
        types.InlineKeyboardButton(
            "ĐÃ XÁC MINH UDID",
            callback_data="vc_verify_udid"
        )
    )
    return markup


def function_keyboard(confirm_enabled=False):
    """Menu chức năng sau khi xác minh"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(
            "NHẤY TẦM OPTIMION",
            callback_data="choose_func"
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            "XÁC NHẬN LỰA CHỌN",
            callback_data="confirm_func"
        ) if confirm_enabled else
        types.InlineKeyboardButton(
            "XÁC NHẬN (chưa chọn)",
            callback_data="confirm_disabled"
        )
    )
    return markup


# =================================
# /start - MENU CHÍNH
# =================================

@bot.message_handler(commands=["start", "setup"])
def cmd_start(message):
    text = (
        "—————————————\n"
        "VC UDID VERIFY\n"
        "—————————————\n\n"
        "1. LẤY UDID\n"
        "Nhấn nút LẤY UDID.\n\n"
        "2. XÁC MINH\n"
        "Nhấn ĐÃ XÁC MINH UDID.\n\n"
        "3. CHỌN CHỨC NĂNG\n"
        "NHẦY TẦM OPTIMION.\n"
        "—————————————\n"
        "VC SYSTEM | UDID VERIFY"
    )
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=udid_keyboard()
    )


# =================================
# XỬ LÝ CALLBACK
# =================================

@bot.callback_query_handler(func=lambda c: True)
def on_callback(call):
    try:
        uid = call.from_user.id

        # --- BƯỚC 1: XÁC MINH UDID ---
        if call.data == "vc_verify_udid":
            verified_users.add(uid)
            text = (
                "VC | XÁC MINH THÀNH CÔNG\n\n"
                "Bạn đã xác nhận UDID!\n\n"
                "Hãy chọn chức năng bên dưới."
            )
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=function_keyboard(confirm_enabled=False)
            )
            bot.answer_callback_query(call.id, "Đã xác minh UDID")
            return

        # --- KIỂM TRA ĐÃ XÁC MINH CHƯA ---
        if uid not in verified_users:
            bot.answer_callback_query(
                call.id,
                "Vui lòng xác minh UDID trước!",
                show_alert=True
            )
            return

        # --- BƯỚC 2: CHỌN CHỨC NĂNG ---
        if call.data == "choose_func":
            text = (
                "NHẦY TẦM OPTIMION\n\n"
                "Đã chọn chức năng:\n"
                "NHẦY TẦM OPTIMION\n\n"
                "Nhấn XÁC NHẬN để hoàn tất."
            )
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=function_keyboard(confirm_enabled=True)
            )
            bot.answer_callback_query(call.id, "Đã chọn chức năng")
            return

        # --- BƯỚC 3: XÁC NHẬN ---
        if call.data == "confirm_func":
            text = (
                "VC | HOÀN TẤT\n\n"
                "Xác nhận thành công!\n\n"
                "UDID: Đã xác nhận thủ công\n"
                "Chức năng: NHẦY TẦM OPTIMION\n"
                "Trạng thái: HOÀN TẤT"
            )
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=None
            )
            bot.answer_callback_query(call.id, "Hoàn tất")
            return

        # --- BẤM XÁC NHẬN KHI CHƯA CHỌN ---
        if call.data in ("confirm_disabled",):
            bot.answer_callback_query(
                call.id,
                "Bạn chưa chọn chức năng!",
                show_alert=True
            )
            return

        bot.answer_callback_query(call.id)

    except Exception as e:
        print(f"[Callback Error] {e}")
        try:
            bot.answer_callback_query(call.id, "Có lỗi xảy ra")
        except:
            pass


# =================================
# FALLBACK
# =================================

@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.reply_to(
        message,
        "Dùng /start hoặc /setup để mở menu."
    )


# =================================
# RUN
# =================================

if __name__ == "__main__":
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise SystemExit("Chưa nhập BOT_TOKEN!")

    print("==============================")
    print("VC UDID VERIFY - TELEGRAM")
    print("STATUS: ONLINE")
    print("==============================")
    bot.infinity_polling(timeout=30, long_polling_timeout=20)