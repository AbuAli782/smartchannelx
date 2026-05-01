"""Inline keyboards for SmartChannelX."""
from __future__ import annotations

from typing import Iterable

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from .i18n import t


def _row_back_home_cancel(lang: str, back_cb: str = "nav:back") -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(t(lang, "btn_back"), callback_data=back_cb),
        InlineKeyboardButton(t(lang, "btn_home"), callback_data="nav:home"),
        InlineKeyboardButton(t(lang, "btn_cancel"), callback_data="nav:cancel"),
    ]


def welcome_kb(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_add_channel"), callback_data="ch:add")],
        [InlineKeyboardButton(t(lang, "btn_my_channels"), callback_data="ch:list")],
        [
            InlineKeyboardButton(t(lang, "btn_events"), callback_data="ev:pickch"),
            InlineKeyboardButton(t(lang, "btn_autocomplete"), callback_data="ac:pickch"),
        ],
        [
            InlineKeyboardButton(t(lang, "btn_multisend"), callback_data="ms:menu"),
            InlineKeyboardButton(t(lang, "btn_forwarding"), callback_data="fw:pickch"),
        ],
        [
            InlineKeyboardButton(t(lang, "btn_goodbye"), callback_data="gb:pickch"),
            InlineKeyboardButton(t(lang, "btn_subscription"), callback_data="sub:pickch"),
        ],
        [
            InlineKeyboardButton(t(lang, "btn_support"), callback_data="sup:menu"),
            InlineKeyboardButton(t(lang, "btn_createbot"), callback_data="cb:menu"),
        ],
        [
            InlineKeyboardButton(t(lang, "btn_guide"), callback_data="gd:menu"),
            InlineKeyboardButton(t(lang, "btn_help"), callback_data="nav:help"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def channels_list_kb(lang: str, channels: list[dict], statuses: dict[int, str] | None = None) -> InlineKeyboardMarkup:
    """Render the user's channels with optional live status badges.

    `statuses` maps channel_id -> single emoji ('✅', '👑', '⚠️', '❌', '❔').
    """
    rows: list[list[InlineKeyboardButton]] = []
    for ch in channels:
        title = ch.get("title") or ch.get("username") or str(ch["telegram_chat_id"])
        badge = (statuses or {}).get(ch["id"], "📢")
        rows.append([InlineKeyboardButton(f"{badge} {title}", callback_data=f"ch:open:{ch['id']}")])
    rows.append([InlineKeyboardButton(t(lang, "btn_verify_all"), callback_data="ch:verifyall")])
    rows.append([InlineKeyboardButton(t(lang, "btn_add_channel"), callback_data="ch:add")])
    rows.append([InlineKeyboardButton(t(lang, "btn_home"), callback_data="nav:home")])
    return InlineKeyboardMarkup(rows)


def channel_main_menu_kb(lang: str, channel_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_create_post"), callback_data=f"post:new:{channel_id}")],
        [InlineKeyboardButton(t(lang, "btn_schedule_posts"), callback_data=f"sched:menu:{channel_id}")],
        [
            InlineKeyboardButton(t(lang, "btn_protection"), callback_data=f"prot:menu:{channel_id}"),
            InlineKeyboardButton(t(lang, "btn_statistics"), callback_data=f"stat:menu:{channel_id}"),
        ],
        [
            InlineKeyboardButton(t(lang, "btn_channel_settings"), callback_data=f"set:menu:{channel_id}"),
            InlineKeyboardButton(t(lang, "btn_admins"), callback_data=f"adm:menu:{channel_id}"),
        ],
        [
            InlineKeyboardButton(t(lang, "btn_events"), callback_data=f"ev:menu:{channel_id}"),
            InlineKeyboardButton(t(lang, "btn_autocomplete"), callback_data=f"ac:menu:{channel_id}"),
        ],
        [
            InlineKeyboardButton(t(lang, "btn_forwarding"), callback_data=f"fw:menu:{channel_id}"),
            InlineKeyboardButton(t(lang, "btn_goodbye"), callback_data=f"gb:menu:{channel_id}"),
        ],
        [
            InlineKeyboardButton(t(lang, "btn_subscription"), callback_data=f"sub:menu:{channel_id}"),
            InlineKeyboardButton(t(lang, "btn_verify_admin"), callback_data=f"ch:verify:{channel_id}"),
        ],
        [
            InlineKeyboardButton(t(lang, "btn_channel_info"), callback_data=f"ch:info:{channel_id}"),
            InlineKeyboardButton(t(lang, "btn_refresh_channel"), callback_data=f"ch:refresh:{channel_id}"),
        ],
        [
            InlineKeyboardButton(t(lang, "btn_delete_channel"), callback_data=f"ch:del_confirm:{channel_id}"),
            InlineKeyboardButton(t(lang, "btn_change_channel"), callback_data="ch:switch"),
        ],
        [InlineKeyboardButton(t(lang, "btn_home"), callback_data="nav:home")],
    ]
    return InlineKeyboardMarkup(rows)


def channel_info_kb(lang: str, channel_id: int) -> InlineKeyboardMarkup:
    """Keyboard for the channel info/details page."""
    rows = [
        [
            InlineKeyboardButton(t(lang, "btn_refresh_channel"), callback_data=f"ch:refresh:{channel_id}"),
            InlineKeyboardButton(t(lang, "btn_verify_admin"), callback_data=f"ch:verify:{channel_id}"),
        ],
        [InlineKeyboardButton(t(lang, "btn_delete_channel"), callback_data=f"ch:del_confirm:{channel_id}")],
        [
            InlineKeyboardButton(t(lang, "btn_back"), callback_data=f"ch:open:{channel_id}"),
            InlineKeyboardButton(t(lang, "btn_home"), callback_data="nav:home"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def channel_delete_confirm_kb(lang: str, channel_id: int) -> InlineKeyboardMarkup:
    """Confirmation keyboard before deleting a channel."""
    rows = [
        [InlineKeyboardButton(t(lang, "btn_delete_confirm"), callback_data=f"ch:del_execute:{channel_id}")],
        [InlineKeyboardButton(t(lang, "btn_delete_cancel"), callback_data=f"ch:open:{channel_id}")],
    ]
    return InlineKeyboardMarkup(rows)


def switch_channel_kb(lang: str, channels: list[dict]) -> InlineKeyboardMarkup:
    """Channel picker for switching the active channel."""
    rows: list[list[InlineKeyboardButton]] = []
    for ch in channels:
        title = ch.get("title") or ch.get("username") or str(ch["telegram_chat_id"])
        rows.append([InlineKeyboardButton(f"\ud83d\udce2 {title}", callback_data=f"ch:open:{ch['id']}")])
    rows.append([
        InlineKeyboardButton(t(lang, "btn_add_channel"), callback_data="ch:add"),
        InlineKeyboardButton(t(lang, "btn_home"), callback_data="nav:home"),
    ])
    return InlineKeyboardMarkup(rows)


# ==================== Channel picker (for global section entry) ====================

def pick_channel_kb(lang: str, channels: list[dict], section: str) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for ch in channels:
        title = ch.get("title") or ch.get("username") or str(ch["telegram_chat_id"])
        rows.append([InlineKeyboardButton(f"📢 {title}", callback_data=f"{section}:menu:{ch['id']}")])
    rows.append([InlineKeyboardButton(t(lang, "btn_home"), callback_data="nav:home")])
    return InlineKeyboardMarkup(rows)


# ==================== 📜 Event Log ====================

def events_menu_kb(lang: str, channel_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_events_view_all"), callback_data=f"ev:list:{channel_id}:0")],
        [InlineKeyboardButton(t(lang, "btn_events_filter"), callback_data=f"ev:filter:{channel_id}")],
        [
            InlineKeyboardButton(t(lang, "btn_events_export"), callback_data=f"ev:export:{channel_id}"),
            InlineKeyboardButton(t(lang, "btn_events_clear"), callback_data=f"ev:clear:{channel_id}"),
        ],
        _row_back_home_cancel(lang, back_cb=f"ch:open:{channel_id}"),
    ]
    return InlineKeyboardMarkup(rows)


def events_filter_kb(lang: str, channel_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_filter_by_type"), callback_data=f"ev:fbytype:{channel_id}")],
        [InlineKeyboardButton(t(lang, "btn_filter_by_user"), callback_data=f"ev:fbyuser:{channel_id}")],
        [InlineKeyboardButton(t(lang, "btn_filter_by_date"), callback_data=f"ev:fbydate:{channel_id}")],
        [InlineKeyboardButton(t(lang, "btn_filter_reset"), callback_data=f"ev:list:{channel_id}:0")],
        _row_back_home_cancel(lang, back_cb=f"ev:menu:{channel_id}"),
    ]
    return InlineKeyboardMarkup(rows)


EVENT_TYPES = [
    "post_published", "post_scheduled", "admin_added", "admin_removed",
    "member_join", "member_leave", "settings_changed", "protection_changed",
    "forward_sent", "multisend", "other",
]


def events_type_pick_kb(lang: str, channel_id: int) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for t_key in EVENT_TYPES:
        rows.append([InlineKeyboardButton(
            t(lang, f"ev_type_{t_key}"),
            callback_data=f"ev:fbtype:{channel_id}:{t_key}",
        )])
    rows.append(_row_back_home_cancel(lang, back_cb=f"ev:filter:{channel_id}"))
    return InlineKeyboardMarkup(rows)


# ==================== 🤖 Autocomplete ====================

def autocomplete_menu_kb(lang: str, channel_id: int, sets: list[dict]) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(t(lang, "btn_ac_add"), callback_data=f"ac:add:{channel_id}")]]
    for s in sets:
        state = "🟢" if s.get("enabled") else "⚪"
        rows.append([InlineKeyboardButton(
            f"{state} {s['name']}",
            callback_data=f"ac:open:{s['id']}",
        )])
    rows.append(_row_back_home_cancel(lang, back_cb=f"ch:open:{channel_id}"))
    return InlineKeyboardMarkup(rows)


def autocomplete_set_kb(lang: str, set_id: int, channel_id: int, enabled: bool) -> InlineKeyboardMarkup:
    state = t(lang, "state_on") if enabled else t(lang, "state_off")
    rows = [
        [InlineKeyboardButton(t(lang, "btn_ac_edit_triggers"), callback_data=f"ac:trig:{set_id}")],
        [InlineKeyboardButton(t(lang, "btn_ac_edit_prefix"), callback_data=f"ac:pref:{set_id}")],
        [InlineKeyboardButton(t(lang, "btn_ac_edit_suffix"), callback_data=f"ac:suff:{set_id}")],
        [InlineKeyboardButton(t(lang, "btn_ac_toggle", state=state), callback_data=f"ac:toggle:{set_id}")],
        [InlineKeyboardButton(t(lang, "btn_ac_delete"), callback_data=f"ac:del:{set_id}")],
        _row_back_home_cancel(lang, back_cb=f"ac:menu:{channel_id}"),
    ]
    return InlineKeyboardMarkup(rows)


# ==================== 📤 Multi-send ====================

def multisend_menu_kb(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_ms_new"), callback_data="ms:new")],
        [InlineKeyboardButton(t(lang, "btn_ms_view"), callback_data="ms:list")],
        _row_back_home_cancel(lang, back_cb="nav:home"),
    ]
    return InlineKeyboardMarkup(rows)


def multisend_pick_post_kb(lang: str, drafts: list[dict]) -> InlineKeyboardMarkup:
    from .utils import short
    rows: list[list[InlineKeyboardButton]] = []
    for d in drafts:
        label = f"#{d['id']} [{d.get('channel_title', '')}] " + short(d.get("text") or d.get("caption"), 30)
        rows.append([InlineKeyboardButton(label, callback_data=f"ms:pickpost:{d['id']}")])
    rows.append(_row_back_home_cancel(lang, back_cb="ms:menu"))
    return InlineKeyboardMarkup(rows)


def multisend_targets_kb(lang: str, channels: list[dict], selected: set[int]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for ch in channels:
        mark = "✅" if ch["id"] in selected else "⬜"
        title = ch.get("title") or ch.get("username") or str(ch["telegram_chat_id"])
        rows.append([InlineKeyboardButton(f"{mark} {title}", callback_data=f"ms:target:{ch['id']}")])
    rows.append([
        InlineKeyboardButton(t(lang, "btn_ms_target_select_all"), callback_data="ms:target_all"),
        InlineKeyboardButton(t(lang, "btn_ms_target_clear"), callback_data="ms:target_clear"),
    ])
    rows.append([InlineKeyboardButton(t(lang, "btn_ms_continue"), callback_data="ms:continue")])
    rows.append(_row_back_home_cancel(lang, back_cb="ms:new"))
    return InlineKeyboardMarkup(rows)


def multisend_when_kb(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_ms_send_now"), callback_data="ms:when:now")],
        [InlineKeyboardButton(t(lang, "btn_ms_schedule"), callback_data="ms:when:sched")],
        _row_back_home_cancel(lang, back_cb="ms:back_targets"),
    ]
    return InlineKeyboardMarkup(rows)


def multisend_confirm_kb(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_ms_confirm"), callback_data="ms:confirm")],
        _row_back_home_cancel(lang, back_cb="ms:back_when"),
    ]
    return InlineKeyboardMarkup(rows)


def multisend_jobs_kb(lang: str, jobs: list[dict]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for j in jobs:
        rows.append([
            InlineKeyboardButton(t(lang, "btn_ms_job_view", id=j["id"]), callback_data=f"ms:jobview:{j['id']}"),
            InlineKeyboardButton(t(lang, "btn_ms_job_delete", id=j["id"]), callback_data=f"ms:jobdel:{j['id']}"),
        ])
    rows.append(_row_back_home_cancel(lang, back_cb="ms:menu"))
    return InlineKeyboardMarkup(rows)


# ==================== 🔁 Forwarding ====================

def forwarding_menu_kb(lang: str, channel_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_fw_add"), callback_data=f"fw:add:{channel_id}")],
        [InlineKeyboardButton(t(lang, "btn_fw_view"), callback_data=f"fw:list:{channel_id}")],
        _row_back_home_cancel(lang, back_cb=f"ch:open:{channel_id}"),
    ]
    return InlineKeyboardMarkup(rows)


def forwarding_list_kb(lang: str, channel_id: int, rules: list[dict]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for r in rules:
        state = t(lang, "state_on") if r.get("enabled") else t(lang, "state_off")
        rows.append([
            InlineKeyboardButton(t(lang, "btn_fw_toggle", state=state), callback_data=f"fw:toggle:{r['id']}"),
            InlineKeyboardButton(t(lang, "btn_fw_edit", id=r["id"]), callback_data=f"fw:edit:{r['id']}"),
            InlineKeyboardButton(t(lang, "btn_fw_delete", id=r["id"]), callback_data=f"fw:del:{r['id']}"),
        ])
    rows.append(_row_back_home_cancel(lang, back_cb=f"fw:menu:{channel_id}"))
    return InlineKeyboardMarkup(rows)


def forwarding_edit_pick_kb(lang: str, rule_id: int, channel_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_fw_edit_target"), callback_data=f"fw:edt:tgt:{rule_id}")],
        [InlineKeyboardButton(t(lang, "btn_fw_edit_filter"), callback_data=f"fw:edt:flt:{rule_id}")],
        _row_back_home_cancel(lang, back_cb=f"fw:list:{channel_id}"),
    ]
    return InlineKeyboardMarkup(rows)


# ==================== 👋 Goodbye ====================

def goodbye_menu_kb(lang: str, channel_id: int, settings: dict) -> InlineKeyboardMarkup:
    enabled = bool(settings.get("enabled"))
    ban = bool(settings.get("ban_on_leave"))
    en_state = t(lang, "state_on") if enabled else t(lang, "state_off")
    ban_state = t(lang, "state_on") if ban else t(lang, "state_off")
    rows = [
        [InlineKeyboardButton(f"{t(lang, 'btn_gb_toggle')} ({en_state})", callback_data=f"gb:toggle:{channel_id}")],
        [InlineKeyboardButton(t(lang, "btn_gb_set_message"), callback_data=f"gb:msg:{channel_id}")],
        [InlineKeyboardButton(f"{t(lang, 'btn_gb_toggle_ban')} ({ban_state})", callback_data=f"gb:ban:{channel_id}")],
        [
            InlineKeyboardButton(t(lang, "btn_gb_view"), callback_data=f"gb:view:{channel_id}"),
            InlineKeyboardButton(t(lang, "btn_gb_delete"), callback_data=f"gb:del:{channel_id}"),
        ],
        _row_back_home_cancel(lang, back_cb=f"ch:open:{channel_id}"),
    ]
    return InlineKeyboardMarkup(rows)


# ==================== 🆘 Support ====================

def support_menu_kb(lang: str, is_staff: bool) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_sup_new"), callback_data="sup:new")],
        [InlineKeyboardButton(t(lang, "btn_sup_my"), callback_data="sup:my")],
    ]
    if is_staff:
        rows.append([InlineKeyboardButton(t(lang, "btn_sup_admin_open"), callback_data="sup:openlist")])
    rows.append(_row_back_home_cancel(lang, back_cb="nav:home"))
    return InlineKeyboardMarkup(rows)


def support_list_kb(lang: str, tickets: list[dict], back_cb: str) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for tk in tickets:
        rows.append([InlineKeyboardButton(
            t(lang, "btn_sup_open_ticket", id=tk["id"]) + f" — {tk.get('subject', '')[:30]}",
            callback_data=f"sup:view:{tk['id']}",
        )])
    rows.append(_row_back_home_cancel(lang, back_cb=back_cb))
    return InlineKeyboardMarkup(rows)


def support_ticket_kb(lang: str, ticket_id: int, status: str, is_staff: bool) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(t(lang, "btn_sup_reply"), callback_data=f"sup:reply:{ticket_id}")]]
    if status == "open":
        rows.append([InlineKeyboardButton(t(lang, "btn_sup_close"), callback_data=f"sup:close:{ticket_id}")])
    else:
        rows.append([InlineKeyboardButton(t(lang, "btn_sup_reopen"), callback_data=f"sup:reopen:{ticket_id}")])
    back = "sup:openlist" if is_staff else "sup:my"
    rows.append(_row_back_home_cancel(lang, back_cb=back))
    return InlineKeyboardMarkup(rows)


# ==================== 🤖➕ Create bot ====================

def childbots_menu_kb(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_cb_add"), callback_data="cb:add")],
        [InlineKeyboardButton(t(lang, "btn_cb_view"), callback_data="cb:list")],
        _row_back_home_cancel(lang, back_cb="nav:home"),
    ]
    return InlineKeyboardMarkup(rows)


def childbots_list_kb(lang: str, bots: list[dict]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for b in bots:
        rows.append([InlineKeyboardButton(
            t(lang, "btn_cb_open", username=b.get("bot_username") or "?"),
            callback_data=f"cb:open:{b['id']}",
        )])
    rows.append(_row_back_home_cancel(lang, back_cb="cb:menu"))
    return InlineKeyboardMarkup(rows)


def childbot_view_kb(lang: str, bot_id: int, enabled: bool) -> InlineKeyboardMarkup:
    state = t(lang, "state_on") if enabled else t(lang, "state_off")
    rows = [
        [InlineKeyboardButton(t(lang, "btn_cb_toggle", state=state), callback_data=f"cb:toggle:{bot_id}")],
        [InlineKeyboardButton(t(lang, "btn_cb_delete"), callback_data=f"cb:del:{bot_id}")],
        _row_back_home_cancel(lang, back_cb="cb:list"),
    ]
    return InlineKeyboardMarkup(rows)


# ==================== 📘 Bot Guide ====================

GUIDE_SECTIONS = ["overview", "channels", "posts", "schedule", "protection",
                  "stats", "admins", "advanced", "faq"]


def guide_menu_kb(lang: str) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    pairs = [GUIDE_SECTIONS[i:i+2] for i in range(0, len(GUIDE_SECTIONS), 2)]
    for pair in pairs:
        row = [InlineKeyboardButton(t(lang, f"btn_guide_{s}"), callback_data=f"gd:show:{s}") for s in pair]
        rows.append(row)
    rows.append(_row_back_home_cancel(lang, back_cb="nav:home"))
    return InlineKeyboardMarkup(rows)


def guide_back_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([_row_back_home_cancel(lang, back_cb="gd:menu")])


# ==================== ⭐ Subscription ====================

def subscription_menu_kb(lang: str, channel_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_sub_add"), callback_data=f"sub:add:{channel_id}")],
        [InlineKeyboardButton(t(lang, "btn_sub_view"), callback_data=f"sub:list:{channel_id}")],
        [InlineKeyboardButton(t(lang, "btn_sub_check"), callback_data=f"sub:check:{channel_id}")],
        _row_back_home_cancel(lang, back_cb=f"ch:open:{channel_id}"),
    ]
    return InlineKeyboardMarkup(rows)


def subscription_list_kb(lang: str, channel_id: int, items: list[dict]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for s in items:
        state = t(lang, "state_on") if s.get("enabled") else t(lang, "state_off")
        rows.append([
            InlineKeyboardButton(t(lang, "btn_sub_toggle", state=state), callback_data=f"sub:toggle:{s['id']}"),
            InlineKeyboardButton(t(lang, "btn_sub_delete"), callback_data=f"sub:del:{s['id']}"),
        ])
    rows.append(_row_back_home_cancel(lang, back_cb=f"sub:menu:{channel_id}"))
    return InlineKeyboardMarkup(rows)


def post_options_kb(lang: str, channel_id: int, post_id: int, has_buttons: bool = False) -> InlineKeyboardMarkup:
    """The massive post control panel."""
    rows = [
        # Publish & Schedule
        [InlineKeyboardButton(t(lang, "btn_publish_now"), callback_data=f"post:publish:{post_id}")],
        [
            InlineKeyboardButton(t(lang, "btn_schedule_publish"), callback_data=f"sched:from_post:{post_id}"),
            InlineKeyboardButton(t(lang, "btn_make_recurring"), callback_data=f"rec:from_post:{post_id}")
        ],
        # Features
        [
            InlineKeyboardButton(t(lang, "btn_auto_delete"), callback_data=f"post:auto_del:{post_id}"),
            InlineKeyboardButton(t(lang, "btn_auto_reply"), callback_data=f"post:auto_reply:{post_id}")
        ],
        [
            InlineKeyboardButton(t(lang, "btn_reactions_settings"), callback_data=f"post:reactions:{post_id}"),
            InlineKeyboardButton(t(lang, "btn_crosspost"), callback_data=f"post:crosspost:{post_id}")
        ],
        # Edit Post Components
        [
            InlineKeyboardButton(t(lang, "btn_add_media"), callback_data=f"post:media:{channel_id}:{post_id}"),
            InlineKeyboardButton(
                t(lang, "btn_edit_buttons") if has_buttons else t(lang, "btn_add_buttons"),
                callback_data=f"post:buttons:{channel_id}:{post_id}"
            )
        ],
        # Settings & Save
        [InlineKeyboardButton(t(lang, "btn_advanced_settings"), callback_data=f"post:adv:{channel_id}")],
        [InlineKeyboardButton(t(lang, "btn_preview_publish"), callback_data=f"post:preview:{channel_id}")],
        [InlineKeyboardButton(t(lang, "btn_save_draft"), callback_data=f"ch:open:{channel_id}")],
    ]
    return InlineKeyboardMarkup(rows)


def preview_actions_kb(lang: str, channel_id: int, post_id: int) -> InlineKeyboardMarkup:
    # Kept for backward compatibility or direct previews
    rows = [
        [InlineKeyboardButton(t(lang, "btn_publish_now"), callback_data=f"post:publish:{post_id}")],
        [InlineKeyboardButton(t(lang, "btn_edit_post"), callback_data=f"post:edit:{post_id}")],
        _row_back_home_cancel(lang, back_cb=f"ch:open:{channel_id}"),
    ]
    return InlineKeyboardMarkup(rows)


def buttons_builder_menu_kb(lang: str, channel_id: int, post_id: int | None) -> InlineKeyboardMarkup:
    if post_id:
        back_cb = f"post:back_to_options:{channel_id}:{post_id}"
    else:
        back_cb = f"post:back_to_options:{channel_id}"
    rows = [
        [InlineKeyboardButton(t(lang, "btn_btnbuilder_wizard"), callback_data=f"btnbuild:start:{post_id or 0}")],
        [
            InlineKeyboardButton(t(lang, "btn_btnbuilder_favs"), callback_data=f"btnbuild:favs:{post_id or 0}"),
            InlineKeyboardButton(t(lang, "btn_btnbuilder_clear"), callback_data=f"btnbuild:clear:{post_id or 0}")
        ],
        _row_back_home_cancel(lang, back_cb=back_cb)
    ]
    return InlineKeyboardMarkup(rows)


def post_creation_settings_kb(
    lang: str,
    post_id: int,
    channel_id: int,
    *,
    parse_mode: str,
    silent: bool,
    protect: bool,
    pin: bool,
    signature_on: bool,
    link_preview_off: bool,
) -> InlineKeyboardMarkup:
    sig_state = t(lang, "state_on") if signature_on else t(lang, "state_off")
    lp_state = t(lang, "state_off") if link_preview_off else t(lang, "state_on")
    silent_state = t(lang, "state_on") if silent else t(lang, "state_off")
    protect_state = t(lang, "state_on") if protect else t(lang, "state_off")
    pin_state = t(lang, "state_on") if pin else t(lang, "state_off")

    rows = [
        [InlineKeyboardButton(t(lang, "btn_parse_mode", mode=parse_mode), callback_data=f"post:adv_parse:{post_id}")],
        [
            InlineKeyboardButton(t(lang, "btn_post_silent", state=silent_state), callback_data=f"post:adv_silent:{post_id}"),
            InlineKeyboardButton(t(lang, "btn_post_protect", state=protect_state), callback_data=f"post:adv_protect:{post_id}"),
        ],
        [
            InlineKeyboardButton(t(lang, "btn_post_pin", state=pin_state), callback_data=f"post:adv_pin:{post_id}"),
            InlineKeyboardButton(t(lang, "btn_toggle_signature", state=sig_state), callback_data=f"post:adv_sig:{post_id}"),
        ],
        [InlineKeyboardButton(t(lang, "btn_disable_preview", state=lp_state), callback_data=f"post:adv_lp:{post_id}")],
        [InlineKeyboardButton(t(lang, "btn_next_content"), callback_data=f"post:next_content:{post_id}")],
        _row_back_home_cancel(lang, back_cb=f"ch:open:{channel_id}"),
    ]
    return InlineKeyboardMarkup(rows)

def schedule_menu_kb(lang: str, channel_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_sched_new_post"), callback_data=f"sched:new_post:{channel_id}")],
        [InlineKeyboardButton(t(lang, "btn_sched_from_draft"), callback_data=f"sched:new:{channel_id}")],
        [
            InlineKeyboardButton(t(lang, "btn_sched_view_list"), callback_data=f"sched:list:{channel_id}"),
            InlineKeyboardButton(t(lang, "btn_sched_recurring"), callback_data=f"rec:menu:{channel_id}"),
        ],
        [InlineKeyboardButton(t(lang, "btn_sched_drafts"), callback_data=f"sched:drafts:{channel_id}")],
        _row_back_home_cancel(lang, back_cb=f"ch:open:{channel_id}"),
    ]
    return InlineKeyboardMarkup(rows)


def schedule_quick_time_kb(lang: str, post_id: int, channel_id: int) -> InlineKeyboardMarkup:
    """Quick time selection + back."""
    rows = [
        [
            InlineKeyboardButton(t(lang, "btn_plus_1h"),  callback_data=f"sched:qt:{post_id}:1"),
            InlineKeyboardButton(t(lang, "btn_plus_3h"),  callback_data=f"sched:qt:{post_id}:3"),
            InlineKeyboardButton(t(lang, "btn_plus_6h"),  callback_data=f"sched:qt:{post_id}:6"),
        ],
        [
            InlineKeyboardButton(t(lang, "btn_plus_12h"), callback_data=f"sched:qt:{post_id}:12"),
            InlineKeyboardButton(t(lang, "btn_plus_24h"), callback_data=f"sched:qt:{post_id}:24"),
        ],
        [
            InlineKeyboardButton(t(lang, "btn_tomorrow_same"), callback_data=f"sched:qt:{post_id}:tomorrow"),
            InlineKeyboardButton(t(lang, "btn_next_week"),      callback_data=f"sched:qt:{post_id}:week"),
        ],
        _row_back_home_cancel(lang, back_cb=f"sched:menu:{channel_id}"),
    ]
    return InlineKeyboardMarkup(rows)


def drafts_pick_kb(lang: str, channel_id: int, drafts: list[dict], action: str) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for d in drafts:
        from .utils import short
        label = t(lang, "draft_label", id=d["id"]) + " — " + short(d.get("text") or d.get("caption"), 30)
        rows.append([InlineKeyboardButton(label, callback_data=f"{action}:{d['id']}")])
    rows.append(_row_back_home_cancel(lang, back_cb=f"sched:menu:{channel_id}"))
    return InlineKeyboardMarkup(rows)


def scheduled_list_kb(lang: str, channel_id: int, scheduled: list[dict], tz_name: str) -> InlineKeyboardMarkup:
    from .utils import format_datetime
    rows: list[list[InlineKeyboardButton]] = []
    for s in scheduled:
        when = format_datetime(s["run_at"], tz_name)
        ctype = s.get("content_type") or "text"
        label = t(lang, "sched_item_line", id=s["id"], type=ctype, when=when)
        rows.append([InlineKeyboardButton(label, callback_data=f"sched:view:{s['id']}")])
    rows.append([InlineKeyboardButton(t(lang, "btn_add_channel") if not scheduled else t(lang, "btn_sched_from_draft"), callback_data=f"sched:new:{channel_id}")])
    rows.append(_row_back_home_cancel(lang, back_cb=f"sched:menu:{channel_id}"))
    return InlineKeyboardMarkup(rows)


def scheduled_item_kb(lang: str, sched_id: int, channel_id: int) -> InlineKeyboardMarkup:
    """Per-item actions: preview, postpone, publish-now, cancel."""
    rows = [
        [InlineKeyboardButton(t(lang, "btn_sched_view_content"), callback_data=f"sched:preview:{sched_id}")],
        [
            InlineKeyboardButton(t(lang, "btn_sched_postpone"),    callback_data=f"sched:postpone:{sched_id}"),
            InlineKeyboardButton(t(lang, "btn_sched_publish_now"), callback_data=f"sched:pubnow:{sched_id}"),
        ],
        [InlineKeyboardButton(t(lang, "btn_sched_delete"), callback_data=f"sched:delconfirm:{sched_id}")],
        [
            InlineKeyboardButton(t(lang, "btn_back"), callback_data=f"sched:list:{channel_id}"),
            InlineKeyboardButton(t(lang, "btn_home"), callback_data="nav:home"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def scheduled_postpone_kb(lang: str, sched_id: int, channel_id: int) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(t(lang, "btn_postpone_1h"),  callback_data=f"sched:pp:{sched_id}:1"),
            InlineKeyboardButton(t(lang, "btn_postpone_3h"),  callback_data=f"sched:pp:{sched_id}:3"),
            InlineKeyboardButton(t(lang, "btn_postpone_24h"), callback_data=f"sched:pp:{sched_id}:24"),
        ],
        [InlineKeyboardButton(t(lang, "btn_postpone_custom"), callback_data=f"sched:pp_custom:{sched_id}")],
        [
            InlineKeyboardButton(t(lang, "btn_back"), callback_data=f"sched:view:{sched_id}"),
            InlineKeyboardButton(t(lang, "btn_home"), callback_data="nav:home"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def scheduled_delete_confirm_kb(lang: str, sched_id: int, channel_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_sched_del_confirm"), callback_data=f"sched:del:{sched_id}")],
        [InlineKeyboardButton(t(lang, "btn_sched_del_cancel"),  callback_data=f"sched:view:{sched_id}")],
    ]
    return InlineKeyboardMarkup(rows)


def recurring_menu_kb(lang: str, channel_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_recurring_new"), callback_data=f"rec:new:{channel_id}")],
        [InlineKeyboardButton(t(lang, "btn_recurring_view"), callback_data=f"rec:list:{channel_id}")],
        _row_back_home_cancel(lang, back_cb=f"sched:menu:{channel_id}"),
    ]
    return InlineKeyboardMarkup(rows)


def frequency_pick_kb(lang: str, post_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_freq_daily"), callback_data=f"rec:freq:daily:{post_id}")],
        [InlineKeyboardButton(t(lang, "btn_freq_weekly"), callback_data=f"rec:freq:weekly:{post_id}")],
        [InlineKeyboardButton(t(lang, "btn_freq_monthly"), callback_data=f"rec:freq:monthly:{post_id}")],
        _row_back_home_cancel(lang, back_cb=f"rec:menu_back"),
    ]
    return InlineKeyboardMarkup(rows)


def recurring_list_kb(lang: str, channel_id: int, items: list[dict]) -> InlineKeyboardMarkup:
    from .utils import weekday_label
    rows: list[list[InlineKeyboardButton]] = []
    for r in items:
        if r["frequency"] == "daily":
            label = t(lang, "recurring_item_daily", id=r["id"], time=r["time_str"])
        elif r["frequency"] == "weekly":
            day = weekday_label(r.get("weekday") or "", lang)
            label = t(lang, "recurring_item_weekly", id=r["id"], day=day, time=r["time_str"])
        else:
            label = t(lang, "recurring_item_monthly", id=r["id"], day=r.get("day_of_month") or "?", time=r["time_str"])
        enabled = r.get("enabled", 1)
        toggle_btn = InlineKeyboardButton(
            t(lang, "btn_rec_toggle_off") if enabled else t(lang, "btn_rec_toggle_on"),
            callback_data=f"rec:toggle:{r['id']}",
        )
        rows.append([InlineKeyboardButton(label, callback_data=f"rec:view:{r['id']}")])
        rows.append([
            toggle_btn,
            InlineKeyboardButton(t(lang, "btn_rec_delete"), callback_data=f"rec:del:{r['id']}"),
        ])
    rows.append(_row_back_home_cancel(lang, back_cb=f"rec:menu:{channel_id}"))
    return InlineKeyboardMarkup(rows)


def delete_timer_ask_kb(lang: str, rec_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_add_delete_timer"), callback_data=f"rec:timer:{rec_id}")],
        [InlineKeyboardButton(t(lang, "btn_skip_delete_timer"), callback_data=f"rec:notimer:{rec_id}")],
        _row_back_home_cancel(lang, back_cb=f"rec:menu_back"),
    ]
    return InlineKeyboardMarkup(rows)


def protection_menu_kb(lang: str, channel: dict) -> InlineKeyboardMarkup:
    anti_spam = t(lang, "state_on") if channel.get("anti_spam_enabled") else t(lang, "state_off")
    anti_link = t(lang, "state_on") if channel.get("anti_link_enabled") else t(lang, "state_off")
    cid = channel["id"]
    rows = [
        [InlineKeyboardButton(t(lang, "btn_prot_join_filters"), callback_data=f"prot:joinf:{cid}")],
        [
            InlineKeyboardButton(t(lang, "btn_prot_anti_links", state=anti_link), callback_data=f"prot:links:{cid}"),
            InlineKeyboardButton(t(lang, "btn_prot_anti_spam", state=anti_spam), callback_data=f"prot:spam:{cid}")
        ],
        [
            InlineKeyboardButton(t(lang, "btn_prot_banned_words"), callback_data=f"prot:words:{cid}"),
            InlineKeyboardButton(t(lang, "btn_prot_punishments"), callback_data=f"prot:punish:{cid}")
        ],
        _row_back_home_cancel(lang, back_cb=f"ch:open:{cid}"),
    ]
    return InlineKeyboardMarkup(rows)

def protection_punishment_kb(lang: str, channel_id: int, max_warn: int, action: int) -> InlineKeyboardMarkup:
    # Highlights the selected option
    w1 = "🟢 " if max_warn == 1 else ""
    w3 = "🟢 " if max_warn == 3 else ""
    w5 = "🟢 " if max_warn == 5 else ""
    
    a1 = "🟢 " if action == 1 else ""
    a2 = "🟢 " if action == 2 else ""
    a3 = "🟢 " if action == 3 else ""
    
    rows = [
        [
            InlineKeyboardButton(w1 + t(lang, "btn_prot_warn_1"), callback_data=f"prot:p:w:1:{channel_id}"),
            InlineKeyboardButton(w3 + t(lang, "btn_prot_warn_3"), callback_data=f"prot:p:w:3:{channel_id}"),
            InlineKeyboardButton(w5 + t(lang, "btn_prot_warn_5"), callback_data=f"prot:p:w:5:{channel_id}")
        ],
        [
            InlineKeyboardButton(a1 + t(lang, "btn_prot_act_mute"), callback_data=f"prot:p:a:1:{channel_id}"),
            InlineKeyboardButton(a2 + t(lang, "btn_prot_act_kick"), callback_data=f"prot:p:a:2:{channel_id}"),
            InlineKeyboardButton(a3 + t(lang, "btn_prot_act_ban"), callback_data=f"prot:p:a:3:{channel_id}")
        ],
        _row_back_home_cancel(lang, back_cb=f"prot:menu:{channel_id}"),
    ]
    return InlineKeyboardMarkup(rows)


def join_filters_kb(lang: str, channel: dict) -> InlineKeyboardMarkup:
    channel_id = channel["id"]
    cap = t(lang, "state_on") if channel.get("captcha_enabled") else t(lang, "state_off")
    bb = t(lang, "state_on") if channel.get("block_bots") else t(lang, "state_off")
    rows = [
        [InlineKeyboardButton(t(lang, "btn_captcha", state=cap), callback_data=f"prot:captcha:{channel_id}")],
        [InlineKeyboardButton(t(lang, "btn_block_bots", state=bb), callback_data=f"prot:bots:{channel_id}")],
        [InlineKeyboardButton(t(lang, "btn_filter_names"), callback_data=f"prot:jf:names:{channel_id}")],
        [
            InlineKeyboardButton(t(lang, "btn_filter_total_ban"), callback_data=f"prot:jf:total:{channel_id}"),
            InlineKeyboardButton(t(lang, "btn_filter_multi_ban"), callback_data=f"prot:jf:multi:{channel_id}")
        ],
        [InlineKeyboardButton(t(lang, "btn_filter_alphabet"), callback_data=f"prot:jf:alpha:{channel_id}")],
        _row_back_home_cancel(lang, back_cb=f"prot:menu:{channel_id}"),
    ]
    return InlineKeyboardMarkup(rows)


def confirm_enable_kb(lang: str, enable_cb: str, disable_cb: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_enable"), callback_data=enable_cb)],
        [InlineKeyboardButton(t(lang, "btn_disable"), callback_data=disable_cb)],
        [
            InlineKeyboardButton(t(lang, "btn_back"), callback_data="nav:back"),
            InlineKeyboardButton(t(lang, "btn_cancel"), callback_data="nav:cancel"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def stats_menu_kb(lang: str, channel_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_stat_growth"), callback_data=f"stat:growth:{channel_id}")],
        [InlineKeyboardButton(t(lang, "btn_stat_engagement"), callback_data=f"stat:eng:{channel_id}")],
        [InlineKeyboardButton(t(lang, "btn_stat_views"), callback_data=f"stat:views:{channel_id}")],
        [InlineKeyboardButton(t(lang, "btn_stat_top"), callback_data=f"stat:top:{channel_id}")],
        _row_back_home_cancel(lang, back_cb=f"ch:open:{channel_id}"),
    ]
    return InlineKeyboardMarkup(rows)


def stats_period_kb(lang: str, channel_id: int, kind: str) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(t(lang, "btn_period_today"), callback_data=f"stat:p:{kind}:{channel_id}:1"),
            InlineKeyboardButton(t(lang, "btn_period_7"), callback_data=f"stat:p:{kind}:{channel_id}:7"),
        ],
        [
            InlineKeyboardButton(t(lang, "btn_period_30"), callback_data=f"stat:p:{kind}:{channel_id}:30"),
            InlineKeyboardButton(t(lang, "btn_period_90"), callback_data=f"stat:p:{kind}:{channel_id}:90"),
        ],
        _row_back_home_cancel(lang, back_cb=f"stat:menu:{channel_id}"),
    ]
    return InlineKeyboardMarkup(rows)


def settings_menu_kb(lang: str, channel: dict) -> InlineKeyboardMarkup:
    notif = t(lang, "state_on") if channel.get("notifications_enabled") else t(lang, "state_off")
    cid = channel["id"]
    rows = [
        [InlineKeyboardButton(t(lang, "btn_change_lang"), callback_data=f"set:lang:{cid}")],
        [InlineKeyboardButton(t(lang, "btn_timezone"), callback_data=f"set:tz:{cid}")],
        [InlineKeyboardButton(t(lang, "btn_signature"), callback_data=f"set:sig:{cid}")],
        [InlineKeyboardButton(t(lang, "btn_notifications", state=notif), callback_data=f"set:notif:{cid}")],
        _row_back_home_cancel(lang, back_cb=f"ch:open:{cid}"),
    ]
    return InlineKeyboardMarkup(rows)


def language_pick_kb(lang: str, channel_id: int | None = None, scope: str = "channel") -> InlineKeyboardMarkup:
    cid = channel_id if channel_id is not None else 0
    rows = [
        [InlineKeyboardButton(t(lang, "btn_lang_ar"), callback_data=f"lng:set:ar:{scope}:{cid}")],
        [InlineKeyboardButton(t(lang, "btn_lang_en"), callback_data=f"lng:set:en:{scope}:{cid}")],
        [
            InlineKeyboardButton(t(lang, "btn_back"), callback_data="nav:back"),
            InlineKeyboardButton(t(lang, "btn_home"), callback_data="nav:home"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def admins_menu_kb(lang: str, channel_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_admin_add"), callback_data=f"adm:add:{channel_id}")],
        [InlineKeyboardButton(t(lang, "btn_admin_view"), callback_data=f"adm:list:{channel_id}")],
        [InlineKeyboardButton(t(lang, "btn_admin_remove"), callback_data=f"adm:rmlist:{channel_id}")],
        _row_back_home_cancel(lang, back_cb=f"ch:open:{channel_id}"),
    ]
    return InlineKeyboardMarkup(rows)


PERMISSIONS_KEYS = ["publish", "edit", "delete", "protection", "stats", "settings"]


def admin_perms_kb(lang: str, username: str, selected: set[str]) -> InlineKeyboardMarkup:
    labels = {
        "publish": t(lang, "perm_publish"),
        "edit": t(lang, "perm_edit"),
        "delete": t(lang, "perm_delete"),
        "protection": t(lang, "perm_protection"),
        "stats": t(lang, "perm_stats"),
        "settings": t(lang, "perm_settings"),
    }
    rows: list[list[InlineKeyboardButton]] = []
    for p in PERMISSIONS_KEYS:
        mark = "✅" if p in selected else "⬜"
        rows.append([InlineKeyboardButton(f"{mark} {labels[p]}", callback_data=f"adm:perm:{p}")])
    rows.append([InlineKeyboardButton(t(lang, "btn_save_perms"), callback_data="adm:perm_save")])
    rows.append([
        InlineKeyboardButton(t(lang, "btn_back"), callback_data="nav:back"),
        InlineKeyboardButton(t(lang, "btn_cancel"), callback_data="nav:cancel"),
    ])
    return InlineKeyboardMarkup(rows)


def admins_remove_kb(lang: str, channel_id: int, admins: list[dict]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for a in admins:
        label = f"@{a.get('username') or a.get('user_id')}"
        rows.append([InlineKeyboardButton(f"🗑️ {label}", callback_data=f"adm:rm:{a['id']}:{channel_id}")])
    rows.append(_row_back_home_cancel(lang, back_cb=f"adm:menu:{channel_id}"))
    return InlineKeyboardMarkup(rows)


def change_menu_kb(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_switch_channel"), callback_data="ch:switch")],
        [InlineKeyboardButton(t(lang, "btn_change_bot_lang"), callback_data="lng:bot")],
        _row_back_home_cancel(lang, back_cb="nav:home"),
    ]
    return InlineKeyboardMarkup(rows)


def dev_menu_kb(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_dev_apikeys"), callback_data="dev:keys")],
        [InlineKeyboardButton(t(lang, "btn_dev_integrations"), callback_data="dev:integ")],
        [InlineKeyboardButton(t(lang, "btn_dev_logs"), callback_data="dev:logs")],
        [InlineKeyboardButton(t(lang, "btn_dev_restart"), callback_data="dev:restart")],
        _row_back_home_cancel(lang, back_cb="nav:home"),
    ]
    return InlineKeyboardMarkup(rows)


def apikeys_menu_kb(lang: str, keys: list[dict]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t(lang, "btn_apikey_add"), callback_data="dev:keyadd")],
    ]
    for k in keys:
        rows.append([
            InlineKeyboardButton(f"🔑 {k['service_name']}", callback_data="noop"),
            InlineKeyboardButton("🗑️", callback_data=f"dev:keydel:{k['id']}"),
        ])
    rows.append(_row_back_home_cancel(lang, back_cb="dev:menu"))
    return InlineKeyboardMarkup(rows)


def back_home_only_kb(lang: str, back_cb: str = "nav:back") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([_row_back_home_cancel(lang, back_cb=back_cb)])
