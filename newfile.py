import telebot
from telebot import types
import google.generativeai as genai
import time
import html

# ==========================================
# 1. إعدادات البوت والبيانات الأساسية
# ==========================================

# التوكن الجديد والمحدث
TOKEN = "8943659346:AAGVmcKsXHO6ACWIl6TPs-ZbMCiwVpS23Nk"
bot = telebot.TeleBot(TOKEN)

# مفتاح الذكاء الاصطناعي (Gemini API)
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

ai_model = None
if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY":
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        ai_model = genai.GenerativeModel('gemini-2.5-flash')
        print("✅ تم تفعيل موديل الذكاء الاصطناعي بنجاح.")
    except Exception as e:
        print(f"⚠️ فشل تفعيل الذكاء الاصطناعي: {e}")

# البيانات والثوابت العامة
ADMIN_ID = "7315643325"
OWNER_ID_GAME = "6513417186"

# روابط الخدمات والمواقع الخارجية
TOKEN_URL = "https://narayan-eta-to-access-token.lovable.app/"
VIDEO_EXPLANATION_URL = "https://youtube.com/shorts/Jsf3PbTVSzg?si=EcNDE3HgG1q2BK8u"
BIO_URL = "https://m2.0xarm.com/longbio"
SQUAD_URL = "https://m2.0xarm.com/ingame"
INSTAGRAM_URL = "https://www.instagram.com/a_m_i_r__mb_16_?stkn=MWpiOTR5ZWZwcTRjZw=="
OFFICIAL_CHANNEL = "narayan_verma" # اسم القناة الرسمية بدون @

# قاعدة بيانات مؤقتة للمستخدمين
user_data = {}

# ==========================================
# 2. الدوال المساعدة وإدارة الحسابات
# ==========================================

def get_user_info(chat_id):
    """إنشاء أو جلب بيانات المستخدم"""
    if chat_id not in user_data:
        user_data[chat_id] = {
            'points': 0,
            'last_daily': 0,
            'token': None,
            'joined_channel': False,
            'referrals': 0
        }
    return user_data[chat_id]

