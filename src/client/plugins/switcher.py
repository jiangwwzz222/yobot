import base64
import hashlib
import json
import os
from typing import Union
from urllib.parse import quote

import requests

from plugins import shorten_url


class Switcher:
    Passive = True
    Active = False
    code_api = "http://api.yobot.xyz/v3/coding/?code="
    setting_url = {
        "global": "http://io.yobot.monster/3.0.1/settings/",
        'pool': 'http://io.yobot.monster/3.1.0/pool/',
        'mail': 'http://io.yobot.monster/3.1.0/mail/',
        'news': 'http://io.yobot.monster/3.1.2/news/'
    }

    def __init__(self, glo_setting: dict, *args, **kwargs):
        self.setting = glo_setting

    def save_settings(self) -> None:
        save_setting = self.setting.copy()
        del save_setting["dirname"]
        del save_setting["verinfo"]
        config_path = os.path.join(
            self.setting["dirname"], "yobot_config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(save_setting, f, indent=4, ensure_ascii=False)

    def get_url_content(self, url: str) -> Union[int, str]:
        try:
            res = requests.get(url)
        except requests.exceptions.ConnectionError:
            return -1
        if res.status_code != 200:
            return res.status_code
        else:
            return res.text

    @staticmethod
    def match(cmd: str) -> int:
        # if cmd.startswith("打开"):
        #     f = 0x100
        # elif cmd.startswith("关闭"):
        #     f = 0x200
        if cmd == "设置":
            f = 0x300
        elif cmd.startswith("设置码"):
            f = 0x400
        elif cmd.startswith("设置"):
            f = 0x500
        else:
            f = 0
        return f

    def dump_url(self) -> str:
        setting_dict = self.setting.copy()
        drop_keys = ("host", "port", "dirname", "version")
        for key in drop_keys:
            del setting_dict[key]
        query = json.dumps(setting_dict, separators=(',', ':'))
        full_url = self.setting_url["global"] + "?form=" + quote(query)
        return shorten_url.shorten(full_url)

    def setting_pool(self, pool: dict) -> str:
        pool["info"] = {"name": "自定义卡池"}
        poolfile = os.path.join(self.setting["dirname"], "pool.json")
        with open(poolfile, "w", encoding="utf-8") as f:
            json.dump(pool, f, indent=4, ensure_ascii=False)
        return "设置成功，重启后生效\n发送“重启”可自动重新启动"

    def setting_mail(self, code: str) -> str:
        while code.endswith('='):
            code = '=' + code[:-1]
        try:
            raw = base64.b64decode(code[::-1])
            confirm = raw[:32].decode()
            data = raw[32:]
            md5 = hashlib.md5(data)
            assert confirm == md5.hexdigest()
            config = json.loads(data.decode())
        except:
            return '设置码不完整，请检查'
        mailfile = os.path.join(self.setting["dirname"], "mailconf.json")
        if not os.path.exists(mailfile):
            return '未初始化'
        if config['s'] == '':
            config['s'] = 'smtp.' + config['m'].split('@')[1]
        if config['n'] == '':
            config['n'] = config['m']
        with open(mailfile, "r+") as f:
            mailconf = json.load(f)
            mailconf['sender'] = {
                "host": config['s'],
                "user": config['m'],
                "pswd": config['p'],
                "sender": config['n']
            }
            f.seek(0)
            f.truncate()
            json.dump(mailconf, f, indent=4)
        return '设置成功'

    def execute(self, match_num: int, msg: dict) -> dict:
        super_admins = self.setting.get("super-admin", list())
        restrict = self.setting.get("setting-restrict", 3)
        if msg["sender"]["user_id"] in super_admins:
            role = 0
        else:
            role_str = msg["sender"].get("role", None)
            if role_str == "owner":
                role = 1
            elif role_str == "admin":
                role = 2
            else:
                role = 3
        if role > restrict:
            reply = "你的权限不足"
            return {"reply": reply, "block": True}

        cmd = msg["raw_message"]
        if match_num == 0x300:
            reply = (self.dump_url() + "\n请在此页进行设置，完成后发送设置码即可\n"
                     "其他设置请发送“设置卡池”、“设置邮箱”、“设置新闻”")
        elif match_num == 0x400:
            in_code = cmd[3:]
            res = self.get_url_content(self.code_api+in_code)
            if isinstance(res, int):
                reply = "服务器错误：{}".format(res)
                return {"reply": reply, "block": True}
            try:
                new_setting = json.loads(res)
            except json.JSONDecodeError:
                reply = "服务器返回值异常"
                return {"reply": reply, "block": True}
            version = new_setting.get("version", 0)
            if version == 2999:
                self.setting.update(new_setting["settings"])
                self.save_settings()
                reply = "设置成功"
            elif version == 3098:
                reply = self.setting_pool(new_setting["settings"])
            elif version == 3099:
                reply = self.setting_mail(new_setting["settings"])
            elif version == 3102:
                self.setting.update(new_setting["settings"])
                self.save_settings()
                reply = "设置成功"
            else:
                reply = "设置码版本错误"
        elif match_num == 0x500:
            if cmd == "设置卡池":
                reply = self.setting_url["pool"]
            elif cmd == "设置邮箱":
                reply = self.setting_url["mail"]
            elif cmd == "设置新闻":
                reply = self.setting_url["news"]
            else:
                reply = "未知的设置"

        return {
            "reply": reply,
            "block": True
        }
