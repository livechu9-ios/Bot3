# -*- coding: utf-8 -*-
"""
Bot_defrom - Telegram Bot (bản không emoji)
Admin: @livechu2004
"""

import telebot
from telebot import types
import hashlib
import os
import json

# ============ CẤU HÌNH ============
BOT_TOKEN = "9093083128:AAEN_pqXRabqdnRK159MXy2nN6tngpdu9J8"   # <-- Thay token bot của bạn
ADMIN_USERNAME = "@livechu2004"
BANK_NAME = "ZALOPLAY"
BANK_STK = "0935742761"
BANK_NAME_OWNER = "Nguyễn Thị Út"
BANK_CONTENT = "livechu dep trai zo xinh gai"
UDID_LINK = "udid.tech"

PRICE = "50.000vnđ"
SECRET_SALT = "BotDefromSecretKey2024"

KEY_FILE = "used_keys.json"

bot = telebot.TeleBot(BOT_TOKEN)

# ============ QUẢN LÝ KEY ============
def load_used_keys():
    if os.path.exists(KEY_FILE):
        try:
            with open(KEY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_used_keys(keys):
    with open(KEY_FILE, "w", encoding="utf-8") as f:
        json.dump(keys, f, ensure_ascii=False, indent=2)

def validate_key(key_input):
    try:
        parts = key_input.upper().split("-")
        if len(parts) != 4:
            return False
        if parts[0] != "BD":
            return False
        raw = "-".join(parts[:3])
        expected = hashlib.md5((raw + SECRET_SALT).encode()).hexdigest()[:4].upper()
        return expected == parts[3]
    except:
        return False

# ============ MENU ============
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("Cửa Hàng"),
        types.KeyboardButton("Nạp Tiền"),
        types.KeyboardButton("Nhập Udid"),
        types.KeyboardButton("Key"),
    )
    return markup

WELCOME = (
    "—————————————\n"
    "Chào Mừng Bạn\n"
    "Đã Đến Với Bot_defrom\n"
    f"admin : {ADMIN_USERNAME}\n"
    "—————————————\n"
    "Cửa Hàng | Nạp Tiền | Nhập Udid | Key\n"
    "—————————————\n"
    "Bấm vào nút bên dưới để xem chi tiết."
)

# Nội dung từng mục (hiện ngay, không cần bấm thêm)
SHOP_TEXT = (
    "—————————————\n"
    "CỬA HÀNG BOT_DEFROM\n"
    "—————————————\n"
    "Sản phẩm: Trick Aim\n"
    f"Giá: {PRICE}\n\n"
    "Để mua:\n"
    "1. Nạp tiền theo mục Nạp Tiền\n"
    "2. Gửi bill cho admin\n"
    "3. Nhận mã Key\n"
    "4. Nhập key bằng lệnh: /key BD-XXXX-XXXX-XXXX\n\n"
    f"Liên hệ: {ADMIN_USERNAME}"
)

NAP_TEXT = (
    "—————————————\n"
    "NẠP TIỀN\n"
    "—————————————\n"
    f"NGÂN HÀNG : {BANK_NAME}\n"
    f"SỐ TÀI KHOẢN : {BANK_STK}\n"
    f"Chủ Tài Khoản : {BANK_NAME_OWNER}\n"
    f"Nội dung ck : {BANK_CONTENT}\n"
    "—————————————\n"
    f"Sau khi chuyển khoản, gửi bill cho {ADMIN_USERNAME}"
)

UDID_TEXT = (
    "—————————————\n"
    "NHẬP UDID\n"
    "—————————————\n"
    f"Link : {UDID_LINK}\n\n"
    "Các bước:\n"
    "1. Tải\n"
    "2. Cho phép\n"
    "3. Đóng\n"
    "4. Cài đặt hồ sơ\n"
    "5. Cài đặt\n\n"
    "Lấy mã udid : 0000000-00000-00\n\n"
    "Sau khi có UDID, gửi lại bằng lệnh:\n"
    "/udid 0000000-00000-00"
)