def check_channel_membership(user_id, channel_username):
    """التحقق برمجياً من انضمام المستخدم للقناة أو المجموعة الرسمية"""
    try:
        member = bot.get_chat_member(f"@{channel_username}", user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception:
        return False
    return False

# ==========================================
# 3. بناء القوائم والأزرار (Inline Keyboards)
# ==========================================

def main_menu_keyboard(chat_id):
    """القائمة الرئيسية للبوت"""
    user = get_user_info(chat_id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # قسم النقاط والهدية
    btn_points = types.InlineKeyboardButton(f"💰 رصيدك: {user['points']} نقطة", callback_data="btn_my_points")
    btn_daily = types.InlineKeyboardButton("🎁 الهدية اليومية (+2)", callback_data="btn_daily_gift")
    btn_gifts_menu = types.InlineKeyboardButton("⭐ قسم الهدايا والمهام", callback_data="btn_gifts_menu")
    
    # قسم الخدمات المدفوعة
    btn_control = types.InlineKeyboardButton("🎮 التحكم بالحساب ($4)", callback_data="btn_control_account")
    btn_ban = types.InlineKeyboardButton("🚫 تبنيد الحساب ($1)", callback_data="btn_ban_account")
    btn_market = types.InlineKeyboardButton("🛒 بيع / شراء / تبديل حسابات", callback_data="btn_market")
    
    # قسم خدمات الألعاب
    btn_likes = types.InlineKeyboardButton("👍 زيادة اللايكات", callback_data="btn_likes")
    btn_dances = types.InlineKeyboardButton("🕺 كل الرقصات (22 نقطة)", callback_data="btn_buy_dances")
    btn_level = types.InlineKeyboardButton("⬆️ رفع الليفل", callback_data="btn_level")
    btn_bio = types.InlineKeyboardButton("📝 بايو طويل", callback_data="btn_bio")
    btn_squad = types.InlineKeyboardButton("⚔️ سكواد 5 و 6", callback_data="btn_squad")
    btn_insta = types.InlineKeyboardButton("📩 الدعم (Instagram)", url=INSTAGRAM_URL)
    
    markup.add(btn_points, btn_daily)
    markup.add(btn_gifts_menu)
    markup.add(btn_control, btn_ban)
    markup.add(btn_market)
    markup.add(btn_likes, btn_dances)
    markup.add(btn_level, btn_bio)
    markup.add(btn_squad)
    markup.add(btn_insta)
    return markup

def admin_approval_keyboard(user_id, service_type="control"):
    """أزرار الموافقة والرفض الموجهة للأدمن"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_approve = types.InlineKeyboardButton("✅ موافقة", callback_data=f"approve_{service_type}_{user_id}")
    btn_reject = types.InlineKeyboardButton("❌ رفض", callback_data=f"reject_{service_type}_{user_id}")
    markup.add(btn_approve, btn_reject)
    return markup

def market_menu_keyboard():
    """قائمة خيارات بيع وشراء الحسابات"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_buy = types.InlineKeyboardButton("🛍️ تصفح الحسابات المتاحة للشراء", url=INSTAGRAM_URL)
    btn_sell = types.InlineKeyboardButton("📩 عرض حسابك للبيع أو التبديل", callback_data="btn_sell_account")
    btn_back = types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="btn_main_menu")
    markup.add(btn_buy, btn_sell, btn_back)
    return markup

def gifts_menu_keyboard():
    """قائمة مهام جمع النقاط الهدايا"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_check_sub = types.InlineKeyboardButton("📢 الاشتراك بالمجموعة (+5 نقاط)", callback_data="btn_claim_sub")
    btn_ref_link = types.InlineKeyboardButton("🔗 رابط الدعوة الخاص بك (+5 نقاط لكل شخص)", callback_data="btn_ref_link")
    btn_back = types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="btn_main_menu")
    markup.add(btn_check_sub, btn_ref_link, btn_back)
    return markup

def token_help_keyboard():
    """قائمة المساعدة في استخراج التوكن"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_get = types.InlineKeyboardButton("🌐 استخراج التوكن", url=TOKEN_URL)
    btn_video = types.InlineKeyboardButton("🎬 فيديو الشرح", url=VIDEO_EXPLANATION_URL)
    btn_back = types.InlineKeyboardButton("🔙 العودة", callback_data="btn_main_menu")
    markup.add(btn_get, btn_video, btn_back)
    return markup

# ==========================================
# 4. معالجة الأوامر الرئيسية
# ==========================================

@bot.message_handler(commands=['start'])
def start_msg(message):
    chat_id = message.chat.id
    user_name = html.escape(message.from_user.first_name)
    user_username = f"@{html.escape(message.from_user.username)}" if message.from_user.username else "لا يوجد"
    
    get_user_info(chat_id)
    
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])
        if referrer_id != chat_id and referrer_id in user_data:
            user_data[referrer_id]['points'] += 5
            user_data[referrer_id]['referrals'] += 1
            try:
                bot.send_message(referrer_id, "🎉 <b>انضم مستخدم جديد عن طريق رابطك!</b>\nحصلت على 5 نقاط إضافية.", parse_mode="HTML")
            except Exception:
                pass

    admin_notification = (
        f"🔔 <b>مستخدم جديد دخل البوت!</b>\n\n"
        f"👤 <b>الاسم:</b> {user_name}\n"
        f"🌐 <b>اليوزر:</b> {user_username}\n"
        f"🆔 <b>ID:</b> <code>{chat_id}</code>"
    )
    try:
        bot.send_message(ADMIN_ID, admin_notification, parse_mode="HTML")
    except Exception:
        pass

    text = (
        f"👋 <b>أهلاً بك يا {user_name} في بوت الخدمات والتسهيلات!</b>\n\n"
        "إليك جميع الخدمات المتاحة، يمكنك جمع النقاط يومياً واستخدام الأوامر والخدمات مجاناً 👇"
    )
    bot.reply_to(message, text, parse_mode="HTML", reply_markup=main_menu_keyboard(chat_id))

