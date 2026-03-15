from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from datetime import datetime
import database as db
import buttons as btn

BOT_TOKEN = "8633402479:AAG97j-H9eunW78fbxGa5jbaGncEhC0g_dU"
ADMIN_ID = 7945500144
CARD_NUMBER = "9860 2301 0344 2953"

# ============================================================
# YORDAMCHI FUNKSIYALAR
# ============================================================
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

async def get_unsubscribed_channels(user_id: int, context) -> list:
    """Foydalanuvchi obuna bo'lmagan FAQAT Telegram kanallar ro'yxatini qaytaradi."""
    channels = db.get_all_channels()
    if not channels:
        return []
    unsubscribed = []
    for ch in channels:
        ch_type = ch[4] if len(ch) > 4 else 'telegram'
        if ch_type != 'telegram':
            continue
        channel_id = ch[1]
        try:
            member = await context.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status in ['left', 'kicked']:
                unsubscribed.append(ch)
        except Exception as e:
            print(f"[XATO] {channel_id} tekshirishda: {e}")
            unsubscribed.append(ch)
    return unsubscribed

def get_instagram_channels() -> list:
    """Barcha Instagram kanallarni qaytaradi."""
    all_channels = db.get_all_channels()
    return [ch for ch in all_channels if (ch[4] if len(ch) > 4 else 'telegram') == 'instagram']

async def get_channels_to_show(user_id: int, context) -> list:
    """
    Qoidasi:
    - Agar Telegram kanalga obuna bo'lmagan bo'lsa:
        Telegram (obuna bo'lmaganlar) + Instagram birga ko'rsatiladi
    - Agar barcha Telegram kanallarga obuna bo'lgan bo'lsa:
        Hech narsa ko'rsatilmaydi (Instagram ham chiqmaydi)
    """
    unsubscribed_telegram = await get_unsubscribed_channels(user_id, context)
    if unsubscribed_telegram:
        # Telegram OK emas → Telegram + Instagram ko'rsatamiz
        instagram_channels = get_instagram_channels()
        return unsubscribed_telegram + instagram_channels
    else:
        # Barcha Telegram kanallarga obuna → hech narsa ko'rsatmaymiz
        return []

async def send_video_with_buttons(update: Update, file_id: str, caption: str):
    """Video + tagida tugmalar"""
    kino_ch = db.get_kino_channel()
    keyboard = btn.video_inline_keyboard(kino_ch)
    await update.message.reply_video(video=file_id, caption=caption, reply_markup=keyboard)

# ============================================================
# /start KOMANDASI
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    db.add_user(user_id, user.username or "Yo'q", user.first_name, user.last_name or "")

    # --- ADMIN ---
    if is_admin(user_id):
        await update.message.reply_text(
            f"👋 Salom Admin!\n\n"
            f"👥 Foydalanuvchilar: {db.get_users_count()}\n"
            f"🎬 Kinolar: {db.get_movies_count()} | 💎 Premium: {db.get_premium_movies_count()}\n"
            f"🎨 Multfilmlar: {db.get_cartoons_count()} | 💎 Premium: {db.get_premium_cartoons_count()}\n"
            f"💎 Premium obunchilar: {len(db.get_premium_users())}",
            reply_markup=btn.admin_keyboard()
        )
        return

    # --- ODDIY FOYDALANUVCHI ---
    is_premium = db.check_premium_status(user_id)
    if not is_premium:
        channels_to_show = await get_channels_to_show(user_id, context)
        if channels_to_show:
            await update.message.reply_text(
                f"👋 Salom {user.first_name}!\n\n"
                "⚠️ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
                reply_markup=btn.subscription_keyboard(channels_to_show)
            )
            return

    await update.message.reply_text(
        f"🎬 Salom {user.first_name}!\n\n"
        f"👥 Foydalanuvchilar: {db.get_users_count()}\n"
        f"🎬 Kinolar: {db.get_movies_count()}\n"
        f"🎨 Multfilmlar: {db.get_cartoons_count()}",
        reply_markup=btn.user_main_keyboard()
    )

