#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K | @AbirHasan2005

# the logging things
import logging
logging.basicConfig(
    level=logging.DEBUG, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)

import asyncio
import os
import time
import re
import json
import subprocess
import math
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.helper_funcs.display_progress import TimeFormatter
from bot.localisation import Localisation
from bot import (
    FINISHED_PROGRESS_STR,
    UN_FINISHED_PROGRESS_STR,
    DOWNLOAD_LOCATION
)

async def convert_video(video_file, output_directory, total_time, bot, message, target_percentage, isAuto, bug):
    out_put_file_name = output_directory + "/" + str(round(time.time())) + ".mp4"
    progress = output_directory + "/" + "progress.txt"
    with open(progress, 'w') as f:
        pass

    file_genertor_command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "quiet",
        "-progress",
        progress,
        "-i",
        video_file,
        "-c:v", 
        "h264",
        "-preset", 
        "ultrafast",
        "-tune",
        "film",
        "-c:a",
        "copy",
        out_put_file_name
    ]

    if not isAuto:
        filesize = os.stat(video_file).st_size
        calculated_percentage = 100 - target_percentage
        target_size = (calculated_percentage / 100) * filesize
        target_bitrate = int(math.floor(target_size * 8 / total_time))
        if target_bitrate // 1000000 >= 1:
            bitrate = str(target_bitrate // 1000000) + "M"
        elif target_bitrate // 1000 > 1:
            bitrate = str(target_bitrate // 1000) + "k"
        else:
            return None
        extra = ["-b:v", bitrate, "-bufsize", bitrate]
        for elem in reversed(extra):
            file_genertor_command.insert(10, elem)
    else:
        target_percentage = 'auto'

    COMPRESSION_START_TIME = time.time()
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    LOGGER.info("ffmpeg_process: " + str(process.pid))
    status = output_directory + "/status.json"
    with open(status, 'r+') as f:
        statusMsg = json.load(f)
        statusMsg['pid'] = process.pid
        statusMsg['message'] = message.message_id
        f.seek(0)
        json.dump(statusMsg, f, indent=2)

    isDone = False
    while process.returncode != 0:
        await asyncio.sleep(3)
        with open(DOWNLOAD_LOCATION + "/progress.txt", 'r+') as file:
            text = file.read()
            frame = re.findall(r"frame=(\d+)", text)
            time_in_us = re.findall(r"out_time_ms=(\d+)", text)
            progress = re.findall(r"progress=(\w+)", text)
            speed = re.findall(r"speed=(\d+\.?\d*)", text)

            frame = int(frame[-1]) if frame else 1
            speed = speed[-1] if speed else 1
            time_in_us = time_in_us[-1] if time_in_us else 1

            if progress and progress[-1] == "end":
                LOGGER.info(progress[-1])
                isDone = True
                break

            execution_time = TimeFormatter((time.time() - COMPRESSION_START_TIME) * 1000)
            elapsed_time = int(time_in_us) / 1000000
            difference = math.floor((total_time - elapsed_time) / float(speed))
            ETA = TimeFormatter(difference * 1000) if difference > 0 else "-"

            percentage = math.floor(elapsed_time * 100 / total_time)
            progress_str = "📊 <b>Progress:</b> {0}%\n[{1}{2}]".format(
                round(percentage, 2),
                ''.join([FINISHED_PROGRESS_STR for _ in range(math.floor(percentage / 10))]),
                ''.join([UN_FINISHED_PROGRESS_STR for _ in range(10 - math.floor(percentage / 10))])
            )
            stats = f'📦️ <b>Compressing</b> {target_percentage}%\n\n' \
                    f'⏰️ <b>ETA:</b> {ETA}\n\n' \
                    f'{progress_str}\n'

            try:
                await message.edit_text(
                    text=stats,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton('❌ Cancel ❌', callback_data='fuckingdo')]
                    ])
                )
            except:
                pass

            try:
                await bug.edit_text(text=stats)
            except:
                pass

    stdout, stderr = await process.communicate()
    LOGGER.info(stderr.decode().strip())
    LOGGER.info(stdout.decode().strip())

    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None

async def media_info(saved_file_path):
    process = subprocess.Popen(
        ["ffmpeg", "-hide_banner", "-i", saved_file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    stdout, _ = process.communicate()
    output = stdout.decode().strip()
    duration = re.search(r"Duration:\s*(\d*):(\d*):(\d+\.?\d*)[\s\w*$]", output)
    bitrates = re.search(r"bitrate:\s*(\d+)[\s\w*$]", output)

    if duration:
        hours = int(duration.group(1))
        minutes = int(duration.group(2))
        seconds = math.floor(float(duration.group(3)))
        total_seconds = (hours * 3600) + (minutes * 60) + seconds
    else:
        total_seconds = None

    bitrate = bitrates.group(1) if bitrates else None
    return total_seconds, bitrate

async def take_screen_shot(video_file, output_directory, ttl):
    out_put_file_name = os.path.join(
        output_directory,
        str(time.time()) + ".jpg"
    )
    if video_file.upper().endswith(("MKV", "MP4", "WEBM")):
        file_genertor_command = [
            "ffmpeg",
            "-ss", str(ttl),
            "-i", video_file,
            "-vframes", "1",
            out_put_file_name
        ]
        process = await asyncio.create_subprocess_exec(
            *file_genertor_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()

    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None