def request_ban_service(chat_id, user_info):
    user_name = html.escape(user_info.first_name)
    user_username = f"@{html.escape(user_info.username)}" if user_info.username else "لا يوجد"

    msg_text = (
        "🚫 <b>خدمة تبنيد الحساب:</b>\n\n"
        "هذه الخدمة <b>مدفوعة بسعر 1 دولار فقط ($1)</b>.\n"
        "تم إرسال طلبك للإدارة للمراجعة. يرجى التواصل لإتمام الدفع، وبمجرد تأكيد الدفع سيرسل لك البوت رابط الخدمة المباشر."
    )
    bot.send_message(chat_id, msg_text, parse_mode="HTML")

    admin_msg = (
        f"📥 <b>طلب خدمة جديدة (تبنيد الحساب - $1)</b>\n\n"
        f"👤 <b>المستخدم:</b> {user_name}\n"
        f"🌐 <b>اليوزر:</b> {user_username}\n"
        f"🆔 <b>ID:</b> <code>{chat_id}</code>\n\n"
        f"هل تم استلام المبلغ ($1) وتأكيد الخدمة؟"
    )
    try:
        bot.send_message(ADMIN_ID, admin_msg, parse_mode="HTML", reply_markup=admin_approval_keyboard(chat_id, "ban"))
    except Exception as e:
        print(f"❌ تعذر إرسال الإشعار للأدمن: {e}")