# ============================================================
# CALLBACK HANDLER
# ============================================================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    # ── HAR QANDAY CALLBACK DA OBUNA TEKSHIRISH ───────────────
    skip_check = (
        is_admin(user_id)
        or data in ("check_sub", "premium_info", "back_to_main", "back_admin")
        or data.startswith("premium_")
        or data.startswith("approve_")
        or data.startswith("reject_")
        or data.startswith("add_ch_")
        or data.startswith("kino_ch")
    )

    if not skip_check:
        is_premium = db.check_premium_status(user_id)
        if not is_premium:
            channels_to_show = await get_channels_to_show(user_id, context)
            if channels_to_show:
                try:
                    await query.message.delete()
                except Exception:
                    pass
                await context.bot.send_message(
                    chat_id=user_id,
                    text="⚠️ Siz quyidagi kanallardan chiqib ketgansiz!\n\nBotdan foydalanish uchun qaytadan obuna bo'ling.",
                    reply_markup=btn.subscription_keyboard(channels_to_show)
                )
                return

    # ── OBUNA TEKSHIRISH TUGMASI ──────────────────────────────
    if data == "check_sub":
        if db.check_premium_status(user_id):
            try:
                await query.message.delete()
            except Exception:
                pass
            await context.bot.send_message(
                chat_id=user_id,
                text="✅ Sizda Premium bor! Botdan erkin foydalaning.",
                reply_markup=btn.user_main_keyboard()
            )
            return

        # Faqat Telegram tekshiriladi
        unsubscribed_telegram = await get_unsubscribed_channels(user_id, context)
        if not unsubscribed_telegram:
            # ✅ Barcha Telegram OK → kirish ruxsati, Instagram ham chiqmaydi
            try:
                await query.message.delete()
            except Exception:
                pass
            await context.bot.send_message(
                chat_id=user_id,
                text="✅ Obuna tasdiqlandi! Botdan foydalanishingiz mumkin.",
                reply_markup=btn.user_main_keyboard()
            )
        else:
            # ❌ Hali Telegram kanalga obuna bo'lmagan → Telegram + Instagram ko'rsatamiz
            channels_to_show = unsubscribed_telegram + get_instagram_channels()
            try:
                await query.message.edit_text(
                    "❌ Hali quyidagi kanallarga obuna bo'lmadingiz!\n"
                    "Obuna bo'lgach '♻️ Tekshirish' tugmasini bosing.",
                    reply_markup=btn.subscription_keyboard(channels_to_show)
                )
            except Exception:
                pass

    # ── PREMIUM INFO ───────────────────────────────────────────
    elif data == "premium_info":
        await query.message.edit_text(
            "💎 Premium obuna\n\n"
            "✅ Kanallarga obuna bo'lmasdan foydalanish\n"
            "✅ Maxsus premium kino va multfilmlarga kirish\n\n"
            "💰 Narxlar:",
            reply_markup=btn.premium_prices_keyboard()
        )

    # ── PREMIUM NARX TANLASH ───────────────────────────────────
    elif data.startswith("premium_") and not data.startswith("premium_list_"):
        parts = data.split("_")
        if len(parts) == 2 and parts[1].isdigit():
            month = int(parts[1])
            prices = {1: 3000, 3: 9000, 6: 18000, 12: 36000}
            price = prices.get(month, 3000)
            context.user_data['premium_months'] = month
            context.user_data['premium_price'] = price
            context.user_data['waiting_receipt'] = True
            await query.message.edit_text(
                f"💳 To'lov ma'lumotlari\n\n"
                f"💳 Karta raqami: {CARD_NUMBER}\n"
                f"💰 Narx: {price} so'm\n"
                f"📅 Muddat: {month} oy\n\n"
                f"📸 To'lovni amalga oshirib, chek rasmini yuboring:",
                reply_markup=btn.back_inline_keyboard()
            )

    # ── TO'LOV TASDIQLASH (ADMIN) ──────────────────────────────
    elif data.startswith("approve_"):
        if not is_admin(user_id):
            await query.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        payment_id = int(data.split("_")[1])
        payment = db.get_payment(payment_id)
        if payment:
            db.approve_payment(payment_id)
            await context.bot.send_message(
                chat_id=payment[1],
                text=f"🎉 Tabriklaymiz! Premium faollashtirildi!\n\n"
                     f"📅 Muddat: {payment[2]} oy\n"
                     f"💰 To'langan: {payment[3]} so'm\n\n"
                     f"Endi barcha premium kino va multfilmlardan bahramand bo'ling! 🎬",
                reply_markup=btn.user_main_keyboard()
            )
            await query.message.edit_text("✅ To'lov tasdiqlandi va premium berildi!")
        else:
            await query.message.edit_text("❌ To'lov topilmadi!")

    # ── TO'LOV RAD ETISH (ADMIN) ───────────────────────────────
    elif data.startswith("reject_"):
        if not is_admin(user_id):
            await query.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        payment_id = int(data.split("_")[1])
        payment = db.get_payment(payment_id)
        if payment:
            db.reject_payment(payment_id)
            await context.bot.send_message(
                chat_id=payment[1],
                text="❌ To'lovingiz rad etildi.\n\nIltimos, to'g'ri chek yuboring yoki admin bilan bog'laning."
            )
            await query.message.edit_text("❌ To'lov rad etildi!")

    # ── PREMIUM PANEL RO'YXAT (ADMIN) ─────────────────────────
    elif data.startswith("premium_list_"):
        if not is_admin(user_id):
            await query.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        months = int(data.split("_")[2])
        users = db.get_premium_users_by_months(months)
        if not users:
            await query.message.edit_text(
                f"❌ {months} oylik premium foydalanuvchilar topilmadi.",
                reply_markup=btn.premium_panel_keyboard()
            )
            return
        text = f"💎 {months} oylik Premium foydalanuvchilar ({len(users)} ta):\n\n"
        for idx, u in enumerate(users, 1):
            try:
                end_dt = datetime.strptime(u[3], "%Y-%m-%d %H:%M:%S")
                days_left = (end_dt - datetime.now()).days
                end_str = end_dt.strftime('%d.%m.%Y')
            except Exception:
                days_left = 0
                end_str = "Noma'lum"
            uname = f"@{u[1]}" if u[1] and u[1] != "Yo'q" else "Username yo'q"
            text += (
                f"{idx}. 👤 {u[2]} ({uname})\n"
                f"   ⏰ {days_left} kun qoldi | 📅 {end_str}\n\n"
            )
        await query.message.edit_text(text, reply_markup=btn.premium_panel_keyboard())

    # ── MULTFILM O'CHIRISH TASDIQLASH ─────────────────────────
    elif data.startswith("del_cartoon_"):
        if not is_admin(user_id):
            return
        code = data.replace("del_cartoon_", "")
        db.delete_cartoon(code)
        await query.message.edit_text(f"✅ '{code}' kodli multfilm muvaffaqiyatli o'chirildi!")

    elif data.startswith("del_movie_"):
        if not is_admin(user_id):
            return
        code = data.replace("del_movie_", "")
        db.delete_movie(code)
        await query.message.edit_text(f"✅ '{code}' kodli kino muvaffaqiyatli o'chirildi!")

    # ── KANAL QO'SHISH TURI ───────────────────────────────────
    elif data == "add_ch_telegram":
        if not is_admin(user_id):
            return
        context.user_data.clear()
        context.user_data['channel_type'] = 'telegram'
        context.user_data['channel_step'] = 'name'
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text="📝 Telegram kanal nomini kiriting:",
            reply_markup=btn.back_keyboard()
        )

    elif data == "add_ch_instagram":
        if not is_admin(user_id):
            return
        context.user_data.clear()
        context.user_data['channel_type'] = 'instagram'
        context.user_data['channel_step'] = 'instagram_name'
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text="📝 Instagram akkaunt nomini kiriting:",
            reply_markup=btn.back_keyboard()
        )

    # ── KINO TUGMALARI ────────────────────────────────────────
    elif data == "kino_ch_menu":
        if not is_admin(user_id):
            return
        kino_ch = db.get_kino_channel()
        info = f"\n\n📢 Hozirgi kanal: {kino_ch[2]}\n🔗 {kino_ch[1]}" if kino_ch else "\n\n❌ Hozircha kanal qo'shilmagan"
        await query.message.edit_text(
            f"📢 Kanalimiz boshqaruvi{info}",
            reply_markup=btn.kino_channel_menu_keyboard()
        )

    elif data == "kino_ch_add":
        if not is_admin(user_id):
            return
        context.user_data.clear()
        context.user_data['kino_ch_add'] = True
        context.user_data['kino_ch_step'] = 'link'
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text="🔗 Kanal linkini yoki @username kiriting:\n\nMisol: https://t.me/kanalim yoki @kanalim",
            reply_markup=btn.back_keyboard()
        )

    elif data == "kino_ch_delete":
        if not is_admin(user_id):
            return
        kino_ch = db.get_kino_channel()
        if not kino_ch:
            await query.message.edit_text(
                "❌ Hech qanday kanal qo'shilmagan!",
                reply_markup=btn.kino_channel_menu_keyboard()
            )
            return
        await query.message.edit_text(
            f"⚠️ Quyidagi kanalni o'chirishni tasdiqlaysizmi?\n\n📢 {kino_ch[2]}\n🔗 {kino_ch[1]}",
            reply_markup=btn.kino_channel_delete_keyboard(kino_ch)
        )

    elif data == "kino_ch_confirm_delete":
        if not is_admin(user_id):
            return
        db.delete_kino_channel()
        await query.message.edit_text("✅ Kanal o'chirildi!")

    # ── ORQAGA ────────────────────────────────────────────────
    elif data == "back_to_main":
        context.user_data.clear()
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "back_admin":
        context.user_data.clear()
        try:
            await query.message.delete()
        except Exception:
            pass