KEY_TEXT = (
    "—————————————\n"
    "KEY KÍCH HOẠT\n"
    "—————————————\n"
    f"Giá: {PRICE}\n\n"
    f"Liên hệ shop để đưa và giao dịch: {ADMIN_USERNAME}\n\n"
    "Sau khi có key, nhập bằng lệnh:\n"
    "/key BD-XXXX-XXXX-XXXX"
)

# ============ COMMAND ============
@bot.message_handler(commands=["start", "menu"])
def cmd_start(message):
    bot.send_message(message.chat.id, WELCOME, reply_markup=main_menu())

@bot.message_handler(commands=["help"])
def cmd_help(message):
    bot.send_message(
        message.chat.id,
        "HƯỚNG DẪN\n\n"
        "Cửa Hàng - Mua Trick Aim (50.000vnđ)\n"
        "Nạp Tiền - Chuyển khoản ZALOPLAY\n"
        "Nhập Udid - Lấy mã UDID tại udid.tech\n"
        "Key - Nhập key đã mua\n\n"
        f"Liên hệ: {ADMIN_USERNAME}",
        reply_markup=main_menu()
    )

# ============ XỬ LÝ NÚT BẤM ============
@bot.message_handler(func=lambda m: m.text == "Cửa Hàng")
def btn_shop(message):
    bot.send_message(message.chat.id, SHOP_TEXT)

@bot.message_handler(func=lambda m: m.text == "Nạp Tiền")
def btn_nap(message):
    bot.send_message(message.chat.id, NAP_TEXT)

@bot.message_handler(func=lambda m: m.text == "Nhập Udid")
def btn_udid(message):
    bot.send_message(message.chat.id, UDID_TEXT)

@bot.message_handler(func=lambda m: m.text == "Key")
def btn_key(message):
    bot.send_message(message.chat.id, KEY_TEXT)

# ============ XỬ LÝ KEY ============
@bot.message_handler(commands=["key"])
def cmd_key(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "Cú pháp: /key BD-XXXX-XXXX-XXXX")
        return
    key = args[1].strip().upper()
    used = load_used_keys()

    if key in used:
        bot.reply_to(message, "Key này đã được sử dụng rồi.")
        return

    if validate_key(key):
        used.append(key)
        save_used_keys(used)
        bot.reply_to(
            message,
            "KÍCH HOẠT THÀNH CÔNG\n"
            f"Key: {key}\n\n"
            "Admin sẽ liên hệ gửi file trong ít phút.\n"
            f"{ADMIN_USERNAME}"
        )
        try:
            bot.send_message(
                message.chat.id,
                f"Người dùng {message.from_user.id} vừa kích hoạt key:\n{key}"
            )
        except:
            pass
    else:
        bot.reply_to(
            message,
            "Key không hợp lệ.\n\n"
            f"Vui lòng liên hệ shop: {ADMIN_USERNAME}"
        )

# ============ XỬ LÝ UDID ============
@bot.message_handler(commands=["udid"])
def cmd_udid(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(
            message,
            "Cú pháp: /udid 0000000-00000-00\n"
            f"Lấy UDID tại: {UDID_LINK}"
        )
        return
    udid = args[1].strip()
    bot.reply_to(
        message,
        "ĐÃ NHẬN UDID\n"
        f"UDID: {udid}\n\n"
        "Admin sẽ xử lý và phản hồi sớm nhất.\n"
        f"{ADMIN_USERNAME}"
    )

# ============ FALLBACK ============
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.reply_to(
        message,
        "Dùng /start để mở menu chính.\n"
        f"Admin: {ADMIN_USERNAME}",
        reply_markup=main_menu()
    )

# ============ CHẠY ============
if __name__ == "__main__":
    print("=" * 40)
    print("Bot_defrom đang khởi động...")
    print(f"Admin: {ADMIN_USERNAME}")
    print("=" * 40)
    bot.infinity_polling(timeout=30, long_polling_timeout=20)