#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import ntplib
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler

# Time fix: Patch time.time before anything else
try:
    time._orig_time = time.time
    ntp = ntplib.NTPClient()
    response = ntp.request("pool.ntp.org")
    offset = response.offset
    time.time = lambda: time._orig_time() + offset
    print(f"[Time Fix] NTP time offset: {offset}")
except Exception as e:
    print(f"[Time Fix] NTP sync failed: {e}")

# Now import your bot components
from bot import (
    APP_ID,
    API_HASH,
    AUTH_USERS,
    DOWNLOAD_LOCATION,
    LOGGER,
    TG_BOT_TOKEN,
    BOT_USERNAME,
    SESSION_NAME,
    DATABASE_URL
)

from bot.plugins.new_join_fn import help_message_f
from bot.plugins.incoming_message_fn import (
    incoming_start_message_f,
    incoming_compress_message_f,
    incoming_cancel_message_f
)
from bot.plugins.admin import sts, ban, unban, _banned_usrs
from bot.plugins.broadcast import broadcast_
from bot.plugins.status_message_fn import exec_message_f, upload_log_file
from bot.commands import Command
from bot.plugins.call_back_button_handler import button

if not os.path.isdir(DOWNLOAD_LOCATION):
    os.makedirs(DOWNLOAD_LOCATION, exist_ok=True)

app = Client(
    SESSION_NAME,
    bot_token=TG_BOT_TOKEN,
    api_id=APP_ID,
    api_hash=API_HASH,
    workers=2
)
app.set_parse_mode("html")

# Handlers
app.add_handler(MessageHandler(sts, filters.command("status") & filters.user(AUTH_USERS)))
app.add_handler(MessageHandler(ban, filters.command("ban_user") & filters.user(AUTH_USERS)))
app.add_handler(MessageHandler(unban, filters.command("unban_user") & filters.user(AUTH_USERS)))
app.add_handler(MessageHandler(_banned_usrs, filters.command("banned_users") & filters.user(AUTH_USERS)))
app.add_handler(MessageHandler(broadcast_, filters.command("broadcast") & filters.user(AUTH_USERS) & filters.reply))
app.add_handler(MessageHandler(incoming_start_message_f, filters.command(["start", f"start@{BOT_USERNAME}"])))
app.add_handler(MessageHandler(incoming_compress_message_f, filters.command(["compress", f"compress@{BOT_USERNAME}"])))
app.add_handler(MessageHandler(incoming_cancel_message_f, filters.command(["cancel", f"cancel@{BOT_USERNAME}"]) & filters.chat(AUTH_USERS)))
app.add_handler(MessageHandler(exec_message_f, filters.command(["exec", f"exec@{BOT_USERNAME}"]) & filters.chat(AUTH_USERS)))
app.add_handler(MessageHandler(help_message_f, filters.command(["help", f"help@{BOT_USERNAME}"])))
app.add_handler(MessageHandler(upload_log_file, filters.command(["log", f"log@{BOT_USERNAME}"]) & filters.chat(AUTH_USERS)))
app.add_handler(CallbackQueryHandler(button))

app.run()