# ============================================================
# ASOSIY XABAR HANDLER
# ============================================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_admin(user_id):
        await handle_admin(update, context)
    else:
        await handle_user(update, context)

# ============================================================
# FOYDALANUVCHI HANDLERI
# ============================================================
async def handle_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    is_premium = db.check_premium_status(user_id)

    if not is_premium:
        channels_to_show = await get_channels_to_show(user_id, context)
        if channels_to_show:
            await update.message.reply_text(
                "⚠️ Siz quyidagi kanallardan chiqib ketgansiz!\n\n"
                "Obuna bo'lgach '♻️ Tekshirish' tugmasini bosing.",
                reply_markup=btn.subscription_keyboard(channels_to_show)
            )
            return

    if text == "🎬 Kino izlash":
        context.user_data.clear()
        context.user_data['search_type'] = 'movie'
        await update.message.reply_text(
            "🔍 Kino kodini kiriting:",
            reply_markup=btn.back_keyboard()
        )

    elif text == "🎨 Multfilm izlash":
        context.user_data.clear()
        context.user_data['search_type'] = 'cartoon'
        await update.message.reply_text(
            "🔍 Multfilm kodini kiriting:",
            reply_markup=btn.back_keyboard()
        )

    elif text == "💎 Premium":
        await update.message.reply_text(
            "💎 Premium obuna\n\n"
            "✅ Kanallarga obuna bo'lmasdan foydalanish\n"
            "✅ Maxsus premium kino va multfilmlarga kirish\n\n"
            "💰 Narxlar:",
            reply_markup=btn.premium_prices_keyboard()
        )

    elif text == "📊 Premium muddati":
        if not is_premium:
            await update.message.reply_text(
                "❌ Sizda hozircha Premium yo'q!\n\n"
                "Premium olish uchun '💎 Premium' tugmasini bosing.",
                reply_markup=btn.user_main_keyboard()
            )
            return
        info = db.get_premium_info(user_id)
        if info and info[0] and info[1]:
            try:
                start_dt = datetime.strptime(info[0], "%Y-%m-%d %H:%M:%S")
                end_dt = datetime.strptime(info[1], "%Y-%m-%d %H:%M:%S")
                days_left = (end_dt - datetime.now()).days
                await update.message.reply_text(
                    f"💎 Sizning Premium ma'lumotlaringiz\n\n"
                    f"📅 Boshlanish: {start_dt.strftime('%d.%m.%Y')}\n"
                    f"📆 Tugash: {end_dt.strftime('%d.%m.%Y')}\n"
                    f"⏰ Qolgan muddat: {days_left} kun\n"
                    f"💰 To'langan: {info[2]} so'm",
                    reply_markup=btn.user_main_keyboard()
                )
            except Exception:
                await update.message.reply_text("❌ Ma'lumotda xatolik!", reply_markup=btn.user_main_keyboard())

    elif text == "🔙 Orqaga":
        context.user_data.clear()
        await update.message.reply_text("🔙 Asosiy menyu", reply_markup=btn.user_main_keyboard())

    elif context.user_data.get('search_type'):
        code = text.strip()
        search_type = context.user_data['search_type']

        if search_type == 'movie':
            if is_premium:
                content = db.get_premium_movie(code)
                label = "💎 Premium Kino"
                err_msg = "❌ Bu kodda premium kino topilmadi!"
            else:
                content = db.get_movie(code)
                label = "✅ Kino topildi"
                err_msg = "❌ Bu kodda kino topilmadi!"

            if content:
                await send_video_with_buttons(
                    update, content[2],
                    f"{label}\n\n{content[1]}\n\n📝 Kod: {content[0]}"
                )
                await update.message.reply_text("🔍 Yana kod kiriting yoki 🔙 Orqaga bosing")
            else:
                await update.message.reply_text(
                    f"{err_msg}\n\nKod: {code}",
                    reply_markup=btn.user_main_keyboard()
                )
                context.user_data.clear()

        else:  # cartoon
            if is_premium:
                content = db.get_premium_cartoon(code)
                label = "💎 Premium Multfilm"
                err_msg = "❌ Bu kodda premium multfilm topilmadi!"
            else:
                content = db.get_cartoon(code)
                label = "✅ Multfilm topildi"
                err_msg = "❌ Bu kodda multfilm topilmadi!"

            if content:
                await send_video_with_buttons(
                    update, content[2],
                    f"{label}\n\n{content[1]}\n\n📝 Kod: {content[0]}"
                )
                await update.message.reply_text("🔍 Yana kod kiriting yoki 🔙 Orqaga bosing")
            else:
                await update.message.reply_text(
                    f"{err_msg}\n\nKod: {code}",
                    reply_markup=btn.user_main_keyboard()
                )
                context.user_data.clear()

    else:
        await update.message.reply_text(
            "⚠️ Iltimos, quyidagi tugmalardan birini tanlang:",
            reply_markup=btn.user_main_keyboard()
        )

