# coding=utf-8
import json
import os
import sys
from typing import List

from plugins import check_ver, switcher, yobot_msg, gacha, jjc_consult, boss_dmg, updater, yobot_errors


class Yobot:
    def __init__(self):
        # dirname = os.__file__
        dirname = os.getcwd()
        config_f_path = os.path.join(dirname, "yobot_config.json")
        if not os.path.exists(config_f_path):
            with open(config_f_path, "w", encoding="utf-8") as config_file:
                config_file.write('{"port":9222,"run-as":"exe"}')
        with open(config_f_path, "r", encoding="utf-8") as config_file:
            try:
                self.glo_setting = json.load(config_file)
            except:
                raise yobot_errors.File_error(
                    config_f_path + " been damaged")

        inner_info = {
            "dirname": dirname,
            "version": {
                "ver_name": "yobot[v3.0.0-beta-2]",
                "ver_id": 2912,
                "checktime": 0,
                "latest": True,
                "check_url": ["https://gitee.com/yobot/yobot/raw/master/docs/v3/ver.json",
                              "https://yuudi.github.io/yobot/v3/ver.json",
                              "http://api.yobot.xyz/v3/version/"]}}
        self.glo_setting.update(inner_info)

        self.plugins = [
            updater.Updater(self.glo_setting),
            switcher.Switcher(self.glo_setting),
            yobot_msg.Message(self.glo_setting),
            gacha.Gacha(self.glo_setting),
            jjc_consult.Consult(self.glo_setting),
            boss_dmg.Boss_dmg(self.glo_setting)
        ]

    def proc(self, msg: dict) -> str:
        if msg["sender"].get("card", "") == "":
            msg["sender"]["card"] = msg["sender"]["nickname"]
        replys = []
        for pitem in self.plugins:
            func_num = pitem.match(msg["raw_message"])
            if func_num:
                res = pitem.execute(func_num, msg)
                replys.append(res["reply"])
                if res["block"]:
                    break
        return "\n".join(replys)

    def execute(self, cmd: str):
        if cmd == "update":
            self.plugins[0].execute(0x10)
