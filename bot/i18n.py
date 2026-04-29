"""Internationalization for SmartChannelX. Arabic (ar) primary, English (en) secondary."""
from __future__ import annotations

from typing import Any

TRANSLATIONS: dict[str, dict[str, str]] = {
    "ar": {
        # Welcome
        "welcome_title": "👋 مرحبًا بك في SmartChannelX!",
        "welcome_body": (
            "أنا مساعدك الذكي لإدارة قنوات تيليجرام باحترافية وسهولة. "
            "سواء كنت ترغب في جدولة المنشورات، حماية قناتك، تحليل الإحصائيات، "
            "أو تخصيص تجربة المشتركين — يوفر SmartChannelX لك كل الأدوات التي تحتاجها.\n\n"
            "🚀 ابدأ الآن بإدارة قنواتك بكفاءة عالية!\n\n"
            "للبدء، يرجى إضافة قناتك أو اختيار إحدى القنوات التي تديرها."
        ),
        "btn_add_channel": "➕ إضافة قناة جديدة",
        "btn_my_channels": "⚙️ إدارة قنواتي",
        "btn_help": "❓ مساعدة",
        # Global nav
        "btn_back": "🔙 رجوع",
        "btn_home": "🏠 الرئيسية",
        "btn_cancel": "❌ إلغاء",
        "btn_yes": "✅ نعم",
        "btn_no": "❌ لا",
        # Channel main menu
        "channel_menu_title": "✨ أهلًا بك في لوحة تحكم القناة: {name}",
        "channel_menu_body": "اختر الإجراء الذي تود القيام به لإدارة قناتك. يمكنك دائمًا العودة إلى هذه القائمة أو إلغاء أي عملية.",
        "btn_create_post": "📝 إنشاء منشور جديد",
        "btn_schedule_posts": "📅 جدولة المنشورات",
        "btn_protection": "🛡️ حماية القناة",
        "btn_statistics": "📊 إحصائيات القناة",
        "btn_channel_settings": "⚙️ إعدادات القناة",
        "btn_admins": "👤 إدارة المشرفين",
        "btn_change_channel": "🌐 تغيير القناة/اللغة",
        # Channel list
        "no_channels": (
            "📭 لا توجد قنوات مضافة بعد.\n\n"
            "لإضافة قناة:\n"
            "1️⃣ أضف هذا البوت كمشرف في قناتك مع صلاحية النشر.\n"
            "2️⃣ ثم اضغط على ➕ إضافة قناة جديدة."
        ),
        "channels_list_title": "⚙️ قنواتك المضافة\n\nاختر قناة لإدارتها:",
        # Add channel
        "add_channel_prompt": (
            "➕ إضافة قناة أو مجموعة جديدة\n\n"
            "اختر الطريقة الأنسب لك من القائمة أدناه. يمكنك إضافتي بضغطة واحدة "
            "كمشرف في قناة أو مجموعة، أو إضافة قناة موجودة يدويًا."
        ),
        "btn_add_to_channel_admin": "📢 أضِفني كمشرف في قناة",
        "btn_add_to_group_admin": "👥 أضِفني كمشرف في مجموعة",
        "btn_add_via_username": "🔤 إضافة عبر @username",
        "btn_add_via_forward": "↪️ إضافة برسالة موجَّهة",
        "btn_add_via_id": "🔢 إضافة عبر Chat ID",
        "btn_add_via_link": "🔗 إضافة عبر رابط t.me",
        "add_channel_methods_help": (
            "💡 ملاحظات مهمة:\n"
            "• القنوات الخاصة: استخدم زر «أضِفني كمشرف في قناة» أو وجّه رسالة منها.\n"
            "• اختر صلاحيات: نشر، تعديل، حذف، دعوة، حظر، إدارة المحادثات الصوتية.\n"
            "• بعد إضافتي ستصلك رسالة تأكيد تلقائيًا — لا حاجة لكتابة أي شيء."
        ),
        "add_via_username_prompt": (
            "🔤 أرسل اسم المستخدم للقناة أو المجموعة العامة:\n\n"
            "مثال: `@mychannel`\n\n"
            "تأكد أنني مشرف فيها أولًا."
        ),
        "add_via_forward_prompt": (
            "↪️ وجِّه أي رسالة من القناة أو المجموعة التي تود إضافتها.\n\n"
            "(يجب أن تكون الرسائل المُعاد توجيهها مفعّلة في إعدادات الخصوصية للقناة)."
        ),
        "add_via_id_prompt": (
            "🔢 أرسل معرّف القناة أو المجموعة (Chat ID):\n\n"
            "مثال: `-1001234567890`\n\n"
            "يمكنك معرفته عبر إضافة بوت معرّفات أو من إعدادات تيليجرام."
        ),
        "add_via_link_prompt": (
            "🔗 أرسل رابط القناة أو المجموعة بصيغة:\n\n"
            "`https://t.me/mychannel`\n"
            "أو\n"
            "`https://t.me/joinchat/...`\n\n"
            "ملاحظة: روابط الدعوة الخاصة تتطلب أن أكون مشرفًا أولًا."
        ),
        "add_channel_success": "✅ تم إضافة قناتك بنجاح: {name}",
        "add_channel_auto_registered": (
            "🎉 تم اكتشافي تلقائيًا في {chat_type}: {name}\n\n"
            "تم تسجيلها في حسابك وأنت الآن قادر على إدارتها من /start."
        ),
        "add_channel_failed": "❌ تعذّر إضافة القناة. تأكد أنني مشرف فيها وأن المعرّف صحيح.",
        "add_channel_not_admin": (
            "⚠️ يجب أن أكون مشرفًا في «{name}» قبل أن تتمكن من إدارتها.\n\n"
            "أضِفني كمشرف ثم حاول مرة أخرى."
        ),
        "add_channel_already": "ℹ️ هذه القناة مضافة مسبقًا: {name}",
        "add_channel_user_not_admin": (
            "⛔ لإضافة «{name}» يجب أن تكون أنت مالكها أو مشرفًا فيها."
        ),
        "chat_type_channel": "القناة",
        "chat_type_group": "المجموعة",
        "chat_type_supergroup": "المجموعة الخارقة",
        "bot_demoted_in_chat": "⚠️ تم إزالتي كمشرف من «{name}». لن أستطيع إدارتها بعد الآن.",
        "bot_removed_from_chat": "ℹ️ تم إزالتي من «{name}». تم تعطيل إدارتها.",
        # Verify status
        "btn_verify_admin": "🔄 تحقّق من صلاحياتي",
        "btn_verify_all": "🩺 فحص جميع القنوات",
        "verify_status_admin": "✅ أنا مشرف في «{name}»",
        "verify_status_owner": "👑 أنا المالك في «{name}»",
        "verify_status_member": "⚠️ أنا عضو فقط في «{name}» — أحتاج رفعي كمشرف.",
        "verify_status_left": "❌ أنا لست عضوًا في «{name}». أضِفني مجدّدًا.",
        "verify_status_unknown": "❔ لا أستطيع الوصول إلى «{name}». تأكد أنني لا أزال داخلها.",
        "verify_perms_title": "🔐 الصلاحيات الممنوحة:",
        "verify_perms_none": "🔒 ليس لدي أي صلاحيات إدارية فعّالة.",
        "verify_error": "❗ خطأ: {error}",
        "verify_all_title": "🩺 فحص حالة جميع قنواتك:",
        "verify_all_empty": "📭 لا توجد قنوات لفحصها. أضِف قناة أولًا.",
        "channel_status_header": "📊 الحالة الحالية:",
        "verify_chat_added_channel": (
            "✅ تم تفعيلي بنجاح في هذه القناة!\n\n"
            "أنا الآن مشرف وجاهز لاستقبال أوامر الإدارة. "
            "افتح حواري الخاص لإدارة القناة."
        ),
        "verify_chat_added_group": (
            "✅ تم تفعيلي بنجاح في هذه المجموعة!\n\n"
            "أنا الآن مشرف وجاهز للحماية والإدارة."
        ),
        # Help
        "help_text": (
            "❓ دليل استخدام SmartChannelX\n\n"
            "🔹 ➕ إضافة قناة جديدة: أضفني كمشرف في قناتك ثم سجّلها هنا.\n"
            "🔹 ⚙️ إدارة قنواتي: تنقّل بين قنواتك وافتح لوحة تحكم خاصة بكل قناة.\n"
            "🔹 📝 إنشاء منشور: أرسل نص/صورة/فيديو/ملف، أضف أزرار، ثم انشر أو جدوِل.\n"
            "🔹 📅 جدولة المنشورات: حدّد تاريخًا ووقتًا أو كرّر النشر يوميًا/أسبوعيًا/شهريًا.\n"
            "🔹 🛡️ حماية القناة: كابتشا، فلاتر انضمام، كلمات محظورة، حظر البوتات.\n"
            "🔹 📊 إحصائيات: نمو المشتركين وأداء المنشورات.\n"
            "🔹 ⚙️ إعدادات: لغة، منطقة زمنية، توقيع تلقائي، إشعارات.\n"
            "🔹 👤 المشرفين: أضف/أزل مشرفين وحدّد صلاحياتهم داخل البوت.\n\n"
            "للوصول السريع: استخدم /start في أي وقت."
        ),
        # Create post
        "create_post_prompt": (
            "📝 إنشاء منشور جديد\n\n"
            "أرسل لي الآن المحتوى الذي تود نشره في قناتك. يمكنك إرسال نص، صورة، فيديو، أو ملف.\n\n"
            "بعد إرسال المحتوى، ستظهر لك خيارات إضافية لتخصيص المنشور."
        ),
        "post_settings_title": (
            "⚙️ إعدادات المنشور الجديد\n\n"
            "قبل إرسال المحتوى، يرجى ضبط إعدادات المنشور كما تفضل.\n"
            "عند الانتهاء، اضغط على زر «الخطوة التالية»."
        ),
        "btn_post_silent": "🔕 الإشعارات: {state}",
        "btn_post_protect": "🛡️ حماية المحتوى: {state}",
        "btn_post_pin": "📌 تثبيت تلقائي: {state}",
        "btn_next_content": "⬅️ الخطوة التالية: كتابة المنشور",
        "post_content_prompt": "📝 ممتاز! الآن أرسل المحتوى (نص، صورة، فيديو، ملف، الخ).",
        "post_received": "✅ تم استلام المحتوى بنجاح. ما الذي تود إضافته؟",
        "btn_add_media": "🖼️ إضافة وسائط",
        "btn_add_buttons": "🔗 إضافة أزرار",
        "btn_advanced_settings": "⚙️ إعدادات متقدمة",
        "btn_preview_publish": "✅ معاينة ونشر",
        "btn_edit_buttons": "🔗 تعديل الأزرار",
        # New Post Control Panel
        "btn_auto_delete": "🗑️ التدمير الذاتي",
        "btn_auto_reply": "💬 رسالة الرد",
        "btn_reactions_settings": "❤️ ردود الفعل",
        "btn_crosspost": "📢 نشر متعدد",
        "btn_save_draft": "💾 حفظ كمسودة",
        "btn_btnbuilder_wizard": "🛠️ منشئ الأزرار التفاعلي",
        "btn_btnbuilder_favs": "⭐ الأزرار المفضلة",
        "btn_btnbuilder_clear": "❌ مسح الأزرار",
        # Buttons input
        "buttons_prompt": (
            "🔗 إضافة الأزرار المتقدمة للمنشور\n\n"
            "يمكنك إضافة أزرار بأشكال ووظائف متعددة (بإمكانك استخدام Premium Emoji في نص الزر). "
            "أرسل الأزرار بالصيغ التالية، كل سطر يمثل صفاً من الأزرار:\n\n"
            "🔹 **1. زر رابط عادي:**\n"
            "`نص الزر - https://t.me/...`\n\n"
            "🔹 **2. أزرار متجاورة (في نفس السطر):**\n"
            "`زر 1 - رابط 1 && زر 2 - رابط 2`\n\n"
            "🔹 **3. زر منبثق (رسالة على الشاشة):**\n"
            "`تنبيه 💡 - popup: هذه رسالة منبثقة!`\n\n"
            "🔹 **4. زر نسخ النص:**\n"
            "`انسخ الكود 📋 - copy: CODE123`\n\n"
            "🔹 **5. زر مشاركة النص/الرابط:**\n"
            "`شارك البوت 📢 - share: انضموا لهذا البوت الرائع!`\n\n"
            "🔹 **6. زر التعليقات:**\n"
            "`التعليقات 💬 - comments: https://t.me/c/...`\n\n"
            "🔹 **7. زر التحقق من الاشتراك:**\n"
            "`هل أنا مشترك؟ - sub: @channel_username`\n\n"
            "💡 *ملاحظة: لدمج أي أنواع معاً في سطر واحد، افصل بينها بـ `&&`.*"
        ),
        "buttons_saved": "✅ تم إضافة الأزرار بنجاح ({count} زر).",
        "buttons_invalid": "❌ صيغة غير صحيحة. تأكد من استخدام: نص الزر - رابط",
        "sub_yes": "✅ أنت مشترك بالفعل في هذه القناة!",
        "sub_no": "❌ أنت لست مشتركاً في هذه القناة حتى الآن.",
        "sub_error": "⚠️ لم نتمكن من التحقق من اشتراكك.",
        # Preview
        "preview_title": "👀 هذه معاينة لمنشورك:",
        "preview_question": "ماذا تود أن تفعل بهذا المنشور؟",
        "btn_publish_now": "🚀 نشر الآن",
        "btn_schedule_publish": "⏰ جدولة النشر",
        "btn_make_recurring": "🔁 جعله متكررًا",
        "btn_edit_post": "✏️ تعديل المنشور",
        "publish_success": "🎉 تم نشر منشورك بنجاح في القناة!",
        "publish_failed": "❌ فشل النشر: {error}",
        # Advanced settings
        "advanced_settings_title": "⚙️ إعدادات متقدمة للمنشور",
        "btn_toggle_signature": "✍️ التوقيع التلقائي: {state}",
        "btn_parse_mode": "📝 التنسيق: {mode}",
        "btn_disable_preview": "🔗 معاينة الروابط: {state}",
        "state_on": "مُفعّل",
        "state_off": "معطّل",
        # Schedule
        "schedule_menu_title": "📅 جدولة المنشورات",
        "schedule_menu_body": "هنا يمكنك إدارة جميع منشوراتك المجدولة والمتكررة. اختر الإجراء الذي تود القيام به.",
        "btn_schedule_new": "➕ جدولة منشور جديد",
        "btn_view_scheduled": "📝 عرض المنشورات المجدولة",
        "btn_recurring": "🔁 إدارة المنشورات المتكررة",
        "schedule_pick_post": "اختر مسوّدة منشور لجدولتها، أو اضغط ➕ لإنشاء جديدة:",
        "schedule_no_drafts": "📭 لا توجد مسوّدات. أنشئ منشورًا أولاً ثم احفظه كمسوّدة.",
        "schedule_time_prompt": (
            "🗓️ أرسل تاريخ ووقت النشر بالصيغة:\n"
            "`YYYY-MM-DD HH:MM`\n\n"
            "مثال: `2026-05-01 10:30`"
        ),
        "schedule_time_invalid": "❌ صيغة التاريخ غير صحيحة. استخدم: YYYY-MM-DD HH:MM",
        "schedule_time_past": "❌ الوقت المُدخل في الماضي. اختر وقتًا في المستقبل.",
        "schedule_success": "✅ تم جدولة المنشور للنشر في {when} (التوقيت: {tz}).",
        "scheduled_list_title": "📅 المنشورات المجدولة",
        "scheduled_list_empty": "📭 لا توجد منشورات مجدولة حاليًا.",
        "scheduled_item": "📄 منشور #{id} — ⏰ {when}",
        "btn_delete_scheduled": "🗑️ حذف",
        "scheduled_deleted": "✅ تم حذف المنشور المجدول.",
        # Recurring
        "recurring_menu_title": "🔁 إدارة المنشورات المتكررة",
        "recurring_menu_body": "هنا يمكنك إنشاء وإدارة المنشورات التي يتم نشرها بشكل دوري في قناتك.",
        "btn_recurring_new": "➕ إنشاء منشور متكرر جديد",
        "btn_recurring_view": "📝 عرض المنشورات المتكررة",
        "btn_recurring_edit": "✏️ تعديل منشور متكرر",
        "btn_recurring_delete": "🗑️ حذف منشور متكرر",
        "recurring_pick_freq": "حدّد تكرار النشر:",
        "btn_freq_daily": "☀️ يومي",
        "btn_freq_weekly": "🗓️ أسبوعي",
        "btn_freq_monthly": "📆 شهري",
        "recurring_time_prompt_daily": "أرسل الوقت اليومي للنشر بالصيغة `HH:MM` (مثال: `09:30`).",
        "recurring_time_prompt_weekly": "أرسل اليوم والوقت بالصيغة `DAY HH:MM`. الأيام: Mon Tue Wed Thu Fri Sat Sun. مثال: `Mon 10:00`",
        "recurring_time_prompt_monthly": "أرسل اليوم من الشهر والوقت بالصيغة `DAY HH:MM` (DAY من 1 إلى 28). مثال: `15 09:00`",
        "recurring_invalid": "❌ صيغة غير صحيحة. حاول مجددًا.",
        "recurring_success_daily": "✅ تم إعداد منشور متكرر يوميًا الساعة {time}.",
        "recurring_success_weekly": "✅ تم إعداد منشور متكرر كل {day} الساعة {time}.",
        "recurring_success_monthly": "✅ تم إعداد منشور متكرر يوم {day} من كل شهر الساعة {time}.",
        "recurring_ask_delete_timer": "هل تود إضافة مؤقت حذف للمنشور؟",
        "btn_add_delete_timer": "⏱️ إضافة مؤقت حذف",
        "btn_skip_delete_timer": "✅ لا، شكرًا",
        "delete_timer_prompt": "أرسل عدد الدقائق قبل حذف المنشور تلقائيًا (مثال: `60`).",
        "delete_timer_set": "✅ سيتم حذف كل نسخة بعد {minutes} دقيقة من النشر.",
        "recurring_list_title": "🔁 المنشورات المتكررة",
        "recurring_list_empty": "📭 لا توجد منشورات متكررة حاليًا.",
        "recurring_item_daily": "📄 #{id} — ☀️ يوميًا {time}",
        "recurring_item_weekly": "📄 #{id} — 🗓️ {day} {time}",
        "recurring_item_monthly": "📄 #{id} — 📆 يوم {day} الساعة {time}",
        "recurring_deleted": "✅ تم حذف المنشور المتكرر.",
        # Protection
        "protection_title": "🛡️ حماية القناة: {name}",
        "protection_body": "هنا يمكنك تفعيل وتخصيص إعدادات الحماية لقناتك. اختر الميزة التي تود إدارتها.",
        "btn_captcha": "🧠 الكابتشا: {state}",
        "btn_join_filters": "🚫 فلاتر الانضمام",
        "btn_word_filter": "🗑️ فلتر الكلمات المحظورة",
        "btn_block_bots": "🤖 حظر البوتات: {state}",
        "captcha_toggled": "✅ تم تحديث إعداد الكابتشا. الحالة الآن: {state}",
        "block_bots_toggled": "✅ تم تحديث إعداد حظر البوتات. الحالة الآن: {state}",
        "join_filters_title": "🚫 اختر نوع فلتر الانضمام الذي تود إدارته:",
        "btn_filter_total_ban": "⛔ حظر كلي",
        "btn_filter_multi_ban": "👨‍👩‍👦 حظر متعدد",
        "btn_filter_names": "🆎 فلتر الأسماء",
        "btn_filter_alphabet": "🕉️ فلتر الأبجدية",
        "name_filter_intro": "تفعيل فلتر الأسماء سيقوم بحظر المستخدمين الذين تحتوي أسماؤهم على كلمات محددة. هل تود تفعيل هذه الميزة؟",
        "btn_enable": "✅ تفعيل",
        "btn_disable": "❌ تعطيل",
        "name_filter_words_prompt": "أرسل الكلمات التي تود حظرها، كلمة واحدة في كل سطر.",
        "name_filter_saved": "✅ تم تفعيل فلتر الأسماء بنجاح. الكلمات المحظورة:\n{words}",
        "word_filter_prompt": "أرسل الكلمات المحظورة في التعليقات، كلمة واحدة في كل سطر. أرسل `-` لتعطيل الفلتر.",
        "word_filter_saved": "✅ تم حفظ فلتر الكلمات المحظورة ({count} كلمة).",
        "word_filter_disabled": "✅ تم تعطيل فلتر الكلمات.",
        # Statistics
        "stats_title": "📊 إحصائيات القناة: {name}",
        "stats_body": "اختر نوع الإحصائيات التي تود عرضها.",
        "btn_stat_growth": "📈 نمو المشتركين",
        "btn_stat_engagement": "❤️ تفاعل المنشورات",
        "btn_stat_views": "👁️ مشاهدات المنشورات",
        "btn_stat_top": "🔝 أفضل المنشورات",
        "stats_pick_period": "حدّد الفترة الزمنية:",
        "btn_period_today": "اليوم",
        "btn_period_7": "آخر 7 أيام",
        "btn_period_30": "آخر 30 يومًا",
        "btn_period_90": "آخر 90 يومًا",
        "stats_growth_caption": "📈 نمو المشتركين خلال {period}\n\nالحالي: {current} مشترك\nالتغيّر: {delta}",
        "stats_engagement_text": (
            "❤️ تفاعل المنشورات (آخر {n} منشور)\n\n"
            "متوسط المشاهدات: {avg_views}\n"
            "إجمالي المشاهدات: {total_views}\n"
            "عدد المنشورات المتتبعة: {tracked}"
        ),
        "stats_views_text": "👁️ مشاهدات المنشورات\n\n{lines}",
        "stats_top_text": "🔝 أفضل المنشورات أداءً:\n\n{lines}",
        "stats_no_data": "📭 لا توجد بيانات إحصائية كافية بعد. سيبدأ التتبع تلقائيًا من الآن.",
        # Settings
        "settings_title": "⚙️ إعدادات القناة: {name}",
        "settings_body": "اختر الإعداد الذي تود تعديله.",
        "btn_change_lang": "🌐 تغيير اللغة",
        "btn_timezone": "⏰ المنطقة الزمنية",
        "btn_signature": "✍️ التوقيع التلقائي",
        "btn_notifications": "🔔 إشعارات القناة: {state}",
        "lang_pick_title": "🌐 اختر لغة البوت لهذه القناة:",
        "btn_lang_ar": "🇸🇦 العربية",
        "btn_lang_en": "🇬🇧 English",
        "lang_changed": "✅ تم تغيير اللغة بنجاح.",
        "timezone_prompt": (
            "⏰ أرسل المنطقة الزمنية بصيغة IANA.\n\n"
            "أمثلة:\n"
            "• Asia/Riyadh\n"
            "• Africa/Cairo\n"
            "• Europe/Istanbul\n"
            "• UTC"
        ),
        "timezone_invalid": "❌ منطقة زمنية غير صحيحة. تأكد من الصيغة.",
        "timezone_saved": "✅ تم تعيين المنطقة الزمنية إلى: {tz}",
        "signature_ask_enable": "هل تود تفعيل التوقيع التلقائي للمنشورات؟",
        "signature_prompt": "أرسل نص التوقيع الذي تود إضافته تلقائيًا إلى نهاية كل منشور.",
        "signature_enabled": "✅ تم تفعيل التوقيع التلقائي. سيتم إضافة:\n«{text}»\nإلى نهاية كل منشور.",
        "signature_disabled": "✅ تم تعطيل التوقيع التلقائي.",
        "notifications_toggled": "✅ تم تحديث الإشعارات. الحالة الآن: {state}",
        # Admins
        "admins_title": "👤 إدارة المشرفين: {name}",
        "admins_body": "هنا يمكنك إدارة المشرفين على قناتك. اختر الإجراء الذي تود القيام به.",
        "btn_admin_add": "➕ إضافة مشرف جديد",
        "btn_admin_edit": "✏️ تعديل صلاحيات مشرف",
        "btn_admin_remove": "🗑️ إزالة مشرف",
        "btn_admin_view": "📝 عرض المشرفين الحاليين",
        "admin_add_prompt": "👤 أعد توجيه أي رسالة من المستخدم الذي تود إضافته كمشرف، أو أرسل @username الخاص به.",
        "admin_added": "✅ تم إضافة @{username} كمشرف بصلاحيات: {perms}",
        "admin_pick_perms": "حدّد الصلاحيات للمشرف الجديد @{username}:",
        "perm_publish": "نشر المنشورات",
        "perm_edit": "تعديل المنشورات",
        "perm_delete": "حذف المنشورات",
        "perm_protection": "إدارة الحماية",
        "perm_stats": "عرض الإحصائيات",
        "perm_settings": "إدارة الإعدادات",
        "btn_save_perms": "✅ حفظ الصلاحيات",
        "admins_list_title": "👤 المشرفون الحاليون:",
        "admins_list_empty": "📭 لا يوجد مشرفون مضافون داخل البوت بعد.",
        "admin_removed": "✅ تم إزالة المشرف @{username}",
        # Change channel/language
        "change_menu_title": "🌐 تغيير القناة/اللغة",
        "change_menu_body": "اختر القناة التي تود إدارتها أو قم بتغيير لغة البوت.",
        "btn_switch_channel": "🔄 تبديل القناة",
        "btn_change_bot_lang": "🌐 تغيير اللغة",
        "switched_channel": "✅ تم التبديل إلى القناة: {name}",
        # Developer
        "dev_title": "🛠️ إعدادات المطور",
        "dev_body": "مرحبًا أيها المطور! هنا يمكنك إدارة الإعدادات المتقدمة لبوت SmartChannelX. يرجى التعامل بحذر.",
        "btn_dev_apikeys": "🔑 إدارة مفاتيح API",
        "btn_dev_integrations": "🔗 إدارة التكاملات",
        "btn_dev_logs": "📜 سجلات الأخطاء",
        "btn_dev_restart": "🔄 إعادة تشغيل البوت",
        "dev_only": "⛔ هذه القائمة متاحة للمطورين فقط.",
        "dev_apikeys_title": "🔑 إدارة مفاتيح API",
        "dev_apikeys_empty": "📭 لا توجد مفاتيح API مسجّلة.",
        "btn_apikey_add": "➕ إضافة مفتاح API جديد",
        "btn_apikey_view": "📝 عرض مفاتيح API",
        "btn_apikey_delete": "🗑️ حذف مفتاح API",
        "apikey_prompt": "أرسل اسم الخدمة في السطر الأول ومفتاح API في السطر الثاني.\n\nمثال:\n```\nOpenAI\nsk-xxxxxxxxxxxx\n```",
        "apikey_added": "✅ تم إضافة مفتاح API لخدمة {name} بنجاح.",
        "apikey_invalid": "❌ صيغة غير صحيحة. يجب إرسال اسم الخدمة في سطر والمفتاح في سطر آخر.",
        "logs_title": "📜 آخر سجلات الأخطاء:\n\n```\n{logs}\n```",
        "logs_empty": "✅ لا توجد أخطاء مسجّلة.",
        "restart_confirm": "⚠️ سيتم إعادة تشغيل البوت. هذا الإجراء قد يستغرق بضع ثوانٍ.",
        # Errors / Confirmations
        "err_invalid_format": "⚠️ صيغة غير صحيحة. يرجى التأكد من استخدام الصيغة المطلوبة.",
        "err_generic": "❌ عذرًا، حدث خطأ ما. يرجى المحاولة مرة أخرى.",
        "err_not_admin": "⛔ يجب أن تكون مالك القناة أو مشرفًا فيها لاستخدام هذه الميزة.",
        "err_no_channel_selected": "⚠️ لم يتم اختيار قناة. اضغط 🏠 الرئيسية ثم اختر قناة.",
        "confirm_delete": "❓ هل أنت متأكد أنك تود حذف هذا العنصر؟ هذا الإجراء لا يمكن التراجع عنه.",
        "cancelled": "✅ تم إلغاء العملية.",
        "saved": "✅ تم الحفظ بنجاح!",
        # Misc
        "draft_label": "📄 منشور #{id} (مسوّدة)",
        "back_to_main": "🏠 العودة إلى القائمة الرئيسية…",
        "channel_locale_label": "[{name}]",
        # Generic operation labels
        "btn_op_add": "➕ إضافة",
        "btn_op_edit": "✏️ تعديل",
        "btn_op_delete": "🗑️ حذف",
        "btn_op_view": "👁 عرض",
        "btn_op_toggle": "⚙️ تفعيل/تعطيل",
        "btn_op_export": "📤 تصدير",
        "btn_op_filter": "🔍 فلترة",
        "btn_op_clear": "🧹 مسح الكل",
        "pick_channel_first": "اختر القناة أولًا:",
        "no_channels_global": "📭 لا توجد قنوات مسجّلة لديك. أضِف قناة أولًا من القائمة الرئيسية.",
        # ===== 📜 Event Log =====
        "btn_events": "📜 سجل الأحداث",
        "events_title": "📜 سجل أحداث القناة: {name}",
        "events_body": (
            "باستخدام هذه الميزة يمكنك مراقبة جميع الأحداث الرئيسية للقناة:\n"
            "نشر منشورات، إضافة/إزالة مشرفين، تغيّر صلاحياتي، انضمام/مغادرة الأعضاء…"
        ),
        "btn_events_view_all": "👁 عرض الكل",
        "btn_events_filter": "🔍 فلترة",
        "btn_events_export": "📤 تصدير",
        "btn_events_clear": "🧹 مسح السجل",
        "events_filter_title": "🔍 اختر نوع الفلتر:",
        "btn_filter_by_type": "حسب النوع",
        "btn_filter_by_user": "حسب المستخدم",
        "btn_filter_by_date": "حسب التاريخ",
        "btn_filter_reset": "♻️ إلغاء الفلتر",
        "events_filter_type_pick": "اختر نوع الحدث:",
        "ev_type_post_published": "📝 نشر منشور",
        "ev_type_post_scheduled": "⏰ جدولة منشور",
        "ev_type_admin_added": "👤➕ إضافة مشرف",
        "ev_type_admin_removed": "👤🗑️ إزالة مشرف",
        "ev_type_member_join": "🟢 عضو انضم",
        "ev_type_member_leave": "🔴 عضو غادر",
        "ev_type_settings_changed": "⚙️ تغيير إعدادات",
        "ev_type_protection_changed": "🛡️ تغيير الحماية",
        "ev_type_forward_sent": "🔁 إعادة توجيه",
        "ev_type_multisend": "📤 إرسال متعدد",
        "ev_type_other": "📌 أخرى",
        "events_filter_user_prompt": "أرسل المعرّف الرقمي للمستخدم الذي تريد فلترة أحداثه:",
        "events_filter_date_prompt": "أرسل عدد الأيام الماضية لعرض أحداثها (مثال: `7`):",
        "events_list_empty": "📭 لا توجد أحداث مسجّلة بعد.",
        "events_list_header": "📜 آخر {n} حدث:",
        "events_export_done": "✅ تم تجهيز ملف السجل.",
        "events_cleared": "✅ تم مسح كامل سجل القناة.",
        # ===== 🤖 Autocomplete =====
        "btn_autocomplete": "🤖 الإكمال التلقائي",
        "ac_title": "🤖 الإكمال التلقائي للقناة: {name}",
        "ac_body": (
            "في هذه القائمة يمكنك إعداد الإضافات التي ستُدرج تلقائيًا في كل رسالة "
            "تُرسلها يدويًا في القناة عبر هذا البوت.\n\n"
            "أنشئ مجموعات من إضافات الرسائل وستُطبَّق استنادًا إلى المرشحات (الكلمات المفتاحية) القابلة للتكوين."
        ),
        "ac_empty": "لم تقم بإنشاء أي إعداد إضافات بعد.",
        "btn_ac_add": "➕ إنشاء إعداد جديد",
        "btn_ac_view": "👁 عرض الإعدادات",
        "btn_ac_edit": "✏️ تعديل إعداد",
        "btn_ac_delete": "🗑️ حذف إعداد",
        "ac_name_prompt": "أرسل اسمًا قصيرًا لهذا الإعداد (مثال: `إعلان`، `ترحيب`):",
        "ac_created": "✅ تم إنشاء الإعداد «{name}». الآن أضف المرشحات والنصوص.",
        "ac_set_view": (
            "🤖 الإعداد: «{name}»\n"
            "الحالة: {state}\n\n"
            "🔍 المرشحات (كلمات تفعيل): {triggers}\n"
            "📜 نص قبل المنشور:\n{prefix}\n\n"
            "📜 نص بعد المنشور:\n{suffix}"
        ),
        "btn_ac_edit_triggers": "🔍 تعديل الكلمات المفتاحية",
        "btn_ac_edit_prefix": "⬆️ تعديل النص قبل",
        "btn_ac_edit_suffix": "⬇️ تعديل النص بعد",
        "btn_ac_toggle": "⚙️ تفعيل/تعطيل: {state}",
        "ac_triggers_prompt": (
            "🔍 أرسل الكلمات المفتاحية مفصولة بفواصل. عند مطابقة أي كلمة سيُطبَّق هذا الإعداد.\n\n"
            "اتركها فارغة (أرسل `-`) لتطبيقه على كل المنشورات."
        ),
        "ac_prefix_prompt": "⬆️ أرسل النص الذي سيُلصق قبل كل منشور (أو `-` للحذف):",
        "ac_suffix_prompt": "⬇️ أرسل النص الذي سيُلصق بعد كل منشور (أو `-` للحذف):",
        "ac_field_saved": "✅ تم حفظ التعديل.",
        "ac_deleted": "✅ تم حذف الإعداد.",
        "ac_toggled": "✅ تم تحديث الحالة: {state}",
        "ac_applied_note": "✨ تم تطبيق الإكمال التلقائي ({n} إعداد).",
        # ===== 📤 Multi-send =====
        "btn_multisend": "📤 الإرسال المتعدد",
        "ms_title": "📤 الإرسال المتعدد",
        "ms_body": (
            "يمكنك إرسال منشور واحد إلى عدّة قنوات في الوقت نفسه، أو جدولته ليُنشر تلقائيًا.\n"
            "اختر إجراءً للبدء."
        ),
        "btn_ms_new": "➕ إنشاء حملة جديدة",
        "btn_ms_view": "📋 عرض الحملات السابقة",
        "ms_pick_post_title": "📝 اختر المنشور (مسودة) من إحدى قنواتك:",
        "ms_no_drafts": "📭 لا توجد مسوّدات في أي قناة. أنشئ منشورًا أولًا.",
        "ms_pick_targets_title": "✅ اختر القنوات الوجهة (اضغط لإضافة/إزالة):",
        "btn_ms_target_select_all": "✔ اختيار كل القنوات",
        "btn_ms_target_clear": "✖ إلغاء الاختيار",
        "btn_ms_continue": "➡️ متابعة",
        "ms_when_title": "⏰ متى تريد الإرسال؟",
        "btn_ms_send_now": "🚀 الآن",
        "btn_ms_schedule": "📅 جدولة",
        "ms_schedule_prompt": "أرسل تاريخ ووقت الإرسال بصيغة `YYYY-MM-DD HH:MM`:",
        "ms_confirm": "📤 سيتم الإرسال إلى {n} قناة. تأكيد؟",
        "btn_ms_confirm": "✅ تأكيد الإرسال",
        "ms_done": "✅ اكتملت الحملة #{id}: نجح {ok}/{total}.",
        "ms_scheduled": "✅ تم جدولة الحملة #{id} للإرسال في {when}.",
        "ms_select_first": "⚠️ اختر قناة واحدة على الأقل.",
        "ms_jobs_title": "📋 حملات الإرسال السابقة:",
        "ms_jobs_empty": "📭 لا توجد حملات سابقة.",
        "ms_job_row": "#{id} • {when} • {status} • {ok}/{total}",
        "btn_ms_job_view": "👁 تفاصيل #{id}",
        "btn_ms_job_delete": "🗑️ حذف #{id}",
        "ms_job_detail": (
            "📤 تفاصيل الحملة #{id}\n"
            "📝 المنشور: #{post_id}\n"
            "🕒 المنشأة: {created}\n"
            "📅 الجدولة: {scheduled}\n"
            "📊 الحالة: {status}\n\n"
            "النتائج:\n{results}"
        ),
        # ===== 🔁 Forwarding =====
        "btn_forwarding": "🔁 إعادة التوجيه",
        "fw_title": "🔁 إعادة التوجيه من قناة: {name}",
        "fw_body": (
            "مع هذه الميزة يمكنك إعادة توجيه كل رسالة تُرسل يدويًا في قناتك إلى مجموعات أو قنوات أخرى.\n\n"
            "أضف قاعدة جديدة لتحديد الوجهة والفلتر."
        ),
        "btn_fw_add": "➕ إضافة قاعدة توجيه",
        "btn_fw_view": "👁 عرض القواعد",
        "fw_target_prompt": (
            "🎯 أرسل وجهة إعادة التوجيه:\n\n"
            "• `@channelname` — لقناة عامة\n"
            "• `-1001234567890` — لمعرّف رقمي\n\n"
            "تأكّد أنني عضو/مشرف في الوجهة قبل البدء."
        ),
        "fw_filter_prompt": (
            "🔍 أرسل كلمة فلترة (سيُعاد توجيه فقط الرسائل التي تحتوي عليها).\n\n"
            "أرسل `-` لإعادة توجيه كل الرسائل بدون فلتر."
        ),
        "fw_added": "✅ تم إضافة قاعدة التوجيه إلى {target}.",
        "fw_target_invalid": "❌ وجهة غير صحيحة أو لا أملك صلاحية الوصول إليها.",
        "fw_list_empty": "📭 لا توجد قواعد توجيه بعد.",
        "fw_list_title": "🔁 قواعد التوجيه الحالية:",
        "fw_rule_row": "🎯 {target}{filter} • {state}",
        "fw_filter_label": " | فلتر: «{f}»",
        "btn_fw_toggle": "⚙️ {state}",
        "btn_fw_edit": "✏️ تعديل #{id}",
        "btn_fw_delete": "🗑️ حذف #{id}",
        "fw_deleted": "✅ تم حذف القاعدة.",
        "fw_toggled": "✅ تم تحديث الحالة: {state}",
        "fw_edit_pick": "✏️ ماذا تريد تعديله؟",
        "btn_fw_edit_target": "🎯 تعديل الوجهة",
        "btn_fw_edit_filter": "🔍 تعديل الفلتر",
        "fw_forwarded_note": "🔁 تمت إعادة التوجيه إلى {n} وجهة.",
        # ===== 👋 Goodbye =====
        "btn_goodbye": "👋 رسالة الوداع",
        "gb_title": "👋 إعدادات رسالة الوداع: {name}",
        "gb_body": (
            "في هذه القائمة يمكنك تخصيص رسالة الوداع التي تظهر عند مغادرة عضو، "
            "وتفعيل خيار حظر الأعضاء الذين يغادرون لتجنّب رجوعهم.\n\n"
            "🔘 الحالة: {enabled}\n"
            "📝 الرسالة:\n{message}\n\n"
            "🚫 حظر عند المغادرة: {ban}"
        ),
        "btn_gb_toggle": "⚙️ تفعيل/تعطيل الوداع",
        "btn_gb_set_message": "✏️ تعديل نص الرسالة",
        "btn_gb_toggle_ban": "🚫 تبديل حظر المغادرين",
        "btn_gb_view": "👁 معاينة الرسالة",
        "btn_gb_delete": "🗑️ حذف الرسالة",
        "gb_message_prompt": (
            "✏️ أرسل نص رسالة الوداع.\n\n"
            "متغيرات متاحة:\n"
            "• `{name}` اسم العضو\n"
            "• `{username}` معرّف العضو\n"
            "• `{channel}` اسم القناة"
        ),
        "gb_message_set": "✅ تم حفظ نص رسالة الوداع.",
        "gb_message_none": "—",
        "gb_toggled": "✅ تم تحديث الحالة: {state}",
        "gb_ban_toggled": "✅ خيار الحظر عند المغادرة: {state}",
        "gb_message_deleted": "✅ تم حذف نص الرسالة.",
        "gb_preview_title": "👁 معاينة:",
        # ===== 🆘 Support =====
        "btn_support": "🆘 الدعم",
        "sup_title": "🆘 مركز الدعم",
        "sup_body": (
            "هنا يمكنك التواصل مع فريق الدعم بنظام تذاكر منظّم.\n"
            "افتح تذكرة جديدة، أو راجع تذاكرك السابقة وردود الفريق."
        ),
        "btn_sup_new": "➕ فتح تذكرة جديدة",
        "btn_sup_my": "📋 تذاكري",
        "btn_sup_admin_open": "📥 التذاكر المفتوحة (للإدارة)",
        "sup_subject_prompt": "📝 أرسل عنوان مختصر للتذكرة (سطر واحد):",
        "sup_body_prompt": "📨 أرسل الآن وصفًا تفصيليًا للمشكلة أو الاستفسار:",
        "sup_created": "✅ تم فتح التذكرة #{id}. سيردّ عليك الفريق في أقرب وقت.",
        "sup_my_empty": "📭 ليس لديك تذاكر بعد.",
        "sup_my_title": "📋 تذاكرك:",
        "sup_ticket_row": "#{id} • {subject} • {status}",
        "btn_sup_open_ticket": "👁 #{id}",
        "btn_sup_reply": "💬 رد",
        "btn_sup_close": "🔒 إغلاق",
        "btn_sup_reopen": "🔓 إعادة فتح",
        "sup_ticket_view": (
            "🎫 تذكرة #{id}\n"
            "📌 العنوان: {subject}\n"
            "📊 الحالة: {status}\n"
            "🕒 آخر تحديث: {updated}\n\n"
            "💬 المحادثة:\n{thread}"
        ),
        "sup_thread_user": "👤 أنت ({when}):\n{body}",
        "sup_thread_staff": "🧑‍💼 الدعم ({when}):\n{body}",
        "sup_reply_prompt": "💬 أرسل ردّك على التذكرة #{id}:",
        "sup_reply_sent": "✅ تم إرسال الرد.",
        "sup_status_open": "🟢 مفتوحة",
        "sup_status_closed": "🔒 مغلقة",
        "sup_closed": "✅ تم إغلاق التذكرة.",
        "sup_reopened": "✅ تم إعادة فتح التذكرة.",
        "sup_admin_open_title": "📥 التذاكر المفتوحة:",
        "sup_admin_open_empty": "✨ لا توجد تذاكر مفتوحة الآن.",
        "sup_notify_user": "📨 رد جديد على تذكرتك #{id}:\n\n{body}",
        "sup_notify_staff": "🆕 تذكرة دعم جديدة #{id} من المستخدم {user}:\n📌 {subject}",
        # ===== 🤖➕ Create bot =====
        "btn_createbot": "🤖➕ إنشاء بوت",
        "cb_title": "🤖➕ إدارة البوتات الفرعية",
        "cb_body": (
            "هنا يمكنك ربط بوتاتك الخاصة المُنشأة عبر @BotFather لإدارتها مركزيًا.\n\n"
            "1️⃣ افتح @BotFather في تيليجرام.\n"
            "2️⃣ أنشئ بوتًا جديدًا عبر /newbot واحصل على التوكن.\n"
            "3️⃣ ارجع هنا واضغط ➕ لإضافته."
        ),
        "btn_cb_add": "➕ إضافة بوت بالتوكن",
        "btn_cb_view": "👁 بوتاتي",
        "cb_token_prompt": (
            "🔐 أرسل توكن البوت من @BotFather بالصيغة:\n"
            "`123456:ABC-DEF1234ghIkl...`\n\n"
            "🔒 لن يُعرض التوكن لأحد غيرك."
        ),
        "cb_token_invalid": "❌ التوكن غير صالح أو رفضه تيليجرام.",
        "cb_added": "✅ تم ربط البوت @{username} بنجاح.",
        "cb_list_empty": "📭 لا توجد بوتات فرعية مرتبطة بعد.",
        "cb_list_title": "🤖 بوتاتك الفرعية:",
        "cb_row": "🤖 @{username} • {state}",
        "btn_cb_open": "👁 @{username}",
        "btn_cb_toggle": "⚙️ {state}",
        "btn_cb_delete": "🗑️ حذف",
        "cb_view": (
            "🤖 @{username}\n"
            "🆔 ID: `{bot_id}`\n"
            "🔑 توكن: `{masked}`\n"
            "📊 الحالة: {state}\n"
            "🕒 منذ: {created}"
        ),
        "cb_deleted": "✅ تم حذف البوت من القائمة.",
        "cb_toggled": "✅ تم تحديث الحالة: {state}",
        # ===== 📘 Bot Guide =====
        "btn_guide": "📘 دليل البوت",
        "guide_title": "📘 دليل البوت SmartChannelX",
        "guide_body": "اختر القسم الذي تريد دليله:",
        "btn_guide_overview": "🏠 نظرة عامة",
        "btn_guide_channels": "📢 القنوات",
        "btn_guide_posts": "📝 المنشورات",
        "btn_guide_schedule": "📅 الجدولة",
        "btn_guide_protection": "🛡️ الحماية",
        "btn_guide_stats": "📊 الإحصائيات",
        "btn_guide_admins": "👤 المشرفين",
        "btn_guide_advanced": "🤖 الأدوات المتقدمة",
        "btn_guide_faq": "❓ الأسئلة الشائعة",
        "guide_overview": (
            "🏠 نظرة عامة\n\n"
            "SmartChannelX هو نظام إدارة قنوات تيليجرام احترافي، يجمع بين:\n"
            "• إنشاء وجدولة وتكرار المنشورات\n"
            "• حماية متقدمة (كابتشا، فلاتر، حظر بوتات)\n"
            "• إحصائيات نمو وتفاعل\n"
            "• إدارة مشرفين بصلاحيات دقيقة\n"
            "• 9 أدوات متقدمة: سجل أحداث، إكمال تلقائي، إرسال متعدد، إعادة توجيه، رسالة وداع، دعم، بوتات فرعية، اشتراك إجباري، دليل."
        ),
        "guide_channels": (
            "📢 القنوات\n\n"
            "• إضافة قناة بـ 6 طرق: زر مباشر، @username، رسالة موجَّهة، Chat ID، رابط t.me، أو إضافة تلقائية عند ترقيتي.\n"
            "• قائمة القنوات تعرض شارة الحالة الفعلية: 👑 مالك، ✅ مشرف، ⚠️ عضو، ❌ خارج، ❔ غير معروف.\n"
            "• /verify لفحص جميع قنواتك دفعة واحدة."
        ),
        "guide_posts": (
            "📝 المنشورات\n\n"
            "• أرسل نصًا/صورة/فيديو/ملفًا.\n"
            "• أضف أزرار رابط (Text - URL).\n"
            "• خيارات متقدمة: التوقيع التلقائي، تنسيق HTML/Markdown، تعطيل معاينة الروابط.\n"
            "• معاينة قبل النشر، ثم: نشر فوري / جدولة / تكرار."
        ),
        "guide_schedule": (
            "📅 الجدولة والتكرار\n\n"
            "• جدولة فردية بصيغة `YYYY-MM-DD HH:MM`.\n"
            "• تكرار يومي/أسبوعي/شهري.\n"
            "• مؤقت حذف تلقائي لكل نسخة."
        ),
        "guide_protection": (
            "🛡️ الحماية\n\n"
            "• 🧠 كابتشا للأعضاء الجدد في المجموعات.\n"
            "• 🚫 فلاتر انضمام (حظر كلي، حظر متعدد، فلتر أسماء، فلتر أبجدية).\n"
            "• 🗑️ فلتر كلمات محظورة في التعليقات.\n"
            "• 🤖 حظر البوتات تلقائيًا."
        ),
        "guide_stats": (
            "📊 الإحصائيات\n\n"
            "• 📈 نمو المشتركين (يومي/أسبوعي/شهري) مع رسم بياني.\n"
            "• ❤️ تفاعل المنشورات.\n"
            "• 👁️ مشاهدات حسب المنشور.\n"
            "• 🔝 أفضل المنشورات."
        ),
        "guide_admins": (
            "👤 المشرفين\n\n"
            "أضف مشرفين داخل البوت بصلاحيات: نشر، تعديل، حذف، حماية، إحصائيات، إعدادات.\n"
            "كل صلاحية مستقلة وقابلة للتعديل."
        ),
        "guide_advanced": (
            "🤖 الأدوات المتقدمة\n\n"
            "• 📜 سجل الأحداث: تتبّع كل العمليات.\n"
            "• 🤖 الإكمال التلقائي: نص قبل/بعد المنشورات.\n"
            "• 📤 الإرسال المتعدد: حملة لعدة قنوات.\n"
            "• 🔁 إعادة التوجيه: مزامنة بين القنوات.\n"
            "• 👋 رسالة الوداع.\n"
            "• 🆘 الدعم: نظام تذاكر.\n"
            "• 🤖➕ إنشاء بوت: اربط بوتاتك من @BotFather.\n"
            "• ⭐ الاشتراك الإجباري."
        ),
        "guide_faq": (
            "❓ الأسئلة الشائعة\n\n"
            "س: لماذا لا يستجيب البوت في قناتي؟\n"
            "ج: تأكد أنني مشرف بصلاحية «نشر». استخدم /verify.\n\n"
            "س: لماذا لا تصل الرسالة الخاصة عند إضافة قناة؟\n"
            "ج: ابدأ محادثة معي عبر /start في الخاص أولًا.\n\n"
            "س: كيف أنقل ملكية البوت؟\n"
            "ج: من قائمة المشرفين أضف المستخدم بصلاحيات كاملة.\n\n"
            "س: هل تحفظ كلمات المرور أو التوكنات؟\n"
            "ج: التوكنات مشفّرة بإخفاء جزئي ولا تُعرض إلا لك."
        ),
        # ===== ⭐ Subscription =====
        "btn_subscription": "⭐ الاشتراك",
        "sub_title": "⭐ الاشتراك الإجباري للقناة: {name}",
        "sub_body": (
            "اربط قنوات اشتراك إجبارية يجب أن يكون أعضاء قناتك مشتركين فيها.\n"
            "يمكنك إضافة قنوات متعددة، تفعيل/تعطيل أي منها، أو حذفها."
        ),
        "btn_sub_add": "➕ إضافة قناة اشتراك",
        "btn_sub_view": "👁 عرض القنوات",
        "btn_sub_check": "🔎 فحص اشتراك مستخدم",
        "sub_add_prompt": (
            "🔗 أرسل القناة المطلوب الاشتراك بها:\n"
            "• `@username`\n"
            "• أو معرّف رقمي `-100…`\n\n"
            "تأكّد أنني عضو في تلك القناة لأستطيع التحقّق."
        ),
        "sub_added": "✅ تم إضافة قناة الاشتراك «{title}».",
        "sub_invalid": "❌ تعذّر التحقق من القناة.",
        "sub_list_empty": "📭 لا توجد قنوات اشتراك مرتبطة.",
        "sub_list_title": "⭐ قنوات الاشتراك المرتبطة:",
        "sub_row": "📡 {title} • {ref} • {state}",
        "btn_sub_toggle": "⚙️ {state}",
        "btn_sub_delete": "🗑️ حذف",
        "sub_deleted": "✅ تم حذف القناة من القائمة.",
        "sub_toggled": "✅ تم تحديث الحالة: {state}",
        "sub_check_prompt": "أرسل المعرّف الرقمي للمستخدم لفحص اشتراكه:",
        "sub_check_result": "نتيجة الفحص للمستخدم {user}:\n\n{lines}",
        "sub_check_ok": "✅ مشترك في {ref}",
        "sub_check_no": "❌ غير مشترك في {ref}",
        "sub_check_err": "❔ تعذّر الفحص لـ {ref}: {err}",
        # Aliases / new keys for the 9 sections
        "err_not_staff": "❌ هذا الإجراء متاح لفريق الدعم فقط.",
        "ms_pick_post": "📝 اختر منشورًا (مسودة) للإرسال:",
        "ms_pick_targets": "✅ اختر القنوات الوجهة (اضغط للإضافة/الإزالة):\n\n📄 {preview}",
        "ms_no_targets": "⚠️ اختر قناة واحدة على الأقل.",
        "ms_when_prompt": "⏰ متى تريد الإرسال؟",
        "ms_when_now": "الآن",
        "ms_dispatched": "✅ تم إرسال/جدولة الحملة #{id}.",
        "ms_jobs_header": "📋 آخر {n} حملة:",
        "ms_job_line": "#{id} • {status} • {n} قناة • {when}",
        "ms_job_view": "📋 الحملة #{id}\nالحالة: {status}\nعدد القنوات: {n}\nنجح: {ok} | فشل: {fail}",
        "fw_empty": "📭 لا توجد قواعد توجيه بعد.",
        "fw_list_header": "🔁 لديك {n} قاعدة توجيه:",
        "fw_add_target_prompt": "📝 أرسل وجهة التوجيه (`@username` أو معرّف رقمي):",
        "fw_add_filter_prompt": "🧪 أرسل كلمة فلترة اختيارية، أو `-` لتمرير كل المنشورات:",
        "fw_updated": "✅ تم تحديث القاعدة.",
        "gb_current_message": "📝 الرسالة الحالية:\n{msg}",
        "gb_no_message": "(لم يتم تعيين رسالة بعد)",
        "gb_msg_prompt": (
            "📝 أرسل نص رسالة الوداع.\n"
            "متغيرات متاحة: `{name}` `{username}` `{id}`."
        ),
        "gb_view": "👁 معاينة:\n\n{msg}",
        "gb_saved": "✅ تم حفظ رسالة الوداع.",
        "sup_no_tickets": "📭 لا توجد لديك تذاكر.",
        "sup_my_header": "🎫 تذاكرك ({n}):",
        "sup_no_open": "✅ لا توجد تذاكر مفتوحة.",
        "sup_open_header": "🆘 التذاكر المفتوحة ({n}):",
        "sup_staff_notify": "🆘 تذكرة جديدة #{id}: {subject}",
        "sup_staff_replied": "💬 رد جديد على تذكرتك #{id}.",
        "cb_invalid_token": "❌ صيغة التوكن غير صحيحة. حاول مرة أخرى.",
        "cb_token_failed": "❌ فشل التحقق من التوكن: {err}",
        "cb_empty": "📭 لا توجد بوتات مسجّلة بعد.",
        "cb_list_header": "🤖 بوتاتك ({n}):",
        "guide_section_overview": (
            "🌟 SmartChannelX هو مساعدك الذكي لإدارة قنوات تيليجرام.\n"
            "يمكنك إنشاء وجدولة المنشورات، حماية القناة، تحليل الإحصائيات، "
            "إدارة المشرفين والمزيد."
        ),
        "guide_section_channels": (
            "📢 لإضافة قناة، اضغط (إضافة قناة/مجموعة) ثم اختر طريقة الإضافة.\n"
            "يمكنك إضافة عبر معرّف، رابط، توجيه رسالة، أو اسم المستخدم."
        ),
        "guide_section_posts": (
            "📝 لإنشاء منشور، اختر قناتك ثم (إنشاء منشور).\n"
            "يدعم النص، الصور، الفيديو، الملفات، الأزرار، والتنسيق."
        ),
        "guide_section_schedule": (
            "📅 يمكنك جدولة المنشورات لوقت لاحق أو تكرارها يومياً/أسبوعياً.\n"
            "كما تتوفر إعادة الإرسال التلقائي للقنوات."
        ),
        "guide_section_protection": (
            "🛡 الحماية: فلترة الكلمات، فحص أسماء الأعضاء، حظر البوتات، "
            "كابتشا، وحماية من الفيضان."
        ),
        "guide_section_stats": (
            "📊 الإحصائيات: عدد المنشورات، الأعضاء، التفاعل، والعمليات."
        ),
        "guide_section_admins": (
            "👥 يمكنك إضافة مشرفين على مستوى البوت لمساعدتك في إدارة قنواتك."
        ),
        "guide_section_advanced": (
            "🤖 الميزات المتقدمة:\n"
            "• 📤 الإرسال المتعدد لعدة قنوات دفعة واحدة\n"
            "• 🔁 إعادة التوجيه التلقائي\n"
            "• 👋 رسائل الوداع\n"
            "• ⭐ الاشتراك الإجباري"
        ),
        "guide_section_faq": (
            "❓ الأسئلة الشائعة:\n"
            "س: لماذا لا يستطيع البوت النشر؟\n"
            "ج: تأكد من إضافته كمشرف بصلاحية النشر.\n\n"
            "س: كيف أغيّر اللغة؟\n"
            "ج: من القائمة الرئيسية ← اللغة."
        ),
        "sub_empty": "📭 لا توجد قنوات اشتراك بعد.",
        "sub_list_header": "⭐ {n} قناة اشتراك:",
        "sub_check_done": "🧪 نتيجة الفحص للمستخدم {uid}: {state}",
        "sub_check_pass": "✅ مكتملة",
        "sub_check_fail": "❌ ناقصة",
        "sub_no_active": "(لا توجد قواعد اشتراك مفعّلة)",
        # ===== Channel Management - New Keys =====
        "btn_channel_info": "ℹ️ تفاصيل القناة",
        "btn_delete_channel": "🗑️ حذف القناة من البوت",
        "btn_refresh_channel": "🔄 تحديث البيانات",
        "btn_delete_confirm": "⚠️ نعم، احذف القناة",
        "btn_delete_cancel": "❌ إلغاء",
        "channel_info_title": "ℹ️ تفاصيل القناة",
        "channel_info_body": (
            "📢 الاسم: {title}\n"
            "🔗 المعرّف: {username}\n"
            "🆔 Chat ID: {chat_id}\n"
            "📅 تاريخ الإضافة: {created}\n\n"
            "📊 الإحصائيات:\n"
            "  📝 المنشورات الكلية: {posts}\n"
            "  ⏰ مجدولة (قيد الانتظار): {scheduled}\n"
            "  🔁 متكررة (مفعّلة): {recurring}\n"
            "  📤 تم نشرها: {publications}"
        ),
        "channel_delete_confirm": (
            "⚠️ تحذير! أنت على وشك حذف القناة:\n\n"
            "📢 {name}\n\n"
            "سيتم حذف جميع البيانات المرتبطة بها (المنشورات، الجداول، الإعدادات) بشكل نهائي.\n\n"
            "هل أنت متأكد؟"
        ),
        "channel_deleted": "✅ تم حذف القناة «{name}» من البوت بنجاح.",
        "channel_refreshed": "✅ تم تحديث بيانات القناة «{name}» بنجاح.",
        "channel_refresh_failed": "❌ تعذّر تحديث بيانات القناة. تأكد أن البوت لا يزال مشرفًا فيها.",
        "change_channel_title": "🔀 تغيير القناة الحالية",
        "change_channel_body": "اختر القناة التي تريد الانتقال إليها:",
        "channels_list_with_stats": "⚙️ قنواتك المضافة ({count} قناة)\n\nاختر قناة لإدارتها:",
        # ===== Scheduling - Enhanced Keys (AR) =====
        "sched_dashboard_title": (
            "📅 لوحة جدولة المنشورات\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📊 الإحصائيات:\n"
            "  ⏰ مجدولة قيد الانتظار: {pending}\n"
            "  🔁 متكررة مفعّلة: {recurring}\n"
            "  📝 مسودّات جاهزة: {drafts}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "اختر الإجراء الذي تريد القيام به:"
        ),
        "btn_sched_new_post": "✍️ إنشاء منشور وجدولته",
        "btn_sched_from_draft": "📋 جدولة من مسودة",
        "btn_sched_view_list": "📅 المنشورات المجدولة",
        "btn_sched_recurring": "🔁 المنشورات المتكررة",
        "btn_sched_drafts": "🗂️ عرض المسودّات",
        "sched_quick_time_title": (
            "⚡ اختر وقت النشر السريع:\n\n"
            "أو أرسل تاريخ ووقتًا يدويًا بالصيغة:\n"
            "`YYYY-MM-DD HH:MM`\n\n"
            "مثال: `2026-05-01 14:30`\n\n"
            "📍 توقيتك الحالي: {now} ({tz})"
        ),
        "btn_plus_1h": "⏱ +1 ساعة",
        "btn_plus_3h": "⏱ +3 ساعات",
        "btn_plus_6h": "⏱ +6 ساعات",
        "btn_plus_12h": "⏱ +12 ساعة",
        "btn_plus_24h": "⏱ +24 ساعة",
        "btn_tomorrow_same": "🌅 غداً نفس الوقت",
        "btn_next_week": "📆 الأسبوع القادم",
        "sched_list_title": "📅 المنشورات المجدولة ({count} منشور)\n\nاختر منشورًا لإدارته:",
        "sched_item_line": "📄 #{id} — {type} — ⏰ {when}",
        "sched_view_title": (
            "📄 تفاصيل المنشور المجدول\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🆔 المعرّف: #{id}\n"
            "📝 النوع: {type}\n"
            "⏰ موعد النشر: {when}\n"
            "🌍 التوقيت: {tz}\n"
            "📊 الحالة: {status}"
        ),
        "btn_sched_view_content": "👁 معاينة المحتوى",
        "btn_sched_postpone": "⏭ تأجيل الموعد",
        "btn_sched_delete": "🗑️ إلغاء الجدولة",
        "btn_sched_publish_now": "🚀 نشر الآن",
        "sched_postpone_title": "⏭ اختر مدة التأجيل:\n\nالموعد الحالي: {when}",
        "btn_postpone_1h": "⏱ +1 ساعة",
        "btn_postpone_3h": "⏱ +3 ساعات",
        "btn_postpone_24h": "⏱ +24 ساعة",
        "btn_postpone_custom": "✏️ وقت مخصص",
        "sched_postponed": "✅ تم تأجيل المنشور #{id} إلى {when}.",
        "sched_delete_confirm": "⚠️ سيتم إلغاء جدولة المنشور #{id} (الموعد: {when}). هل أنت متأكد؟",
        "btn_sched_del_confirm": "✅ نعم، إلغاء الجدولة",
        "btn_sched_del_cancel": "❌ لا، إبقاءه",
        "sched_deleted_ok": "✅ تم إلغاء جدولة المنشور #{id} بنجاح.",
        "sched_no_drafts_hint": (
            "📭 لا توجد مسوّدات جاهزة للجدولة.\n\n"
            "💡 لإنشاء منشور مجدول:\n"
            "1️⃣ اضغط على ✍️ إنشاء منشور وجدولته\n"
            "2️⃣ أرسل المحتوى → اختر «جدولة النشر»"
        ),
        "rec_toggle_enabled": "✅ تم تفعيل المنشور المتكرر #{id}.",
        "rec_toggle_disabled": "⏸ تم إيقاف المنشور المتكرر #{id} مؤقتًا.",
        "btn_rec_toggle_on": "✅ تفعيل",
        "btn_rec_toggle_off": "⏸ إيقاف مؤقت",
        "rec_view_title": (
            "🔁 تفاصيل المنشور المتكرر\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🆔 المعرّف: #{id}\n"
            "📅 التكرار: {freq}\n"
            "⏰ الوقت: {time}\n"
            "🗑 مؤقت الحذف: {timer}\n"
            "📊 الحالة: {status}"
        ),
        "rec_status_active": "🟢 مفعّل",
        "rec_status_paused": "⏸ موقوف",
        "rec_timer_none": "لا يوجد",
        "rec_timer_set": "{min} دقيقة بعد النشر",
        "btn_rec_view": "👁 عرض التفاصيل",
        "btn_rec_delete": "🗑️ حذف نهائي",
        "drafts_list_title": "🗂️ المسودّات المتاحة ({count} مسوّدة):",
        "draft_item": "📄 #{id} — {type} — {preview}",
        "draft_no_text": "(وسائط بدون نص)",
    },
    "en": {
        "welcome_title": "👋 Welcome to SmartChannelX!",
        "welcome_body": (
            "I am your smart assistant for managing Telegram channels professionally and easily. "
            "Whether you want to schedule posts, protect your channel, analyze statistics, or "
            "customize the subscriber experience — SmartChannelX gives you all the tools you need.\n\n"
            "🚀 Start managing your channels efficiently right now!\n\n"
            "To begin, please add your channel or pick one of the channels you manage."
        ),
        "btn_add_channel": "➕ Add New Channel",
        "btn_my_channels": "⚙️ My Channels",
        "btn_help": "❓ Help",
        "btn_back": "🔙 Back",
        "btn_home": "🏠 Home",
        "btn_cancel": "❌ Cancel",
        "btn_yes": "✅ Yes",
        "btn_no": "❌ No",
        "channel_menu_title": "✨ Welcome to channel dashboard: {name}",
        "channel_menu_body": "Pick the action you'd like to perform. You can return here or cancel any operation at any time.",
        "btn_create_post": "📝 Create New Post",
        "btn_schedule_posts": "📅 Schedule Posts",
        "btn_protection": "🛡️ Channel Protection",
        "btn_statistics": "📊 Channel Statistics",
        "btn_channel_settings": "⚙️ Channel Settings",
        "btn_admins": "👤 Admin Management",
        "btn_change_channel": "🌐 Change Channel/Language",
        "no_channels": (
            "📭 No channels added yet.\n\n"
            "To add a channel:\n"
            "1️⃣ Add this bot as admin to your channel with post permission.\n"
            "2️⃣ Then tap ➕ Add New Channel."
        ),
        "channels_list_title": "⚙️ Your channels\n\nPick a channel to manage:",
        "add_channel_prompt": (
            "➕ Add New Channel or Group\n\n"
            "Pick the easiest method below. You can add me as admin in a channel or group "
            "with one tap, or register an existing chat manually."
        ),
        "btn_add_to_channel_admin": "📢 Add me as admin to a channel",
        "btn_add_to_group_admin": "👥 Add me as admin to a group",
        "btn_add_via_username": "🔤 Add by @username",
        "btn_add_via_forward": "↪️ Add by forwarded message",
        "btn_add_via_id": "🔢 Add by Chat ID",
        "btn_add_via_link": "🔗 Add by t.me link",
        "add_channel_methods_help": (
            "💡 Notes:\n"
            "• Private channels: use «Add me as admin» button or forward a message.\n"
            "• Pick permissions: post, edit, delete, invite, ban, manage video chats.\n"
            "• After adding me you'll get a confirmation automatically — no need to type anything."
        ),
        "add_via_username_prompt": (
            "🔤 Send the public username of the channel or group:\n\n"
            "Example: `@mychannel`\n\n"
            "Make sure I'm an admin first."
        ),
        "add_via_forward_prompt": (
            "↪️ Forward any message from the channel or group you want to add.\n\n"
            "(Forwarded messages must be enabled in the channel privacy settings)."
        ),
        "add_via_id_prompt": (
            "🔢 Send the chat ID of the channel or group:\n\n"
            "Example: `-1001234567890`"
        ),
        "add_via_link_prompt": (
            "🔗 Send the channel or group link, e.g.:\n\n"
            "`https://t.me/mychannel`\n"
            "or\n"
            "`https://t.me/joinchat/...`\n\n"
            "Note: private invite links require me to be admin first."
        ),
        "add_channel_success": "✅ Channel added successfully: {name}",
        "add_channel_auto_registered": (
            "🎉 I was auto-detected in {chat_type}: {name}\n\n"
            "It has been registered to your account. Manage it via /start."
        ),
        "add_channel_failed": "❌ Could not add channel. Make sure the bot is an admin and the identifier is correct.",
        "add_channel_not_admin": (
            "⚠️ I must be an admin in «{name}» before you can manage it.\n\n"
            "Promote me as admin and try again."
        ),
        "add_channel_already": "ℹ️ This channel is already registered: {name}",
        "add_channel_user_not_admin": (
            "⛔ To add «{name}» you must be its owner or an admin in it."
        ),
        "chat_type_channel": "channel",
        "chat_type_group": "group",
        "chat_type_supergroup": "supergroup",
        "bot_demoted_in_chat": "⚠️ I was demoted in «{name}». I can no longer manage it.",
        "bot_removed_from_chat": "ℹ️ I was removed from «{name}». Management disabled.",
        # Verify status
        "btn_verify_admin": "🔄 Verify my permissions",
        "btn_verify_all": "🩺 Check all channels",
        "verify_status_admin": "✅ I am admin in «{name}»",
        "verify_status_owner": "👑 I am the owner of «{name}»",
        "verify_status_member": "⚠️ I am only a member of «{name}» — please promote me to admin.",
        "verify_status_left": "❌ I am not a member of «{name}». Add me again.",
        "verify_status_unknown": "❔ I cannot reach «{name}». Make sure I'm still inside.",
        "verify_perms_title": "🔐 Granted permissions:",
        "verify_perms_none": "🔒 I have no admin permissions enabled.",
        "verify_error": "❗ Error: {error}",
        "verify_all_title": "🩺 Status of all your channels:",
        "verify_all_empty": "📭 No channels to check. Add one first.",
        "channel_status_header": "📊 Current status:",
        "verify_chat_added_channel": (
            "✅ I have been activated in this channel!\n\n"
            "I'm now an admin and ready for management commands. "
            "Open my private chat to manage the channel."
        ),
        # ===== Channel Management - New Keys (EN) =====
        "btn_channel_info": "ℹ️ Channel Details",
        "btn_delete_channel": "🗑️ Remove Channel from Bot",
        "btn_refresh_channel": "🔄 Refresh Data",
        "btn_delete_confirm": "⚠️ Yes, Delete Channel",
        "btn_delete_cancel": "❌ Cancel",
        "channel_info_title": "ℹ️ Channel Details",
        "channel_info_body": (
            "📢 Name: {title}\n"
            "🔗 Username: {username}\n"
            "🆔 Chat ID: {chat_id}\n"
            "📅 Added: {created}\n\n"
            "📊 Stats:\n"
            "  📝 Total posts: {posts}\n"
            "  ⏰ Scheduled (pending): {scheduled}\n"
            "  🔁 Recurring (active): {recurring}\n"
            "  📤 Published: {publications}"
        ),
        "channel_delete_confirm": (
            "⚠️ Warning! You are about to remove the channel:\n\n"
            "📢 {name}\n\n"
            "All associated data (posts, schedules, settings) will be permanently deleted.\n\n"
            "Are you sure?"
        ),
        "channel_deleted": "✅ Channel «{name}» removed from the bot successfully.",
        "channel_refreshed": "✅ Channel «{name}» data refreshed successfully.",
        "channel_refresh_failed": "❌ Could not refresh channel data. Make sure the bot is still an admin.",
        "change_channel_title": "🔀 Switch Channel",
        "change_channel_body": "Pick the channel you want to switch to:",
        "channels_list_with_stats": "⚙️ Your Channels ({count} channels)\n\nPick a channel to manage:",
        "verify_chat_added_group": (
            "✅ I have been activated in this group!\n\n"
            "I'm now an admin and ready for protection and management."
        ),
        "help_text": (
            "❓ SmartChannelX User Guide\n\n"
            "🔹 ➕ Add channel: Make me admin in your channel, then register it.\n"
            "🔹 ⚙️ My channels: Switch between channels and open per-channel dashboards.\n"
            "🔹 📝 Create post: Send text/photo/video/file, add buttons, then publish or schedule.\n"
            "🔹 📅 Schedule posts: One-time scheduling or daily/weekly/monthly recurring.\n"
            "🔹 🛡️ Protection: captcha, join filters, banned words, bot blocking.\n"
            "🔹 📊 Statistics: subscriber growth and post performance.\n"
            "🔹 ⚙️ Settings: language, timezone, auto-signature, notifications.\n"
            "🔹 👤 Admins: add/remove admins and configure their permissions.\n\n"
            "Quick access: type /start anytime."
        ),
        "create_post_prompt": (
            "📝 Create New Post\n\n"
            "Send me the content you want to publish in your channel. You can send text, photo, video, or file.\n\n"
            "After sending, you'll see customization options."
        ),
        "post_settings_title": (
            "⚙️ New Post Settings\n\n"
            "Before sending the content, please configure the post settings.\n"
            "When done, tap the «Next Step» button."
        ),
        "btn_post_silent": "🔕 Notifications: {state}",
        "btn_post_protect": "🛡️ Protect Content: {state}",
        "btn_post_pin": "📌 Auto-Pin: {state}",
        "btn_next_content": "⬅️ Next Step: Write Content",
        "post_content_prompt": "📝 Great! Now send the content (text, photo, video, file, etc.).",
        "post_received": "✅ Content received. What would you like to add?",
        "btn_add_media": "🖼️ Add Media",
        "btn_add_buttons": "🔗 Add Buttons",
        "btn_advanced_settings": "⚙️ Advanced Settings",
        "btn_preview_publish": "✅ Preview & Publish",
        "btn_edit_buttons": "🔗 Edit Buttons",
        # New Post Control Panel
        "btn_auto_delete": "🗑️ Self-Destruct",
        "btn_auto_reply": "💬 Auto-Reply",
        "btn_reactions_settings": "❤️ Reactions",
        "btn_crosspost": "📢 Cross-post",
        "btn_save_draft": "💾 Save as Draft",
        "btn_btnbuilder_wizard": "🛠️ Button Builder Wizard",
        "btn_btnbuilder_favs": "⭐ Favorite Buttons",
        "btn_btnbuilder_clear": "❌ Clear Buttons",
        "buttons_prompt": (
            "🔗 Add Advanced Buttons\n\n"
            "You can add buttons with various functions (Premium Emojis are supported in button text). "
            "Send your buttons using the following formats (each line is a new row):\n\n"
            "🔹 **1. Standard URL:**\n"
            "`Button Text - https://t.me/...`\n\n"
            "🔹 **2. Multiple buttons per row:**\n"
            "`Btn 1 - URL 1 && Btn 2 - URL 2`\n\n"
            "🔹 **3. Popup Alert:**\n"
            "`Alert 💡 - popup: This is a popup message!`\n\n"
            "🔹 **4. Copy Text:**\n"
            "`Copy Code 📋 - copy: CODE123`\n\n"
            "🔹 **5. Share Text/Link:**\n"
            "`Share 📢 - share: Join this awesome bot!`\n\n"
            "🔹 **6. Comments:**\n"
            "`Comments 💬 - comments: https://t.me/c/...`\n\n"
            "🔹 **7. Check Subscription:**\n"
            "`Am I subscribed? - sub: @channel_username`\n\n"
            "💡 *Note: To mix multiple button types in one row, separate them with `&&`.*"
        ),
        "buttons_saved": "✅ Buttons added successfully ({count}).",
        "buttons_invalid": "❌ Invalid format. Use: text - url",
        "sub_yes": "✅ You are already subscribed to this channel!",
        "sub_no": "❌ You are not subscribed to this channel yet.",
        "sub_error": "⚠️ Could not verify your subscription.",
        "preview_title": "👀 Post preview:",
        "preview_question": "What would you like to do with this post?",
        "btn_publish_now": "🚀 Publish Now",
        "btn_schedule_publish": "⏰ Schedule",
        "btn_make_recurring": "🔁 Make Recurring",
        "btn_edit_post": "✏️ Edit Post",
        "publish_success": "🎉 Post published successfully to your channel!",
        "publish_failed": "❌ Publish failed: {error}",
        "advanced_settings_title": "⚙️ Advanced post settings",
        "btn_toggle_signature": "✍️ Auto signature: {state}",
        "btn_parse_mode": "📝 Format: {mode}",
        "btn_disable_preview": "🔗 Link preview: {state}",
        "state_on": "ON",
        "state_off": "OFF",
        "schedule_menu_title": "📅 Schedule Posts",
        "schedule_menu_body": "Manage all your scheduled and recurring posts here.",
        "btn_schedule_new": "➕ Schedule New Post",
        "btn_view_scheduled": "📝 View Scheduled Posts",
        "btn_recurring": "🔁 Recurring Posts",
        "schedule_pick_post": "Pick a draft to schedule, or create a new one:",
        "schedule_no_drafts": "📭 No drafts yet. Create a post first and save it as draft.",
        "schedule_time_prompt": (
            "🗓️ Send the publish date and time as:\n"
            "`YYYY-MM-DD HH:MM`\n\n"
            "Example: `2026-05-01 10:30`"
        ),
        "schedule_time_invalid": "❌ Invalid date format. Use: YYYY-MM-DD HH:MM",
        "schedule_time_past": "❌ The provided time is in the past. Pick a future time.",
        "schedule_success": "✅ Post scheduled for {when} ({tz}).",
        "scheduled_list_title": "📅 Scheduled posts",
        "scheduled_list_empty": "📭 No scheduled posts.",
        "scheduled_item": "📄 Post #{id} — ⏰ {when}",
        "btn_delete_scheduled": "🗑️ Delete",
        "scheduled_deleted": "✅ Scheduled post deleted.",
        # ===== Scheduling - Enhanced Keys (EN) =====
        "sched_dashboard_title": (
            "📅 Post Scheduling Dashboard\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📊 Stats:\n"
            "  ⏰ Scheduled (pending): {pending}\n"
            "  🔁 Recurring (active): {recurring}\n"
            "  📝 Ready drafts: {drafts}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Choose an action:"
        ),
        "btn_sched_new_post": "✍️ Create & Schedule Post",
        "btn_sched_from_draft": "📋 Schedule from Draft",
        "btn_sched_view_list": "📅 Scheduled Posts",
        "btn_sched_recurring": "🔁 Recurring Posts",
        "btn_sched_drafts": "🗂️ View Drafts",
        "sched_quick_time_title": (
            "⚡ Pick a quick publish time:\n\n"
            "Or send a date/time manually:\n"
            "`YYYY-MM-DD HH:MM`\n\n"
            "Example: `2026-05-01 14:30`\n\n"
            "📍 Your current time: {now} ({tz})"
        ),
        "btn_plus_1h": "⏱ +1 hour",
        "btn_plus_3h": "⏱ +3 hours",
        "btn_plus_6h": "⏱ +6 hours",
        "btn_plus_12h": "⏱ +12 hours",
        "btn_plus_24h": "⏱ +24 hours",
        "btn_tomorrow_same": "🌅 Tomorrow same time",
        "btn_next_week": "📆 Next week",
        "sched_list_title": "📅 Scheduled Posts ({count})\n\nPick a post to manage:",
        "sched_item_line": "📄 #{id} — {type} — ⏰ {when}",
        "sched_view_title": (
            "📄 Scheduled Post Details\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🆔 ID: #{id}\n"
            "📝 Type: {type}\n"
            "⏰ Scheduled: {when}\n"
            "🌍 Timezone: {tz}\n"
            "📊 Status: {status}"
        ),
        "btn_sched_view_content": "👁 Preview Content",
        "btn_sched_postpone": "⏭ Postpone",
        "btn_sched_delete": "🗑️ Cancel Schedule",
        "btn_sched_publish_now": "🚀 Publish Now",
        "sched_postpone_title": "⏭ Choose postpone duration:\n\nCurrent time: {when}",
        "btn_postpone_1h": "⏱ +1 hour",
        "btn_postpone_3h": "⏱ +3 hours",
        "btn_postpone_24h": "⏱ +24 hours",
        "btn_postpone_custom": "✏️ Custom time",
        "sched_postponed": "✅ Post #{id} postponed to {when}.",
        "sched_delete_confirm": "⚠️ Cancel scheduling of post #{id} (scheduled: {when})? This cannot be undone.",
        "btn_sched_del_confirm": "✅ Yes, cancel scheduling",
        "btn_sched_del_cancel": "❌ No, keep it",
        "sched_deleted_ok": "✅ Post #{id} unscheduled successfully.",
        "sched_no_drafts_hint": (
            "📭 No drafts available for scheduling.\n\n"
            "💡 To schedule a post:\n"
            "1️⃣ Tap ✍️ Create & Schedule Post\n"
            "2️⃣ Send content → choose «Schedule»"
        ),
        "rec_toggle_enabled": "✅ Recurring post #{id} enabled.",
        "rec_toggle_disabled": "⏸ Recurring post #{id} paused.",
        "btn_rec_toggle_on": "✅ Enable",
        "btn_rec_toggle_off": "⏸ Pause",
        "rec_view_title": (
            "🔁 Recurring Post Details\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🆔 ID: #{id}\n"
            "📅 Frequency: {freq}\n"
            "⏰ Time: {time}\n"
            "🗑 Delete timer: {timer}\n"
            "📊 Status: {status}"
        ),
        "rec_status_active": "🟢 Active",
        "rec_status_paused": "⏸ Paused",
        "rec_timer_none": "None",
        "rec_timer_set": "{min} min after publish",
        "btn_rec_view": "👁 View Details",
        "btn_rec_delete": "🗑️ Delete permanently",
        "drafts_list_title": "🗂️ Available Drafts ({count}):",
        "draft_item": "📄 #{id} — {type} — {preview}",
        "draft_no_text": "(media without text)",
        "recurring_menu_title": "🔁 Recurring Posts",
        "recurring_menu_body": "Create and manage posts that publish on a recurring schedule.",
        "btn_recurring_new": "➕ New Recurring Post",
        "btn_recurring_view": "📝 View Recurring Posts",
        "btn_recurring_edit": "✏️ Edit Recurring Post",
        "btn_recurring_delete": "🗑️ Delete Recurring Post",
        "recurring_pick_freq": "Pick the recurrence:",
        "btn_freq_daily": "☀️ Daily",
        "btn_freq_weekly": "🗓️ Weekly",
        "btn_freq_monthly": "📆 Monthly",
        "recurring_time_prompt_daily": "Send the daily publish time as `HH:MM` (e.g. `09:30`).",
        "recurring_time_prompt_weekly": "Send `DAY HH:MM`. Days: Mon Tue Wed Thu Fri Sat Sun. Example: `Mon 10:00`",
        "recurring_time_prompt_monthly": "Send `DAY HH:MM` where DAY is 1–28. Example: `15 09:00`",
        "recurring_invalid": "❌ Invalid format. Try again.",
        "recurring_success_daily": "✅ Daily recurring post set at {time}.",
        "recurring_success_weekly": "✅ Weekly recurring post set every {day} at {time}.",
        "recurring_success_monthly": "✅ Monthly recurring post set on day {day} at {time}.",
        "recurring_ask_delete_timer": "Add an auto-delete timer to each instance?",
        "btn_add_delete_timer": "⏱️ Add Delete Timer",
        "btn_skip_delete_timer": "✅ No, thanks",
        "delete_timer_prompt": "Send the number of minutes after which each instance is auto-deleted (e.g. `60`).",
        "delete_timer_set": "✅ Each instance will be deleted {minutes} min after publishing.",
        "recurring_list_title": "🔁 Recurring posts",
        "recurring_list_empty": "📭 No recurring posts.",
        "recurring_item_daily": "📄 #{id} — ☀️ Daily {time}",
        "recurring_item_weekly": "📄 #{id} — 🗓️ {day} {time}",
        "recurring_item_monthly": "📄 #{id} — 📆 Day {day} at {time}",
        "recurring_deleted": "✅ Recurring post deleted.",
        "protection_title": "🛡️ Channel Protection: {name}",
        "protection_body": "Enable and customize protection settings for your channel.",
        "btn_captcha": "🧠 Captcha: {state}",
        "btn_join_filters": "🚫 Join Filters",
        "btn_word_filter": "🗑️ Banned Words Filter",
        "btn_block_bots": "🤖 Block Bots: {state}",
        "captcha_toggled": "✅ Captcha setting updated. Now: {state}",
        "block_bots_toggled": "✅ Bot block setting updated. Now: {state}",
        "join_filters_title": "🚫 Pick a join filter to manage:",
        "btn_filter_total_ban": "⛔ Total Ban",
        "btn_filter_multi_ban": "👨‍👩‍👦 Multi Ban",
        "btn_filter_names": "🆎 Name Filter",
        "btn_filter_alphabet": "🕉️ Alphabet Filter",
        "name_filter_intro": "Enabling the name filter will block users whose names contain specific words. Enable it?",
        "btn_enable": "✅ Enable",
        "btn_disable": "❌ Disable",
        "name_filter_words_prompt": "Send the words to block, one per line.",
        "name_filter_saved": "✅ Name filter enabled. Blocked words:\n{words}",
        "word_filter_prompt": "Send banned comment words, one per line. Send `-` to disable the filter.",
        "word_filter_saved": "✅ Word filter saved ({count} words).",
        "word_filter_disabled": "✅ Word filter disabled.",
        "stats_title": "📊 Channel Statistics: {name}",
        "stats_body": "Pick the type of statistics to view.",
        "btn_stat_growth": "📈 Subscriber Growth",
        "btn_stat_engagement": "❤️ Post Engagement",
        "btn_stat_views": "👁️ Post Views",
        "btn_stat_top": "🔝 Top Posts",
        "stats_pick_period": "Pick the time period:",
        "btn_period_today": "Today",
        "btn_period_7": "Last 7 days",
        "btn_period_30": "Last 30 days",
        "btn_period_90": "Last 90 days",
        "stats_growth_caption": "📈 Subscriber growth over {period}\n\nCurrent: {current} subscribers\nChange: {delta}",
        "stats_engagement_text": (
            "❤️ Post engagement (last {n} posts)\n\n"
            "Avg views: {avg_views}\n"
            "Total views: {total_views}\n"
            "Tracked posts: {tracked}"
        ),
        "stats_views_text": "👁️ Post views\n\n{lines}",
        "stats_top_text": "🔝 Top performing posts:\n\n{lines}",
        "stats_no_data": "📭 Not enough statistical data yet. Tracking starts now.",
        "settings_title": "⚙️ Channel Settings: {name}",
        "settings_body": "Pick the setting you want to edit.",
        "btn_change_lang": "🌐 Change Language",
        "btn_timezone": "⏰ Timezone",
        "btn_signature": "✍️ Auto Signature",
        "btn_notifications": "🔔 Channel Notifications: {state}",
        "lang_pick_title": "🌐 Pick the bot language for this channel:",
        "btn_lang_ar": "🇸🇦 العربية",
        "btn_lang_en": "🇬🇧 English",
        "lang_changed": "✅ Language changed.",
        "timezone_prompt": (
            "⏰ Send the IANA timezone.\n\n"
            "Examples:\n"
            "• Asia/Riyadh\n"
            "• Africa/Cairo\n"
            "• Europe/Istanbul\n"
            "• UTC"
        ),
        "timezone_invalid": "❌ Invalid timezone.",
        "timezone_saved": "✅ Timezone set to: {tz}",
        "signature_ask_enable": "Enable auto-signature for posts?",
        "signature_prompt": "Send the signature text to append at the end of each post.",
        "signature_enabled": "✅ Auto-signature enabled. Will append:\n«{text}»",
        "signature_disabled": "✅ Auto-signature disabled.",
        "notifications_toggled": "✅ Notifications updated. Now: {state}",
        "admins_title": "👤 Admin Management: {name}",
        "admins_body": "Manage admins for your channel.",
        "btn_admin_add": "➕ Add Admin",
        "btn_admin_edit": "✏️ Edit Permissions",
        "btn_admin_remove": "🗑️ Remove Admin",
        "btn_admin_view": "📝 View Admins",
        "admin_add_prompt": "👤 Forward any message from the user to add as admin, or send their @username.",
        "admin_added": "✅ @{username} added as admin with permissions: {perms}",
        "admin_pick_perms": "Pick permissions for new admin @{username}:",
        "perm_publish": "Publish posts",
        "perm_edit": "Edit posts",
        "perm_delete": "Delete posts",
        "perm_protection": "Manage protection",
        "perm_stats": "View statistics",
        "perm_settings": "Manage settings",
        "btn_save_perms": "✅ Save Permissions",
        "admins_list_title": "👤 Current admins:",
        "admins_list_empty": "📭 No bot-level admins added yet.",
        "admin_removed": "✅ Admin @{username} removed.",
        "change_menu_title": "🌐 Change Channel/Language",
        "change_menu_body": "Pick a channel to manage or change the bot language.",
        "btn_switch_channel": "🔄 Switch Channel",
        "btn_change_bot_lang": "🌐 Change Language",
        "switched_channel": "✅ Switched to channel: {name}",
        "dev_title": "🛠️ Developer Settings",
        "dev_body": "Developer panel for SmartChannelX. Handle with care.",
        "btn_dev_apikeys": "🔑 API Keys",
        "btn_dev_integrations": "🔗 Integrations",
        "btn_dev_logs": "📜 Error Logs",
        "btn_dev_restart": "🔄 Restart Bot",
        "dev_only": "⛔ This menu is for developers only.",
        "dev_apikeys_title": "🔑 API Keys",
        "dev_apikeys_empty": "📭 No API keys registered.",
        "btn_apikey_add": "➕ Add API Key",
        "btn_apikey_view": "📝 View API Keys",
        "btn_apikey_delete": "🗑️ Delete API Key",
        "apikey_prompt": "Send service name on the first line and API key on the second line.\n\nExample:\n```\nOpenAI\nsk-xxxxxxxxxxxx\n```",
        "apikey_added": "✅ API key for {name} added.",
        "apikey_invalid": "❌ Invalid format.",
        "logs_title": "📜 Recent error logs:\n\n```\n{logs}\n```",
        "logs_empty": "✅ No errors logged.",
        "restart_confirm": "⚠️ The bot will restart. This may take a few seconds.",
        "err_invalid_format": "⚠️ Invalid format.",
        "err_generic": "❌ Something went wrong. Please try again.",
        "err_not_admin": "⛔ You must be the channel owner or an admin to use this feature.",
        "err_no_channel_selected": "⚠️ No channel selected. Tap 🏠 Home and pick a channel.",
        "confirm_delete": "❓ Are you sure? This action cannot be undone.",
        "cancelled": "✅ Operation cancelled.",
        "saved": "✅ Saved successfully!",
        "draft_label": "📄 Post #{id} (draft)",
        "back_to_main": "🏠 Returning to main menu…",
        "channel_locale_label": "[{name}]",
        # Generic
        "btn_op_add": "➕ Add",
        "btn_op_edit": "✏️ Edit",
        "btn_op_delete": "🗑️ Delete",
        "btn_op_view": "👁 View",
        "btn_op_toggle": "⚙️ Toggle",
        "btn_op_export": "📤 Export",
        "btn_op_filter": "🔍 Filter",
        "btn_op_clear": "🧹 Clear All",
        "pick_channel_first": "Pick a channel first:",
        "no_channels_global": "📭 You have no channels yet. Add one from the main menu.",
        # Event Log
        "btn_events": "📜 Event Log",
        "events_title": "📜 Event log: {name}",
        "events_body": (
            "Monitor all major channel events: posts, admin changes, my permission changes, joins/leaves…"
        ),
        "btn_events_view_all": "👁 View All",
        "btn_events_filter": "🔍 Filter",
        "btn_events_export": "📤 Export",
        "btn_events_clear": "🧹 Clear Log",
        "events_filter_title": "🔍 Pick filter type:",
        "btn_filter_by_type": "By type",
        "btn_filter_by_user": "By user",
        "btn_filter_by_date": "By date",
        "btn_filter_reset": "♻️ Reset filter",
        "events_filter_type_pick": "Pick event type:",
        "ev_type_post_published": "📝 Post published",
        "ev_type_post_scheduled": "⏰ Post scheduled",
        "ev_type_admin_added": "👤➕ Admin added",
        "ev_type_admin_removed": "👤🗑️ Admin removed",
        "ev_type_member_join": "🟢 Member joined",
        "ev_type_member_leave": "🔴 Member left",
        "ev_type_settings_changed": "⚙️ Settings changed",
        "ev_type_protection_changed": "🛡️ Protection changed",
        "ev_type_forward_sent": "🔁 Forward sent",
        "ev_type_multisend": "📤 Multi-send",
        "ev_type_other": "📌 Other",
        "events_filter_user_prompt": "Send the numeric user ID to filter:",
        "events_filter_date_prompt": "Send the number of past days to view (e.g. `7`):",
        "events_list_empty": "📭 No events logged yet.",
        "events_list_header": "📜 Last {n} events:",
        "events_export_done": "✅ Log file ready.",
        "events_cleared": "✅ Channel log cleared.",
        # Autocomplete
        "btn_autocomplete": "🤖 Auto-completion",
        "ac_title": "🤖 Auto-completion: {name}",
        "ac_body": (
            "In this menu you can configure additions that are automatically inserted in every "
            "message you manually send via this bot.\n\n"
            "Create sets of message additions that apply based on configurable filters (trigger words)."
        ),
        "ac_empty": "You have not created any auto-completion sets yet.",
        "btn_ac_add": "➕ Create new set",
        "btn_ac_view": "👁 View sets",
        "btn_ac_edit": "✏️ Edit set",
        "btn_ac_delete": "🗑️ Delete set",
        "ac_name_prompt": "Send a short name for this set (e.g. `Promo`, `Welcome`):",
        "ac_created": "✅ Set «{name}» created. Now add triggers and texts.",
        "ac_set_view": (
            "🤖 Set: «{name}»\n"
            "State: {state}\n\n"
            "🔍 Triggers: {triggers}\n"
            "📜 Prefix:\n{prefix}\n\n"
            "📜 Suffix:\n{suffix}"
        ),
        "btn_ac_edit_triggers": "🔍 Edit triggers",
        "btn_ac_edit_prefix": "⬆️ Edit prefix",
        "btn_ac_edit_suffix": "⬇️ Edit suffix",
        "btn_ac_toggle": "⚙️ Toggle: {state}",
        "ac_triggers_prompt": (
            "🔍 Send trigger words separated by commas. The set will apply when any word matches.\n\n"
            "Send `-` to apply to every post."
        ),
        "ac_prefix_prompt": "⬆️ Send the prefix text to prepend (or `-` to clear):",
        "ac_suffix_prompt": "⬇️ Send the suffix text to append (or `-` to clear):",
        "ac_field_saved": "✅ Saved.",
        "ac_deleted": "✅ Set deleted.",
        "ac_toggled": "✅ State updated: {state}",
        "ac_applied_note": "✨ Auto-completion applied ({n} sets).",
        # Multi-send
        "btn_multisend": "📤 Multi-send",
        "ms_title": "📤 Multi-send",
        "ms_body": (
            "Send a single post to multiple channels at once, or schedule it to be published later.\n"
            "Pick an action to start."
        ),
        "btn_ms_new": "➕ New campaign",
        "btn_ms_view": "📋 Past campaigns",
        "ms_pick_post_title": "📝 Pick a draft from one of your channels:",
        "ms_no_drafts": "📭 No drafts in any channel. Create a post first.",
        "ms_pick_targets_title": "✅ Pick target channels (tap to add/remove):",
        "btn_ms_target_select_all": "✔ Select all channels",
        "btn_ms_target_clear": "✖ Clear selection",
        "btn_ms_continue": "➡️ Continue",
        "ms_when_title": "⏰ When do you want to send?",
        "btn_ms_send_now": "🚀 Now",
        "btn_ms_schedule": "📅 Schedule",
        "ms_schedule_prompt": "Send date & time as `YYYY-MM-DD HH:MM`:",
        "ms_confirm": "📤 Will send to {n} channels. Confirm?",
        "btn_ms_confirm": "✅ Confirm send",
        "ms_done": "✅ Campaign #{id} done: {ok}/{total} succeeded.",
        "ms_scheduled": "✅ Campaign #{id} scheduled for {when}.",
        "ms_select_first": "⚠️ Select at least one channel.",
        "ms_jobs_title": "📋 Past campaigns:",
        "ms_jobs_empty": "📭 No past campaigns.",
        "ms_job_row": "#{id} • {when} • {status} • {ok}/{total}",
        "btn_ms_job_view": "👁 Detail #{id}",
        "btn_ms_job_delete": "🗑️ Delete #{id}",
        "ms_job_detail": (
            "📤 Campaign #{id}\n"
            "📝 Post: #{post_id}\n"
            "🕒 Created: {created}\n"
            "📅 Scheduled: {scheduled}\n"
            "📊 Status: {status}\n\n"
            "Results:\n{results}"
        ),
        # Forwarding
        "btn_forwarding": "🔁 Forwarding",
        "fw_title": "🔁 Forwarding from: {name}",
        "fw_body": (
            "Forward every manually-sent message in your channel to other channels or groups.\n\n"
            "Add a new rule with target and optional filter."
        ),
        "btn_fw_add": "➕ Add forwarding rule",
        "btn_fw_view": "👁 View rules",
        "fw_target_prompt": (
            "🎯 Send the forwarding target:\n\n"
            "• `@channelname` — public channel\n"
            "• `-1001234567890` — numeric ID\n\n"
            "Make sure I am a member/admin in the target."
        ),
        "fw_filter_prompt": (
            "🔍 Send a filter word (only messages containing it will be forwarded).\n\n"
            "Send `-` to forward all messages without filter."
        ),
        "fw_added": "✅ Forwarding rule to {target} added.",
        "fw_target_invalid": "❌ Invalid target or I cannot access it.",
        "fw_list_empty": "📭 No forwarding rules yet.",
        "fw_list_title": "🔁 Active forwarding rules:",
        "fw_rule_row": "🎯 {target}{filter} • {state}",
        "fw_filter_label": " | filter: «{f}»",
        "btn_fw_toggle": "⚙️ {state}",
        "btn_fw_edit": "✏️ Edit #{id}",
        "btn_fw_delete": "🗑️ Delete #{id}",
        "fw_deleted": "✅ Rule deleted.",
        "fw_toggled": "✅ State updated: {state}",
        "fw_edit_pick": "✏️ What do you want to edit?",
        "btn_fw_edit_target": "🎯 Edit target",
        "btn_fw_edit_filter": "🔍 Edit filter",
        "fw_forwarded_note": "🔁 Forwarded to {n} targets.",
        # Goodbye
        "btn_goodbye": "👋 Goodbye Message",
        "gb_title": "👋 Goodbye settings: {name}",
        "gb_body": (
            "Customize the goodbye message shown when a member leaves, and toggle banning leavers.\n\n"
            "🔘 State: {enabled}\n"
            "📝 Message:\n{message}\n\n"
            "🚫 Ban on leave: {ban}"
        ),
        "btn_gb_toggle": "⚙️ Toggle goodbye",
        "btn_gb_set_message": "✏️ Edit message",
        "btn_gb_toggle_ban": "🚫 Toggle ban-on-leave",
        "btn_gb_view": "👁 Preview message",
        "btn_gb_delete": "🗑️ Delete message",
        "gb_message_prompt": (
            "✏️ Send the goodbye message text.\n\n"
            "Available variables:\n"
            "• `{name}` member name\n"
            "• `{username}` member username\n"
            "• `{channel}` channel name"
        ),
        "gb_message_set": "✅ Goodbye message saved.",
        "gb_message_none": "—",
        "gb_toggled": "✅ State updated: {state}",
        "gb_ban_toggled": "✅ Ban-on-leave: {state}",
        "gb_message_deleted": "✅ Message deleted.",
        "gb_preview_title": "👁 Preview:",
        # Support
        "btn_support": "🆘 Support",
        "sup_title": "🆘 Support Center",
        "sup_body": (
            "Contact our support team via an organized ticket system.\n"
            "Open a new ticket or check your past tickets and replies."
        ),
        "btn_sup_new": "➕ New ticket",
        "btn_sup_my": "📋 My tickets",
        "btn_sup_admin_open": "📥 Open tickets (staff)",
        "sup_subject_prompt": "📝 Send a short subject (one line):",
        "sup_body_prompt": "📨 Now send a detailed description:",
        "sup_created": "✅ Ticket #{id} opened. Our team will reply soon.",
        "sup_my_empty": "📭 You have no tickets yet.",
        "sup_my_title": "📋 Your tickets:",
        "sup_ticket_row": "#{id} • {subject} • {status}",
        "btn_sup_open_ticket": "👁 #{id}",
        "btn_sup_reply": "💬 Reply",
        "btn_sup_close": "🔒 Close",
        "btn_sup_reopen": "🔓 Reopen",
        "sup_ticket_view": (
            "🎫 Ticket #{id}\n"
            "📌 Subject: {subject}\n"
            "📊 Status: {status}\n"
            "🕒 Updated: {updated}\n\n"
            "💬 Thread:\n{thread}"
        ),
        "sup_thread_user": "👤 You ({when}):\n{body}",
        "sup_thread_staff": "🧑‍💼 Support ({when}):\n{body}",
        "sup_reply_prompt": "💬 Send your reply to ticket #{id}:",
        "sup_reply_sent": "✅ Reply sent.",
        "sup_status_open": "🟢 Open",
        "sup_status_closed": "🔒 Closed",
        "sup_closed": "✅ Ticket closed.",
        "sup_reopened": "✅ Ticket reopened.",
        "sup_admin_open_title": "📥 Open tickets:",
        "sup_admin_open_empty": "✨ No open tickets right now.",
        "sup_notify_user": "📨 New reply on your ticket #{id}:\n\n{body}",
        "sup_notify_staff": "🆕 New support ticket #{id} from {user}:\n📌 {subject}",
        # Create bot
        "btn_createbot": "🤖➕ Create Bot",
        "cb_title": "🤖➕ Sub-bots Management",
        "cb_body": (
            "Connect your own bots created via @BotFather to manage them centrally.\n\n"
            "1️⃣ Open @BotFather.\n"
            "2️⃣ Create a new bot via /newbot and get the token.\n"
            "3️⃣ Come back and tap ➕ to register it."
        ),
        "btn_cb_add": "➕ Add bot by token",
        "btn_cb_view": "👁 My bots",
        "cb_token_prompt": (
            "🔐 Send the bot token from @BotFather:\n"
            "`123456:ABC-DEF1234ghIkl...`\n\n"
            "🔒 The token will only be visible to you."
        ),
        "cb_token_invalid": "❌ Token invalid or rejected by Telegram.",
        "cb_added": "✅ Bot @{username} linked successfully.",
        "cb_list_empty": "📭 No sub-bots linked yet.",
        "cb_list_title": "🤖 Your sub-bots:",
        "cb_row": "🤖 @{username} • {state}",
        "btn_cb_open": "👁 @{username}",
        "btn_cb_toggle": "⚙️ {state}",
        "btn_cb_delete": "🗑️ Delete",
        "cb_view": (
            "🤖 @{username}\n"
            "🆔 ID: `{bot_id}`\n"
            "🔑 Token: `{masked}`\n"
            "📊 State: {state}\n"
            "🕒 Since: {created}"
        ),
        "cb_deleted": "✅ Bot removed from list.",
        "cb_toggled": "✅ State updated: {state}",
        # Bot Guide
        "btn_guide": "📘 Bot Guide",
        "guide_title": "📘 SmartChannelX Guide",
        "guide_body": "Pick the section you want to read about:",
        "btn_guide_overview": "🏠 Overview",
        "btn_guide_channels": "📢 Channels",
        "btn_guide_posts": "📝 Posts",
        "btn_guide_schedule": "📅 Schedule",
        "btn_guide_protection": "🛡️ Protection",
        "btn_guide_stats": "📊 Statistics",
        "btn_guide_admins": "👤 Admins",
        "btn_guide_advanced": "🤖 Advanced",
        "btn_guide_faq": "❓ FAQ",
        "guide_overview": (
            "🏠 Overview\n\n"
            "SmartChannelX is a professional Telegram channel management system that combines:\n"
            "• Post creation, scheduling, and recurrence\n"
            "• Advanced protection (captcha, filters, bot blocking)\n"
            "• Growth and engagement statistics\n"
            "• Granular admin permissions\n"
            "• 9 advanced tools: event log, auto-completion, multi-send, forwarding, goodbye, support, sub-bots, force-subscribe, guide."
        ),
        "guide_channels": (
            "📢 Channels\n\n"
            "• 6 ways to add: direct button, @username, forward, Chat ID, t.me link, or auto-detect on promotion.\n"
            "• The channel list shows live status badges: 👑 owner, ✅ admin, ⚠️ member, ❌ left, ❔ unknown.\n"
            "• Use /verify to check all your channels at once."
        ),
        "guide_posts": (
            "📝 Posts\n\n"
            "• Send text/photo/video/file.\n"
            "• Add link buttons (Text - URL).\n"
            "• Advanced: auto-signature, HTML/Markdown formatting, disable link preview.\n"
            "• Preview before publish, then: publish now / schedule / recurring."
        ),
        "guide_schedule": (
            "📅 Schedule & recurring\n\n"
            "• One-time as `YYYY-MM-DD HH:MM`.\n"
            "• Daily/weekly/monthly recurrence.\n"
            "• Auto-delete timer per instance."
        ),
        "guide_protection": (
            "🛡️ Protection\n\n"
            "• 🧠 Captcha for new group members.\n"
            "• 🚫 Join filters (total ban, multi-ban, name filter, alphabet filter).\n"
            "• 🗑️ Banned-words filter for comments.\n"
            "• 🤖 Auto bot blocking."
        ),
        "guide_stats": (
            "📊 Statistics\n\n"
            "• 📈 Subscriber growth (with chart).\n"
            "• ❤️ Post engagement.\n"
            "• 👁️ Per-post views.\n"
            "• 🔝 Top posts."
        ),
        "guide_admins": (
            "👤 Admins\n\n"
            "Add bot-level admins with permissions: publish, edit, delete, protection, statistics, settings.\n"
            "Each permission is independent."
        ),
        "guide_advanced": (
            "🤖 Advanced tools\n\n"
            "• 📜 Event log: track every operation.\n"
            "• 🤖 Auto-completion: prefix/suffix posts.\n"
            "• 📤 Multi-send: campaign to multiple channels.\n"
            "• 🔁 Forwarding: sync between channels.\n"
            "• 👋 Goodbye message.\n"
            "• 🆘 Support tickets.\n"
            "• 🤖➕ Sub-bots: link your @BotFather bots.\n"
            "• ⭐ Force-subscribe."
        ),
        "guide_faq": (
            "❓ FAQ\n\n"
            "Q: Why is the bot not responding in my channel?\n"
            "A: Make sure I'm an admin with «post» permission. Use /verify.\n\n"
            "Q: Why didn't the private confirmation arrive when adding a channel?\n"
            "A: Start a chat with me via /start in DM first.\n\n"
            "Q: How do I delegate management?\n"
            "A: Add the user as an admin with full permissions from the Admins menu.\n\n"
            "Q: Do you store passwords or tokens?\n"
            "A: Tokens are masked and only visible to you."
        ),
        # Subscription
        "btn_subscription": "⭐ Subscription",
        "sub_title": "⭐ Force-subscribe for: {name}",
        "sub_body": (
            "Link mandatory subscription channels that members must join.\n"
            "You can add multiple, toggle any, or delete them."
        ),
        "btn_sub_add": "➕ Add subscription channel",
        "btn_sub_view": "👁 View channels",
        "btn_sub_check": "🔎 Check user subscription",
        "sub_add_prompt": (
            "🔗 Send the subscription channel:\n"
            "• `@username`\n"
            "• Or numeric `-100…`\n\n"
            "Make sure I am a member of that channel for verification."
        ),
        "sub_added": "✅ Subscription channel «{title}» added.",
        "sub_invalid": "❌ Could not verify the channel.",
        "sub_list_empty": "📭 No subscription channels linked.",
        "sub_list_title": "⭐ Linked subscription channels:",
        "sub_row": "📡 {title} • {ref} • {state}",
        "btn_sub_toggle": "⚙️ {state}",
        "btn_sub_delete": "🗑️ Delete",
        "sub_deleted": "✅ Channel removed.",
        "sub_toggled": "✅ State updated: {state}",
        "sub_check_prompt": "Send the numeric user ID to check subscription:",
        "sub_check_result": "Subscription check for user {user}:\n\n{lines}",
        "sub_check_ok": "✅ Subscribed in {ref}",
        "sub_check_no": "❌ Not subscribed in {ref}",
        "sub_check_err": "❔ Cannot check {ref}: {err}",
        # Aliases / new keys for the 9 sections
        "err_not_staff": "❌ This action is restricted to support staff.",
        "ms_pick_post": "📝 Pick a draft post to broadcast:",
        "ms_pick_targets": "✅ Choose target channels (tap to add/remove):\n\n📄 {preview}",
        "ms_no_targets": "⚠️ Pick at least one channel.",
        "ms_when_prompt": "⏰ When do you want to send?",
        "ms_when_now": "Now",
        "ms_dispatched": "✅ Campaign #{id} dispatched/scheduled.",
        "ms_jobs_header": "📋 Last {n} campaigns:",
        "ms_job_line": "#{id} • {status} • {n} channels • {when}",
        "ms_job_view": "📋 Campaign #{id}\nStatus: {status}\nTargets: {n}\nOK: {ok} | Failed: {fail}",
        "fw_empty": "📭 No forwarding rules yet.",
        "fw_list_header": "🔁 You have {n} forwarding rule(s):",
        "fw_add_target_prompt": "📝 Send the forwarding target (`@username` or numeric id):",
        "fw_add_filter_prompt": "🧪 Send an optional filter word, or `-` to forward everything:",
        "fw_updated": "✅ Rule updated.",
        "gb_current_message": "📝 Current message:\n{msg}",
        "gb_no_message": "(No message set yet)",
        "gb_msg_prompt": (
            "📝 Send the goodbye message text.\n"
            "Available variables: `{name}` `{username}` `{id}`."
        ),
        "gb_view": "👁 Preview:\n\n{msg}",
        "gb_saved": "✅ Goodbye message saved.",
        "sup_no_tickets": "📭 You don't have any tickets.",
        "sup_my_header": "🎫 Your tickets ({n}):",
        "sup_no_open": "✅ No open tickets.",
        "sup_open_header": "🆘 Open tickets ({n}):",
        "sup_staff_notify": "🆘 New ticket #{id}: {subject}",
        "sup_staff_replied": "💬 New reply on your ticket #{id}.",
        "cb_invalid_token": "❌ Invalid token format. Try again.",
        "cb_token_failed": "❌ Token validation failed: {err}",
        "cb_empty": "📭 No bots registered yet.",
        "cb_list_header": "🤖 Your bots ({n}):",
        "guide_section_overview": (
            "🌟 SmartChannelX is your smart assistant for Telegram channel management.\n"
            "Create and schedule posts, protect your channel, analyze stats, "
            "manage admins, and more."
        ),
        "guide_section_channels": (
            "📢 To add a channel, tap (Add channel/group) and pick a method.\n"
            "You can add via id, link, forwarded message, or username."
        ),
        "guide_section_posts": (
            "📝 To create a post, open your channel then (Create post).\n"
            "Supports text, photos, video, files, buttons, and formatting."
        ),
        "guide_section_schedule": (
            "📅 You can schedule posts for later or repeat them daily/weekly.\n"
            "Auto-resending is also available."
        ),
        "guide_section_protection": (
            "🛡 Protection: word filter, name filter, bot blocking, "
            "captcha, and flood protection."
        ),
        "guide_section_stats": (
            "📊 Stats: posts, members, engagement, and operations."
        ),
        "guide_section_admins": (
            "👥 Add bot-level admins to help manage your channels."
        ),
        "guide_section_advanced": (
            "🤖 Advanced features:\n"
            "• 📤 Multi-send to many channels at once\n"
            "• 🔁 Auto-forwarding\n"
            "• 👋 Goodbye messages\n"
            "• ⭐ Mandatory subscription"
        ),
        "guide_section_faq": (
            "❓ FAQ:\n"
            "Q: Why can't the bot publish?\n"
            "A: Make sure it's added as admin with post permission.\n\n"
            "Q: How do I change the language?\n"
            "A: Main menu → Language."
        ),
        "sub_empty": "📭 No subscription channels yet.",
        "sub_list_header": "⭐ {n} subscription channel(s):",
        "sub_check_done": "🧪 Check result for user {uid}: {state}",
        "sub_check_pass": "✅ Complete",
        "sub_check_fail": "❌ Missing",
        "sub_no_active": "(No active subscription rules)",
    },
}


def t(lang: str | None, key: str, **kwargs: Any) -> str:
    """Translate a key into the given language."""
    lang = (lang or "ar").lower()
    if lang not in TRANSLATIONS:
        lang = "ar"
    template = TRANSLATIONS[lang].get(key)
    if template is None:
        template = TRANSLATIONS["ar"].get(key, key)
    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError):
            return template
    return template