# ============================================================
# ADMIN HANDLERI
# ============================================================
async def handle_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🎬 Kino yuklash":
        context.user_data.clear()
        context.user_data['upload_type'] = 'movie'
        context.user_data['step'] = 'code'
        await update.message.reply_text("📝 Kino kodini kiriting:", reply_markup=btn.back_keyboard())

    elif text == "🎨 Multfilm yuklash":
        context.user_data.clear()
        context.user_data['upload_type'] = 'cartoon'
        context.user_data['step'] = 'code'
        await update.message.reply_text("📝 Multfilm kodini kiriting:", reply_markup=btn.back_keyboard())

    elif text == "💎 Premium kino":
        context.user_data.clear()
        context.user_data['upload_type'] = 'premium_movie'
        context.user_data['step'] = 'code'
        await update.message.reply_text("📝 Premium kino kodini kiriting:", reply_markup=btn.back_keyboard())

    elif text == "💎 Premium multfilm":
        context.user_data.clear()
        context.user_data['upload_type'] = 'premium_cartoon'
        context.user_data['step'] = 'code'
        await update.message.reply_text("📝 Premium multfilm kodini kiriting:", reply_markup=btn.back_keyboard())

    elif text == "🗑 Multfilm o'chirish":
        context.user_data.clear()
        context.user_data['deleting_cartoon'] = True
        await update.message.reply_text(
            "🗑 O'chirmoqchi bo'lgan multfilmning kodini yuboring:",
            reply_markup=btn.back_keyboard()
        )

    elif text == "🗑 Kino o'chirish":
        context.user_data.clear()
        context.user_data['deleting_movie'] = True
        await update.message.reply_text(
            "🗑 O'chirmoqchi bo'lgan kinoning kodini yuboring:",
            reply_markup=btn.back_keyboard()
        )

    elif text == "🔍 Kino izlash":
        context.user_data.clear()
        context.user_data['admin_search'] = 'movie'
        await update.message.reply_text("🔍 Kino kodini kiriting:", reply_markup=btn.back_keyboard())

    elif text == "🔎 Multfilm izlash":
        context.user_data.clear()
        context.user_data['admin_search'] = 'cartoon'
        await update.message.reply_text("🔍 Multfilm kodini kiriting:", reply_markup=btn.back_keyboard())

    elif text == "📊 Statistika":
        p_users = db.get_premium_users()
        await update.message.reply_text(
            f"📊 Bot Statistikasi\n\n"
            f"👥 Jami foydalanuvchilar: {db.get_users_count()}\n"
            f"💎 Premium obunchilar: {len(p_users)}\n\n"
            f"🎬 Oddiy kinolar: {db.get_movies_count()}\n"
            f"💎 Premium kinolar: {db.get_premium_movies_count()}\n"
            f"🎨 Oddiy multfilmlar: {db.get_cartoons_count()}\n"
            f"💎 Premium multfilmlar: {db.get_premium_cartoons_count()}\n\n"
            f"📢 Obuna kanallari: {len(db.get_all_channels())}"
        )

    elif text == "📢 Xabar yuborish":
        context.user_data.clear()
        context.user_data['broadcast'] = True
        await update.message.reply_text(
            "📢 Barcha foydalanuvchilarga yuboriladigan xabarni kiriting\n"
            "(matn, rasm yoki video yuborishingiz mumkin):",
            reply_markup=btn.back_keyboard()
        )

    elif text == "⚙️ Kanallar":
        await update.message.reply_text(
            f"⚙️ Obuna kanallari boshqaruvi\n\n"
            f"📊 Jami: {len(db.get_all_channels())} ta kanal",
            reply_markup=btn.channels_keyboard()
        )

    elif text == "➕ Kanal qo'shish":
        await update.message.reply_text(
            "Qaysi turdagi kanal qo'shmoqchisiz?",
            reply_markup=btn.add_channel_type_keyboard()
        )

    elif text == "📋 Kanallar ro'yxati":
        channels = db.get_all_channels()
        if not channels:
            await update.message.reply_text("❌ Hozircha kanallar yo'q!", reply_markup=btn.channels_keyboard())
        else:
            msg = "📋 Obuna kanallari ro'yxati:\n\n"
            for i, ch in enumerate(channels, 1):
                ch_type = ch[4] if len(ch) > 4 else 'telegram'
                icon = "📸" if ch_type == 'instagram' else "📢"
                msg += f"{i}. {icon} {ch[2]}\n   🔗 {ch[3]}\n\n"
            await update.message.reply_text(msg, reply_markup=btn.channels_keyboard())

    elif text == "🗑 Kanal o'chirish":
        channels = db.get_all_channels()
        if not channels:
            await update.message.reply_text("❌ Hozircha kanallar yo'q!", reply_markup=btn.channels_keyboard())
        else:
            context.user_data.clear()
            context.user_data['delete_channel'] = True
            msg = "🗑 Qaysi kanalni o'chirmoqchisiz?\nRaqamini kiriting:\n\n"
            for i, ch in enumerate(channels, 1):
                ch_type = ch[4] if len(ch) > 4 else 'telegram'
                icon = "📸" if ch_type == 'instagram' else "📢"
                msg += f"{i}. {icon} {ch[2]}\n"
            await update.message.reply_text(msg, reply_markup=btn.back_keyboard())

    elif text == "💎 Premium panel":
        users = db.get_premium_users()
        await update.message.reply_text(
            f"💎 Premium Panel\n\n"
            f"Jami premium obunchilar: {len(users)} ta\n\n"
            f"Qaysi muddat bo'yicha ko'rmoqchisiz?",
            reply_markup=btn.premium_panel_keyboard()
        )

    elif text == "👥 Foydalanuvchilar":
        users = db.get_all_users()
        msg = f"👥 Jami foydalanuvchilar: {len(users)} ta\n\n"
        for i, u in enumerate(users[:20], 1):
            uname = f"@{u[1]}" if u[1] and u[1] != "Yo'q" else "—"
            premium_icon = "💎 " if u[5] == 1 else ""
            msg += f"{i}. {premium_icon}{u[2]} ({uname})\n"
        if len(users) > 20:
            msg += f"\n... va yana {len(users) - 20} ta foydalanuvchi"
        await update.message.reply_text(msg)

    elif text == "🎬 Kino tugmalari":
        kino_ch = db.get_kino_channel()
        info = f"\n\n📢 Hozirgi kanal: {kino_ch[2]}\n🔗 {kino_ch[1]}" if kino_ch else "\n\n❌ Hozircha kanal qo'shilmagan"
        await update.message.reply_text(
            f"🎬 Kino tugmalari bo'limi\n\n"
            f"Bu bo'limda video tagida chiqadigan '📢 Kanalimiz' tugmachasini boshqarasiz.{info}",
            reply_markup=btn.kino_tugmalari_keyboard()
        )

    elif text == "🔙 Orqaga":
        context.user_data.clear()
        await update.message.reply_text("🔙 Admin paneli", reply_markup=btn.admin_keyboard())

    elif context.user_data.get('channel_step'):
        await handle_channel_add(update, context)
    elif context.user_data.get('delete_channel'):
        await handle_delete_channel(update, context)
    elif context.user_data.get('deleting_cartoon'):
        await handle_delete_cartoon(update, context)
    elif context.user_data.get('deleting_movie'):
        await handle_delete_movie(update, context)
    elif context.user_data.get('kino_ch_add'):
        await handle_kino_channel_add(update, context)
    elif context.user_data.get('upload_type'):
        await handle_upload_text(update, context)
    elif context.user_data.get('admin_search'):
        await handle_admin_search(update, context)
    elif context.user_data.get('broadcast'):
        await broadcast(update, context)
    else:
        await update.message.reply_text(
            "⚠️ Tugmalardan birini tanlang:",
            reply_markup=btn.admin_keyboard()
        )

