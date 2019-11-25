import asyncio
import json
import os
import sys

from aiocqhttp import CQHttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import yobot
import plugins.updater

conn = CQHttp(access_token='your-token',
              enable_http_post=False)

bot = yobot.Yobot()


@conn.on_message
async def handle_msg(context):
    if context["message_type"] != "group":
        return None
    reply = bot.proc(context)
    if reply != "" and reply is not None:
        return {'reply': reply,
                'at_sender': False}
    else:
        return None


def scheduled_update():
    print("检查更新...")
    print(bot.execute("update"))


def ask_for_input(msg: str, default: str = "",
                  convert: callable = None, check: callable = None):
    flag = True
    while flag:
        print(msg, end="")
        instr = input()
        if instr == "":
            instr = default
        if check is not None:
            if check(instr):
                flag = False
            else:
                print("输入无效")
        else:
            flag = False
    if convert is not None:
        return convert(instr)
    else:
        return instr


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        host, port = sys.argv[2].split(":")
        port = int(port)
        update_hour = 3
        update_minute = 30
    elif os.path.exists("yobot_config.json"):
        with open("yobot_config.json", "r") as f:
            config = json.load(f)
            host = config.get("host", "127.0.0.1")
            port = config.get("port", 9222)
            update_time = config.get("update-time", "3:30")
            update_hour, update_minute = update_time.split(":")
    else:
        host = ask_for_input("请输入主机地址（默认为127.0.0.1）：", "127.0.0.1")
        port = ask_for_input("请输入绑定端口（8001~65535，默认为9222）：", "9222",
                             convert=lambda x: int(x), check=str.isdigit)
        update_hour = 3
        update_minute = 30

    sche = AsyncIOScheduler()
    trigger = CronTrigger(hour=update_hour, minute=update_minute)
    sche.add_job(scheduled_update, trigger)

    sche.start()
    conn.run(host=host, port=port)
