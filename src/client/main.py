import asyncio
import json
import os
import sys

from aiocqhttp import CQHttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import yobot

rcnb = CQHttp(access_token='token-yukikaze',
              enable_http_post=False)

bot = yobot.Yobot()


@rcnb.on_message
async def handle_msg(context):
    if context["message_type"] == "group" or context["message_type"] == "private":
        reply = bot.proc(context)
    else:
        reply = None
    if reply != "" and reply is not None:
        return {'reply': reply,
                'at_sender': False}
    else:
        return None


async def send_it(func):
    to_sends = func()
    tasks = [rcnb.send_msg(**kwargs) for kwargs in to_sends]
    await asyncio.gather(*tasks)


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
        input_para = True
        input_host, input_port = sys.argv[2].split(":")
        input_port = int(input_port)
    else:
        input_para = False
    if os.path.exists("yobot_config.json"):
        with open("yobot_config.json", "r") as f:
            config = json.load(f)
            if input_para:
                host, port = input_host, input_port
            else:
                host = config.get("host", "127.0.0.1")
                port = config.get("port", 9222)
    else:
        if input_para:
            host, port = input_host, input_port
        else:
            host = ask_for_input("请输入主机地址（默认为127.0.0.1）：", "127.0.0.1")
            port = ask_for_input("请输入绑定端口（8001~65535，默认为9222）：", "9222",
                                 convert=lambda x: int(x), check=str.isdigit)
        default_config = {
            "host": host,
            "port": port,
            "run-as": "python",
            "super-admin": [],
            "black-list": [],
            "setting-restrict": 3,
            "auto_update": True,
            "update-time": "3:30",
            "show_jjc_solution": "url",
            "gacha_on": True,
            "preffix_on": False,
            "preffix_string": "",
            "zht_in": False,
            "zht_out": False
        }
        with open("yobot_config.json", "w") as f:
            json.dump(default_config, f)

    jobs = bot.active_jobs()
    if jobs:
        sche = AsyncIOScheduler()
        for trigger, job in jobs:
            sche.add_job(send_it, trigger=trigger, args=(job,))
        sche.start()

    rcnb.run(host=host, port=port)