# ============================================================
# KANAL QO'SHISH
# ============================================================
async def handle_channel_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get('channel_step')
    text = update.message.text

    if step == 'instagram_name':
        context.user_data['channel_name'] = text
        context.user_data['channel_step'] = 'instagram_link'
        await update.message.reply_text(
            "🔗 Instagram profil linkini tashlang:\n\nMisol: https://instagram.com/username"
        )
    elif step == 'instagram_link':
        link = text.strip()
        name = context.user_data.get('channel_name', '')
        db.add_channel(link, name, link, 'instagram')
        await update.message.reply_text(
            f"✅ Instagram akkaunt qo'shildi!\n\n📸 {name}\n🔗 {link}",
            reply_markup=btn.channels_keyboard()
        )
        context.user_data.clear()

    elif step == 'name':
        context.user_data['channel_name'] = text
        context.user_data['channel_step'] = 'link'
        await update.message.reply_text("🔗 Kanal havolasini (linkini) kiriting:")

    elif step == 'link':
        context.user_data['channel_link'] = text
        context.user_data['channel_step'] = 'id'
        await update.message.reply_text(
            "🆔 Kanal ID sini kiriting:\n\nMisol: @kanal yoki -100123456789"
        )

    elif step == 'id':
        channel_id = text.strip()
        channel_name = context.user_data.get('channel_name', '')
        channel_link = context.user_data.get('channel_link', '')
        try:
            await context.bot.get_chat(chat_id=channel_id)
        except Exception:
            await update.message.reply_text(
                "❌ Kanal topilmadi!\n\nBotni kanalga qo'shib, admin qiling va qaytadan urinib ko'ring.",
                reply_markup=btn.channels_keyboard()
            )
            context.user_data.clear()
            return
        try:
            bot_member = await context.bot.get_chat_member(
                chat_id=channel_id,
                user_id=context.bot.id
            )
            if bot_member.status not in ['administrator', 'creator']:
                await update.message.reply_text(
                    "❌ Bot bu kanalda admin emas!\n"
                    "Botni kanalga admin qiling va qaytadan urinib ko'ring.",
                    reply_markup=btn.channels_keyboard()
                )
                context.user_data.clear()
                return
        except Exception:
            pass
        db.add_channel(channel_id, channel_name, channel_link, 'telegram')
        await update.message.reply_text(
            f"✅ Kanal muvaffaqiyatli qo'shildi!\n\n📢 {channel_name}\n🔗 {channel_link}",
            reply_markup=btn.channels_keyboard()
        )
        context.user_data.clear()

