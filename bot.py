import telebot
from telebot import types
import json
import os
from datetime import datetime

bot = telebot.TeleBot("7545229622:AAFnoS4kGYV_5RYmz2D-s3NlhvbevrSBJBc")

ADMIN_PASSWORD = "KaguyaMLB"
ADMIN_USERNAME = "@Kaguya_MLB"
ADMIN_ID = 1936795754

USERS_FILE = "users.json"
CHANNELS_FILE = "channels.json"
SHOT_FILE = "shot_requests.json"  # SHOT so‘rovlari fayli

def load_json(filename):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump({}, f)
    with open(filename, "r") as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def get_today():
    return datetime.now().strftime("%Y-%m-%d")

@bot.message_handler(commands=['start'])
def start(msg):
    users = load_json(USERS_FILE)
    user_id = str(msg.chat.id)

    args = msg.text.split()
    ref_id = args[1] if len(args) > 1 else None

    if user_id not in users:
        users[user_id] = {
            "username": msg.from_user.username if msg.from_user.username else "Noma'lum",
            "balance": 0,
            "last_date": "",
            "done_channels": [],
            "invited_by": ref_id
        }
        save_json(USERS_FILE, users)

        # Agar kimdir sizning referral link orqali kelsa
        if ref_id and ref_id in users:
            users[ref_id]["balance"] += 100
            save_json(USERS_FILE, users)
            try:
                bot.send_message(int(ref_id), f"🎉 Siz TAKLIF qilgan odam botga /start bosdi, sizga 100 so‘m qo‘shildi!")
            except Exception:
                pass

    # Asosiy menyu va xush kelibsiz xabari
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📋 Topshiriqlar"),
        types.KeyboardButton("💰 Balansim"),
        types.KeyboardButton("💸 SHOT"),
        types.KeyboardButton("👥 Do‘st taklif qilish"),
        types.KeyboardButton("📞 Admin bilan bog‘lanish"),
        types.KeyboardButton("📊 Statistika")
    )

    welcome_text = (
        "🎉 Botga xush kelibsiz!\n"
        "Har kuni 5 ta kanalga obuna bo‘ling va pul ishlang.\n"
        "Balansingiz 20,000 so‘m bo‘lsa, SHOT orqali yechib olishingiz mumkin."
    )
    bot.send_message(msg.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📋 Topshiriqlar")
def tasks(msg):
    user_id = str(msg.chat.id)
    users = load_json(USERS_FILE)
    today = get_today()

    if user_id in users and users[user_id]["last_date"] == today:
        bot.send_message(msg.chat.id, "✅ Siz bugungi topshiriqlarni allaqachon bajargansiz.")
        return

    channels = load_json(CHANNELS_FILE)
    channels_today = channels.get(today, ["Tg_Gift_Premium", "StickShop_uz", "Amaterasu_store_uz", "About_me_Madinaa"])

    markup = types.InlineKeyboardMarkup()
    for ch in channels_today:
        markup.add(types.InlineKeyboardButton(text=ch, url=f"https://t.me/{ch}"))
    markup.add(types.InlineKeyboardButton("✅ Tekshirish", callback_data="check"))

    bot.send_message(msg.chat.id, "Quyidagi kanallarga obuna bo‘ling:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_subscription(call):
    user_id = str(call.message.chat.id)
    users = load_json(USERS_FILE)
    today = get_today()

    if users.get(user_id, {}).get("last_date") == today:
        bot.send_message(call.message.chat.id, "✅ Siz bugungi topshiriqlarni allaqachon bajargansiz.")
        return

    channels = load_json(CHANNELS_FILE)
    channels_today = channels.get(today, ["Tg_Gift_Premium", "StickShop_uz", "Amaterasu_store_uz", "About_me_Madinaa"])

    joined_count = 0
    for ch in channels_today:
        try:
            member = bot.get_chat_member(f"@{ch}", call.message.chat.id)
            if member.status in ['member', 'administrator', 'creator']:
                joined_count += 1
        except Exception:
            continue

    if joined_count > 0:
        total_earnings = min(joined_count * 100, 500)
        users[user_id]["balance"] += total_earnings
        users[user_id]["last_date"] = today
        save_json(USERS_FILE, users)

        # Taklif qilgan odamga yana 100 so‘m beramiz
        inviter = users[user_id].get("invited_by")
        if inviter and inviter in users:
            users[inviter]["balance"] += 100
            save_json(USERS_FILE, users)
            try:
                bot.send_message(int(inviter), f"🎉 Siz TAKLIF qilgan odam botga TOPSHIRIQLARNI bajardi, sizga 100 so‘m qo‘shildi!")
            except Exception:
                pass

        bot.send_message(call.message.chat.id, f"✅ Tekshiruv muvaffaqiyatli! {total_earnings} so‘m balansingizga qo‘shildi.")
    else:
        bot.send_message(call.message.chat.id, "❌ Hech bir kanallarga obuna bo‘lmagansiz.")

@bot.message_handler(func=lambda m: m.text == "💰 Balansim")
def show_balance(msg):
    users = load_json(USERS_FILE)
    user_id = str(msg.chat.id)
    balance = users.get(user_id, {}).get("balance", 0)
    bot.send_message(msg.chat.id, f"💳 Sizning balansingiz: {balance} so‘m")

@bot.message_handler(func=lambda m: m.text == "💸 SHOT")
def payout(msg):
    users = load_json(USERS_FILE)
    user_id = str(msg.chat.id)
    balance = users.get(user_id, {}).get("balance", 0)
    if balance >= 20000:
        users[user_id]["balance"] = 0
        save_json(USERS_FILE, users)

        # SHOT so‘rovini faylga yozamiz
        shot_requests = load_json(SHOT_FILE)
        shot_requests[user_id] = {
            "username": msg.from_user.username if msg.from_user.username else "Noma'lum",
            "chat_id": msg.chat.id,
            "date": get_today()
        }
        save_json(SHOT_FILE, shot_requests)

        bot.send_message(msg.chat.id, "✅ SHOT so‘rovingiz qabul qilindi. Tez orada siz bilan bog‘lanamiz.")
        bot.send_message(ADMIN_ID, f"💸 @{msg.from_user.username if msg.from_user.username else "Noma'lum" SHOT so‘radi! Telegram ID: {msg.chat.id}")

    else:
        bot.send_message(msg.chat.id, "❌ SHOT uchun kamida 20 000 so‘m kerak.")

@bot.message_handler(commands=['admin'])
def admin_panel(msg):
    if msg.chat.id != ADMIN_ID:
        bot.send_message(msg.chat.id, "❌ Sizda bu buyruqdan foydalanish huquqi yo‘q.")
        return
    bot.send_message(msg.chat.id, "🔐 Parolni kiriting:")
    bot.register_next_step_handler(msg, check_admin_password)

def check_admin_password(msg):
    if msg.text == ADMIN_PASSWORD and msg.chat.id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📊 Statistika", "📤 Pul so‘rovlari", "📋 Kanallarni yangilash")
        bot.send_message(msg.chat.id, "✅ Admin paneliga xush kelibsiz!", reply_markup=markup)
    else:
        bot.send_message(msg.chat.id, "❌ Noto‘g‘ri parol yoki ruxsat yo‘q.")

@bot.message_handler(func=lambda m: m.text == "📋 Kanallarni yangilash")
def add_channels(msg):
    if msg.chat.id != ADMIN_ID:
        bot.send_message(msg.chat.id, "❌ Sizda bu buyruqdan foydalanish huquqi yo‘q.")
        return
    bot.send_message(msg.chat.id, "📥 Yangi kanallarni vergul bilan yuboring:")
    bot.register_next_step_handler(msg, save_channels)

def save_channels(msg):
    today = get_today()
    channels = load_json(CHANNELS_FILE)
    new_channels = [x.strip().replace("@", "") for x in msg.text.split(",") if x.strip()]
    channels[today] = new_channels
    save_json(CHANNELS_FILE, channels)
    bot.send_message(msg.chat.id, f"✅ {len(new_channels)} ta kanal bugun uchun qo‘shildi.")

@bot.message_handler(func=lambda m: m.text == "👥 Do‘st taklif qilish")
def invite_friends(msg):
    user_id = str(msg.chat.id)
    invite_link = f"https://t.me/Birgalikda_pul_ishlaymiz_bot?start={user_id}"
    text = (
        "Siz do‘stingizni taklif qilsangiz va u /startni bossa sizga 100 so‘m beriladi.\n"
        "Agar u TOPSHIRIQLARni bajarsa yana sizga 100 so‘m beriladi.\n\n"
        f"Do‘stlaringizni quyidagi havola orqali taklif qiling:\n{invite_link}"
    )
    bot.send_message(msg.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "📞 Admin bilan bog‘lanish")
def contact_admin(msg):
    bot.send_message(msg.chat.id, f"📞 Iltimos, quyidagi admin bilan bog‘laning: {ADMIN_USERNAME}")

@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def show_stats(msg):
    if msg.chat.id != ADMIN_ID:
        bot.send_message(msg.chat.id, "❌ Sizda bu buyruqdan foydalanish huquqi yo‘q.")
        return

    users = load_json(USERS_FILE)
    total_users = len(users)
    today = get_today()
    done_today = sum(1 for u in users.values() if u.get("last_date") == today)

    shot_requests = load_json(SHOT_FILE)
    shot_count = len(shot_requests)

    bot.send_message(msg.chat.id,
        f"📊 Statistika:\n"
        f"👥 Jami foydalanuvchilar: {total_users}\n"
        f"✅ Bugun topshiriq bajarganlar: {done_today}\n"
        f"💸 SHOT so‘rovlari: {shot_count} ta"
    )

@bot.message_handler(func=lambda m: m.text == "📤 Pul so‘rovlari")
def show_payout_requests(msg):
    if msg.chat.id != ADMIN_ID:
        bot.send_message(msg.chat.id, "❌ Sizda bu buyruqdan foydalanish huquqi yo‘q.")
        return

    shot_requests = load_json(SHOT_FILE)
    if not shot_requests:
        bot.send_message(msg.chat.id, "📭 Hozircha hech qanday SHOT so‘rovlari yo‘q.")
        return

    text = "📤 SHOT so‘rovlari:\n\n"
    for uid, info in shot_requests.items():
        text += f"👤 @{info.get('username', 'Nomaʼlum')}\n🆔 ID: {uid}\n📅 Sana: {info['date']}\n\n"

    bot.send_message(msg.chat.id, text)

print("✅ Bot ishga tushdi...")
bot.polling(none_stop=True)
# Pul-TG