# ==========================================
# 5. معالجة أزرار التفاعل (Callback Handlers)
# ==========================================

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    try:
        bot.answer_callback_query(call.id)
    except Exception:
        pass

    chat_id = call.message.chat.id
    user = get_user_info(chat_id)

    # العودة للقائمة الرئيسية
    if call.data == "btn_main_menu":
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="🏠 <b>القائمة الرئيسية:</b>",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(chat_id)
        )

    elif call.data == "btn_control_account":
        user_info = call.from_user
        user_name = html.escape(user_info.first_name)
        user_username = f"@{html.escape(user_info.username)}" if user_info.username else "لا يوجد"
        
        bot.send_message(
            chat_id, 
            "⏳ <b>تم إرسال طلب تفعيل خدمة (التحكم بالحساب) للأدمن للمراجعة.</b>\n"
            "سوف يصلك الرد هنا فور تأكيد عملية الدفع ($4).", 
            parse_mode="HTML"
        )
        
        admin_msg = (
            f"📥 <b>طلب خدمة جديدة (التحكم بالحساب - $4)</b>\n\n"
            f"👤 <b>المستخدم:</b> {user_name}\n"
            f"🌐 <b>اليوزر:</b> {user_username}\n"
            f"🆔 <b>ID:</b> <code>{chat_id}</code>\n\n"
            f"هل تم استلام الدفع وتريد تأكيد الخدمة؟"
        )
        try:
            bot.send_message(ADMIN_ID, admin_msg, parse_mode="HTML", reply_markup=admin_approval_keyboard(chat_id, "control"))
        except Exception as e:
            print(f"❌ تعذر إرسال الإشعار للأدمن: {e}")

    elif call.data == "btn_ban_account":
        request_ban_service(chat_id, call.from_user)

    elif call.data.startswith("approve_"):
        parts = call.data.split("_")
        service_type = parts[1]
        target_user_id = parts[2]
        
        if service_type == "ban":
            approval_text = (
                "✅ <b>تم تأكيد دفع مبلغ $1 بنجاح!</b>\n\n"
                "يمكنك الآن استخدام بوت تبنيد الحسابات عبر الرابط التالي:\n"
                "👉 @FFAccountBanBot"
            )
        else:
            approval_text = (
                "✅ <b>تمت الموافقة على طلبك بنجاح!</b>\n\n"
                "يمكنك الآن استخدام البوت المخصص عبر الرابط التالي:\n"
                "👉 @Monte_tool_ffbot"
            )

        try:
            bot.send_message(target_user_id, approval_text, parse_mode="HTML")
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"✅ <b>تمت الموافقة وإرسال البوت المخصص للمستخدم</b> (ID: <code>{target_user_id}</code>)",
                parse_mode="HTML"
            )
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ تعذر إرسال الرسالة للمستخدم: {e}")

    elif call.data.startswith("reject_"):
        parts = call.data.split("_")
        target_user_id = parts[2]
        
        rejection_text = "❌ <b>عذراً، تم رفض طلبك.</b>\nيرجى التأكد من إتمام عملية الدفع والتواصل مع الدعم عبر الإنستغرام."
        try:
            bot.send_message(target_user_id, rejection_text, parse_mode="HTML")
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"❌ <b>تم رفض الطلب وإبلاغ المستخدم</b> (ID: <code>{target_user_id}</code>)",
                parse_mode="HTML"
            )
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ تعذر إرسال الرسالة للمستخدم: {e}")

    elif call.data == "btn_market":
        text = (
            "🛒 <b>قسم بيع وشراء وتبديل الحسابات:</b>\n\n"
            "تتم جميع المعاملات وتوثيق الحسابات عبر حسابنا الرسمي على الإنستغرام لتفادي الاحتيال وضمان الحقوق.\n\n"
            "اختر ما تريد من القائمة أدناه 👇"
        )
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            parse_mode="HTML",
            reply_markup=market_menu_keyboard()
        )

    elif call.data == "btn_sell_account":
        text = (
            "📩 <b>طريقة عرض حسابك للبيع أو التبديل:</b>\n\n"
            "يرجى التواصل مباشرة مع الإدارة عبر حساب الانستغرام وإرسال التفاصيل التالية:\n"
            "1️⃣ صور أو فيديو لمحتويات الحساب.\n"
            "2️⃣ نوع الربط (فيسبوك، تويتر، إلخ...).\n"
            "3️⃣ السعر المطلوب أو الحساب المراد التبديل معه.\n\n"
            f'🔗 <a href="{INSTAGRAM_URL}">اضغط هنا للمراسلة المباشرة على الانستغرام</a>'
        )
        bot.send_message(chat_id, text, parse_mode="HTML", disable_web_page_preview=True)

    elif call.data == "btn_my_points":
        msg = f"💰 <b>رصيدك الحالي:</b> {user['points']} نقطة\n👥 <b>عدد الإحالات:</b> {user['referrals']}"
        bot.send_message(chat_id, msg, parse_mode="HTML")

    elif call.data == "btn_daily_gift":
        current_time = time.time()
        if current_time - user['last_daily'] >= 86400:
            user['points'] += 2
            user['last_daily'] = current_time
            bot.send_message(chat_id, "🎉 <b>مبروك!</b> حصلت على 2 نقاط كهدية يومية.", parse_mode="HTML")
            bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=main_menu_keyboard(chat_id))
        else:
            remaining_hours = int((86400 - (current_time - user['last_daily'])) / 3600)
            bot.send_message(chat_id, f"⏳ لقد أخذت هديتك اليومية بالفعل! يرجى الانتظار <b>{remaining_hours} ساعة</b> إضافية.", parse_mode="HTML")

    elif call.data == "btn_gifts_menu":
        text = (
            "⭐ <b>قسم الهدايا وتجميع النقاط المجانية:</b>\n\n"
            "اختر إحدى الطرق التالية للحصول على نقاط إضافية وتفعيل الخدمات المدفوعة مجاناً:"
        )
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            parse_mode="HTML",
            reply_markup=gifts_menu_keyboard()
        )

    elif call.data == "btn_claim_sub":
        if user['joined_channel']:
            bot.send_message(chat_id, "❌ <b>لقد استلمت مكافأة الانضمام سابقاً!</b>", parse_mode="HTML")
        else:
            if check_channel_membership(chat_id, OFFICIAL_CHANNEL):
                user['points'] += 5
                user['joined_channel'] = True
                bot.send_message(chat_id, "🎉 <b>تم التحقق بنجاح!</b> حصلت على 5 نقاط إضافية.", parse_mode="HTML")
                bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=main_menu_keyboard(chat_id))
            else:
                msg_sub = (
                    f"❌ <b>لم تنضم للمجموعة بعد!</b>\n\n"
                    f"يرجى الانضمام إلى المجموعة أولاً عبر الرابط:\n"
                    f"👉 @{OFFICIAL_CHANNEL}\n\n"
                    f"📌 <b>شروط الحصول على النقاط:</b>\n"
                    f"عند الدخول إلى المجموعة، يجب عليك إرسال هذا الأمر بالضبط داخل المجموعة:\n"
                    f"<code>/like me 6513417186</code>"
                )
                bot.send_message(chat_id, msg_sub, parse_mode="HTML")

    elif call.data == "btn_ref_link":
        bot_info = bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={chat_id}"
        text = (
            f"🔗 <b>رابط الدعوة الخاص بك:</b>\n<code>{ref_link}</code>\n\n"
            "قم بنشر هذا الرابط لأصدقائك، وكل شخص يدخل للبوت عن طريقك ستحصل على <b>5 نقاط</b> فوراً!"
        )
        bot.send_message(chat_id, text, parse_mode="HTML")

    elif call.data == "btn_buy_dances":
        COST = 22
        if user['points'] >= COST:
            user['points'] -= COST
            bot.send_message(chat_id, "✅ <b>تم خصم 22 نقطة بنجاح!</b> تم تفعيل خدمة كل الرقصات لحسابك مجاناً.", parse_mode="HTML")
            bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=main_menu_keyboard(chat_id))
        else:
            needed = COST - user['points']
            text = (
                f"❌ <b>نقاطك غير كافية!</b>\n\n"
                f"سعر الخدمة: <b>22 نقطة</b> (أو 4 دولار)\n"
                f"رصيدك الحالي: <b>{user['points']} نقطة</b>\n"
                f"تحتاج إلى <b>{needed} نقاط</b> إضافية لتفعيلها مجاناً."
            )
            bot.send_message(chat_id, text, parse_mode="HTML")

    elif call.data == "btn_likes":
        text = "👍 <b>خدمة زيادة اللايكات:</b>\n\nيرجى استخراج التوكن الخاص بك وإرساله هنا لتشغيل الخدمة."
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=token_help_keyboard())

    elif call.data == "btn_level":
        bot.send_message(chat_id, "⬆️ <b>خدمة رفع الليفل:</b>\n\nتواصل مع الدعم الفني لمتابعة التحديثات والعروض.", parse_mode="HTML")

    elif call.data == "btn_bio":
        text = f'📝 <b>خدمة البايو الطويل:</b>\n\nانقر على الرابط التالي لتعديل البايو الخاص بحسابك:\n🔗 <a href="{BIO_URL}">اضغط هنا للفتح</a>'
        bot.send_message(chat_id, text, parse_mode="HTML", disable_web_page_preview=True)

    elif call.data == "btn_squad":
        text = f'⚔️ <b>خدمة سكواد 5 و 6:</b>\n\nانقر على الرابط التالي للوصول لتعديل السكواد:\n🔗 <a href="{SQUAD_URL}">اضغط هنا للفتح</a>'
        bot.send_message(chat_id, text, parse_mode="HTML", disable_web_page_preview=True)

