from __future__ import annotations

import asyncio
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from .. import database as db
from .. import keyboards as kb
from ..i18n import t
from ..utils import get_user_language

log = logging.getLogger(__name__)

async def cb_automation_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    
    rows = [
        [InlineKeyboardButton("➕ إنشاء قاعدة جديدة", callback_data=f"auto:new:{channel_id}")],
        [InlineKeyboardButton("📋 استعراض القواعد", callback_data=f"auto:list:{channel_id}")],
        [InlineKeyboardButton("🔙 رجوع", callback_data=f"ch:open:{channel_id}")]
    ]
    markup = InlineKeyboardMarkup(rows)
    text = "🤖 **نظام الأتمتة الذكية**\n\nقم ببناء قواعد أتمتة مخصصة (مثال: عند نشر منشور يحتوي على كلمة X، قم بإرساله للقناة Y، أو تثبيته)."
    await q.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")

async def cb_sync_engine_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    
    rows = [
        [InlineKeyboardButton("🔄 تشغيل المزامنة الآن", callback_data=f"ch:run_sync:{channel_id}")],
        [InlineKeyboardButton("⏱️ إعداد المزامنة المجدولة", callback_data=f"sync:sched:{channel_id}")],
        [InlineKeyboardButton("📜 سجلات المزامنة", callback_data=f"sync:logs:{channel_id}")],
        [InlineKeyboardButton("🔙 رجوع", callback_data=f"ch:open:{channel_id}")]
    ]
    markup = InlineKeyboardMarkup(rows)
    text = "🔄 **محرك المزامنة (Sync Engine)**\n\nيضمن مزامنة بيانات المشتركين والإحصائيات والرسائل بشكل مستمر مع تيليجرام للحفاظ على دقة البيانات."
    await q.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")

async def cb_tags_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    
    rows = [
        [InlineKeyboardButton("➕ إضافة علامة", callback_data=f"tags:add:{channel_id}")],
        [InlineKeyboardButton("🔙 رجوع", callback_data=f"ch:dash:{channel_id}")]
    ]
    markup = InlineKeyboardMarkup(rows)
    text = "🏷️ **إدارة العلامات (Tags & Categories)**\n\nصنف قنواتك وقم بإدارتها بشكل أفضل عبر إسناد علامات مخصصة لها (مثال: 'إخبارية'، 'فريق المبيعات')."
    await q.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")

def register(app) -> None:
    app.add_handler(CallbackQueryHandler(cb_automation_menu, pattern=r"^ch:auto:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_sync_engine_menu, pattern=r"^ch:sync:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_tags_menu, pattern=r"^ch:tags:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_tag_add_prompt, pattern=r"^tags:add:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_sync_schedule_prompt, pattern=r"^sync:sched:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_auto_new_prompt, pattern=r"^auto:new:\d+$"))

async def cb_tag_add_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    
    context.user_data["flow"] = {"name": "add_channel_tag", "channel_id": channel_id}
    await q.edit_message_text(
        "🏷️ أرسل الآن اسم العلامة (Tag) التي تريد إضافتها لهذه القناة (مثال: إخبارية، عاجل):",
        reply_markup=kb.InlineKeyboardMarkup([[kb.InlineKeyboardButton("🔙 إلغاء", callback_data=f"ch:tags:{channel_id}")]])
    )

async def msg_add_channel_tag(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow")
    if not flow or flow.get("name") != "add_channel_tag":
        return False
        
    tag_name = update.message.text.strip()
    channel_id = flow["channel_id"]
    
    # Save tag to database
    conn = db.db()
    await conn.execute("INSERT INTO channel_tags (channel_id, tag_name) VALUES (?, ?)", (channel_id, tag_name))
    await conn.commit()
    
    context.user_data.pop("flow", None)
    await update.message.reply_text(
        f"✅ تم إضافة العلامة '{tag_name}' بنجاح للقناة.",
        reply_markup=kb.InlineKeyboardMarkup([[kb.InlineKeyboardButton("🔙 العودة للإدارة", callback_data=f"ch:tags:{channel_id}")]])
    )
    return True

async def cb_sync_schedule_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer("سيتم تفعيل هذه الميزة قريباً لضبط مزامنة كل (ساعة/يوم/أسبوع).", show_alert=True)

async def cb_auto_new_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer("قريباً: معالج إنشاء القواعد الذكية التلقائية (Rule Builder Wizard).", show_alert=True)