async def handle_delete_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        num = int(update.message.text.strip())
        channels = db.get_all_channels()
        if 1 <= num <= len(channels):
            db.delete_channel(channels[num - 1][0])
            await update.message.reply_text("✅ Kanal o'chirildi!", reply_markup=btn.channels_keyboard())
            context.user_data.clear()
        else:
            await update.message.reply_text(f"❌ Noto'g'ri raqam! 1 dan {len(channels)} gacha kiriting.")
    except ValueError:
        await update.message.reply_text("❌ Iltimos, raqam kiriting!")

# ============================================================
# MULTFILM / KINO O'CHIRISH
# ============================================================
async def handle_delete_cartoon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    cartoon = db.get_cartoon(code)
    if cartoon:
        await update.message.reply_text(
            f"⚠️ Quyidagi multfilmni o'chirishni tasdiqlaysizmi?\n\n"
            f"📝 Kod: {cartoon[0]}\n"
            f"ℹ️ Ma'lumot: {cartoon[1]}",
            reply_markup=btn.cartoon_delete_confirm_keyboard(code)
        )
    else:
        await update.message.reply_text(
            f"❌ '{code}' kodli multfilm topilmadi!",
            reply_markup=btn.admin_keyboard()
        )
    context.user_data.clear()

async def handle_delete_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    movie = db.get_movie(code)
    if movie:
        await update.message.reply_text(
            f"⚠️ Quyidagi kinoni o'chirishni tasdiqlaysizmi?\n\n"
            f"📝 Kod: {movie[0]}\n"
            f"ℹ️ Ma'lumot: {movie[1]}",
            reply_markup=btn.movie_delete_confirm_keyboard(code)
        )
    else:
        await update.message.reply_text(
            f"❌ '{code}' kodli kino topilmadi!",
            reply_markup=btn.admin_keyboard()
        )
    context.user_data.clear()