# ==========================================
# 6. معالجة الرسائل النصية والـ AI
# ==========================================

@bot.message_handler(func=lambda message: True)
def handle_user_text(message):
    chat_id = message.chat.id
    user_text = message.text

    if "تبنيد الحساب" in user_text or "تبنيد حساب" in user_text:
        request_ban_service(chat_id, message.from_user)
        return

    if "توكن" in user_text or "token" in user_text.lower():
        bot.reply_to(message, "🔑 لاستخراج التوكن الخاص بك، استخدم الأزرار التالية:", reply_markup=token_help_keyboard())
        return

    if ai_model:
        try:
            prompt = f"أنت مساعد آلي ذكي وخفيف الظل لبوت خدمات ألعاب وتسهيلات. أجب بإيجاز وبشكل واضح على الاستفسار التالي: {user_text}"
            response = ai_model.generate_content(prompt)
            bot.reply_to(message, response.text)
            return
        except Exception as e:
            print(f"خطأ في استجابة Gemini: {e}")

    bot.reply_to(message, "تفضل باختيار الخدمة المناسبة لك من القائمة أدناه 👇", reply_markup=main_menu_keyboard(chat_id))

# ==========================================
# 7. تشغيل البوت المباشر
# ==========================================

if __name__ == "__main__":
    print("==========================================")
    print("🤖 البوت يعمل بنجاح ومستعد لاستقبال الطلبات...")
    print("==========================================")
    bot.infinity_polling()
