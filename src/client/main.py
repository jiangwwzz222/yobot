import asyncio
import json
import os

from aiocqhttp import CQHttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import yobot

conn = CQHttp(access_token='your-token',
              enable_http_post=False)

bot = yobot.Yobot()


@conn.on_message
async def handle_msg(context):
    if context["message_type"] != "group":
        return None
    reply = bot.proc(context)
    if reply != "":
        return {'reply': reply,
                'at_sender': False}
    else:
        return None


def scheduled_update():
    print("检查更新...")
    print(bot.execute("update"))


if os.path.exists("yobot_config.json"):
    with open("yobot_config.json", "r") as f:
        config = json.load(f)
        host = config.get("host", "127.0.0.1")
        port = config.get("port", 9222)
        update_time = config.get("update-time", "3:30")
        update_hour, update_minute = update_time.split(":")
else:
    host = "127.0.0.1"
    port = 9222
    update_hour = 3
    update_minute = 30

sche = AsyncIOScheduler()
trigger = CronTrigger(hour=update_hour, minute=update_minute)
sche.add_job(scheduled_update, trigger)

sche.start()
conn.run(host=host, port=port)