# ============================================================
# KINO TUGMASI KANALI QO'SHISH
# ============================================================
async def handle_kino_channel_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    step = context.user_data.get('kino_ch_step', 'link')
    if step == 'link':
        context.user_data['kino_ch_link'] = text
        context.user_data['kino_ch_step'] = 'name'
        await update.message.reply_text("📝 Kanal nomini kiriting:", reply_markup=btn.back_keyboard())
    elif step == 'name':
        link = context.user_data.get('kino_ch_link', '')
        db.set_kino_channel(link, text)
        await update.message.reply_text(
            f"✅ Kanalimiz tugmasi uchun kanal saqlandi!\n\n📢 {text}\n🔗 {link}",
            reply_markup=btn.admin_keyboard()
        )
        context.user_data.clear()

# ============================================================
# VIDEO YUKLASH (MATN QISMI)
# ============================================================
async def handle_upload_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get('step')
    text = update.message.text
    if step == 'code':
        context.user_data['code'] = text
        context.user_data['step'] = 'info'
        await update.message.reply_text("📋 Ma'lumotni kiriting (nomi, yili, janri va h.k.):")
    elif step == 'info':
        context.user_data['info'] = text
        context.user_data['step'] = 'video'
        upload_type = context.user_data.get('upload_type', '')
        type_names = {
            'movie': 'kino',
            'cartoon': 'multfilm',
            'premium_movie': 'premium kino',
            'premium_cartoon': 'premium multfilm'
        }
        await update.message.reply_text(
            f"🎥 Endi {type_names.get(upload_type, 'video')}ni yuboring:"
        )

# ============================================================
# VIDEO / DOCUMENT HANDLER
# ============================================================
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    step = context.user_data.get('step')
    upload_type = context.user_data.get('upload_type')
    if step == 'video' and upload_type:
        video = update.message.video or update.message.document
        if not video:
            await update.message.reply_text("❌ Video yuboring!")
            return
        code = context.user_data.get('code', '')
        info = context.user_data.get('info', '')
        if upload_type == 'movie':
            db.add_movie(code, info, video.file_id)
            await update.message.reply_text(
                f"✅ Kino muvaffaqiyatli qo'shildi!\n\n📝 Kod: {code}\nℹ️ {info}",
                reply_markup=btn.admin_keyboard()
            )
        elif upload_type == 'cartoon':
            db.add_cartoon(code, info, video.file_id)
            await update.message.reply_text(
                f"✅ Multfilm muvaffaqiyatli qo'shildi!\n\n📝 Kod: {code}\nℹ️ {info}",
                reply_markup=btn.admin_keyboard()
            )
        elif upload_type == 'premium_movie':
            db.add_premium_movie(code, info, video.file_id)
            await update.message.reply_text(
                f"✅ Premium kino muvaffaqiyatli qo'shildi!\n\n📝 Kod: {code}\nℹ️ {info}",
                reply_markup=btn.admin_keyboard()
            )
        elif upload_type == 'premium_cartoon':
            db.add_premium_cartoon(code, info, video.file_id)
            await update.message.reply_text(
                f"✅ Premium multfilm muvaffaqiyatli qo'shildi!\n\n📝 Kod: {code}\nℹ️ {info}",
                reply_markup=btn.admin_keyboard()
            )
        context.user_data.clear()

