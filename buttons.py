from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


# ===== REPLY KEYBOARDS =====

def user_main_keyboard():
    keyboard = [
        [KeyboardButton("🎬 Kino izlash"), KeyboardButton("🎨 Multfilm izlash")],
        [KeyboardButton("💎 Premium"), KeyboardButton("📊 Premium muddati")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def admin_keyboard():
    keyboard = [
        [KeyboardButton("🎬 Kino yuklash"), KeyboardButton("🎨 Multfilm yuklash")],
        [KeyboardButton("💎 Premium kino"), KeyboardButton("💎 Premium multfilm")],
        [KeyboardButton("🔍 Kino izlash"), KeyboardButton("🔎 Multfilm izlash")],
        [KeyboardButton("🗑 Kino o'chirish"), KeyboardButton("🗑 Multfilm o'chirish")],
        [KeyboardButton("📊 Statistika"), KeyboardButton("📢 Xabar yuborish")],
        [KeyboardButton("⚙️ Kanallar"), KeyboardButton("💎 Premium panel")],
        [KeyboardButton("💎 Premium panel"), KeyboardButton("👥 Foydalanuvchilar")],
        [KeyboardButton("🎬 Kino tugmalari")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def channels_keyboard():
    keyboard = [
        [KeyboardButton("➕ Kanal qo'shish")],
        [KeyboardButton("📋 Kanallar ro'yxati"), KeyboardButton("🗑 Kanal o'chirish")],
        [KeyboardButton("🔙 Orqaga")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def back_keyboard():
    keyboard = [[KeyboardButton("🔙 Orqaga")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ===== INLINE KEYBOARDS =====

def subscription_keyboard(channels):
    keyboard = []
    for ch in channels:
        ch_type = ch[4] if len(ch) > 4 else 'telegram'
        icon = "📸" if ch_type == 'instagram' else "📢"
        keyboard.append([InlineKeyboardButton(f"{icon} {ch[2]}", url=ch[3])])
    keyboard.append([InlineKeyboardButton("💎 Premium sotib olish", callback_data="premium_info")])
    keyboard.append([InlineKeyboardButton("♻️ Tekshirish", callback_data="check_sub")])
    return InlineKeyboardMarkup(keyboard)


def add_channel_type_keyboard():
    keyboard = [
        [InlineKeyboardButton("📢 Telegram kanal", callback_data="add_ch_telegram")],
        [InlineKeyboardButton("📸 Instagram akkaunt", callback_data="add_ch_instagram")]
    ]
    return InlineKeyboardMarkup(keyboard)


def premium_prices_keyboard():
    keyboard = [
        [InlineKeyboardButton("1 oylik - 3000 so'm", callback_data="premium_1")],
        [InlineKeyboardButton("3 oylik - 9000 so'm", callback_data="premium_3")],
        [InlineKeyboardButton("6 oylik - 18000 so'm", callback_data="premium_6")],
        [InlineKeyboardButton("12 oylik - 36000 so'm", callback_data="premium_12")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def payment_confirm_keyboard(payment_id):
    keyboard = [
        [InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_{payment_id}")],
        [InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{payment_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)


def premium_panel_keyboard():
    keyboard = [
        [InlineKeyboardButton("1 oylik", callback_data="premium_list_1"),
         InlineKeyboardButton("3 oylik", callback_data="premium_list_3")],
        [InlineKeyboardButton("6 oylik", callback_data="premium_list_6"),
         InlineKeyboardButton("12 oylik", callback_data="premium_list_12")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_admin")]
    ]
    return InlineKeyboardMarkup(keyboard)


def back_inline_keyboard():
    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_main")]]
    return InlineKeyboardMarkup(keyboard)


def cartoon_delete_confirm_keyboard(code):
    keyboard = [
        [InlineKeyboardButton("🗑 Ha, o'chirish", callback_data=f"del_cartoon_{code}")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_admin")]
    ]
    return InlineKeyboardMarkup(keyboard)



def movie_delete_confirm_keyboard(code):
    keyboard = [
        [InlineKeyboardButton("🗑 Ha, o'chirish", callback_data=f"del_movie_{code}")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_admin")]
    ]
    return InlineKeyboardMarkup(keyboard)

def video_inline_keyboard(kino_channel):
    row = [InlineKeyboardButton("📤 Dostlarga ulashish", switch_inline_query="")]
    if kino_channel:
        row.append(InlineKeyboardButton("📢 Kanalimiz", url=kino_channel[1]))
    return InlineKeyboardMarkup([row])


def kino_tugmalari_keyboard():
    keyboard = [[InlineKeyboardButton("📢 Kanalimiz", callback_data="kino_ch_menu")]]
    return InlineKeyboardMarkup(keyboard)


def kino_channel_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("➕ Kanal qo'shish", callback_data="kino_ch_add")],
        [InlineKeyboardButton("🗑 Kanal o'chirish", callback_data="kino_ch_delete")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_admin")]
    ]
    return InlineKeyboardMarkup(keyboard)


def kino_channel_delete_keyboard(channel):
    keyboard = [
        [InlineKeyboardButton(f"🗑 {channel[2]} — o'chirish", callback_data="kino_ch_confirm_delete")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="kino_ch_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Bot mashhudev tomonidan yaratildi izohlar yaxshiroq tushunishiz uchunn yozil