# ============================================================
# RASM HANDLER (CHEK)
# ============================================================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if context.user_data.get('waiting_receipt'):
        photo = update.message.photo[-1]
        months = context.user_data.get('premium_months', 1)
        price = context.user_data.get('premium_price', 3000)
        payment_id = db.add_payment(user_id, months, price, photo.file_id)
        user = update.effective_user
        uname = f"@{user.username}" if user.username else "Username yo'q"
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo.file_id,
            caption=(
                f"💳 Yangi to'lov so'rovi!\n\n"
                f"👤 Ism: {user.first_name}\n"
                f"🔗 Username: {uname}\n"
                f"🆔 ID: {user_id}\n"
                f"💰 Summa: {price} so'm\n"
                f"📅 Muddat: {months} oy\n"
                f"🔢 To'lov ID: #{payment_id}"
            ),
            reply_markup=btn.payment_confirm_keyboard(payment_id)
        )
        await update.message.reply_text(
            "✅ Chek muvaffaqiyatli yuborildi!\n\n"
            "⏳ Admin tekshirgach, premium faollashtiriladi. Biroz kuting.",
            reply_markup=btn.user_main_keyboard()
        )
        context.user_data.clear()

    elif is_admin(user_id) and context.user_data.get('broadcast'):
        await broadcast(update, context)

# ============================================================
# ADMIN IZLASH
# ============================================================
async def handle_admin_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    search_type = context.user_data.get('admin_search')
    if search_type == 'movie':
        content = db.get_movie(code)
        if content:
            await update.message.reply_video(
                video=content[2],
                caption=f"✅ Kino topildi!\n\n{content[1]}\n\n📝 Kod: {content[0]}"
            )
        else:
            await update.message.reply_text(f"❌ '{code}' kodli kino topilmadi!")
    else:
        content = db.get_cartoon(code)
        if content:
            await update.message.reply_video(
                video=content[2],
                caption=f"✅ Multfilm topildi!\n\n{content[1]}\n\n📝 Kod: {content[0]}"
            )
        else:
            await update.message.reply_text(f"❌ '{code}' kodli multfilm topilmadi!")

# ============================================================
# BROADCAST
# ============================================================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = db.get_all_users()
    message = update.message
    sent = 0
    failed = 0
    await update.message.reply_text(f"📢 {len(users)} ta foydalanuvchiga yuborilmoqda...")
    for u in users:
        try:
            if message.text:
                await context.bot.send_message(
                    chat_id=u[0],
                    text=f"📢 Yangi xabar!\n\n{message.text}"
                )
            elif message.photo:
                await context.bot.send_photo(
                    chat_id=u[0],
                    photo=message.photo[-1].file_id,
                    caption=f"📢 Yangi xabar!\n\n{message.caption or ''}"
                )
            elif message.video:
                await context.bot.send_video(
                    chat_id=u[0],
                    video=message.video.file_id,
                    caption=f"📢 Yangi xabar!\n\n{message.caption or ''}"
                )
            sent += 1
        except Exception:
            failed += 1
    await update.message.reply_text(
        f"✅ Broadcast yakunlandi!\n\n"
        f"📤 Yuborildi: {sent} ta\n"
        f"❌ Xatolik: {failed} ta",
        reply_markup=btn.admin_keyboard()
    )
    context.user_data.clear()

# ============================================================
# MAIN
# ============================================================
def main():
    db.init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.ALL, handle_video))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot muvaffaqiyatli ishga tushdi!")
    print(f"   👑 Admin ID: {ADMIN_ID}")
    print(f"   👥 Foydalanuvchilar: {db.get_users_count()}")
    print(f"   🎬 Oddiy kinolar: {db.get_movies_count()}")
    print(f"   💎 Premium kinolar: {db.get_premium_movies_count()}")
    print(f"   🎨 Oddiy multfilmlar: {db.get_cartoons_count()}")
    print(f"   💎 Premium multfilmlar: {db.get_premium_cartoons_count()}")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()

# Bot mashhudev tomonidan yaratildi