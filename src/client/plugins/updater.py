import json
import os
import platform
import shutil
import sys
import zipfile
from typing import Any, Callable, Dict, Iterable, List, Tuple

import requests
from apscheduler.triggers.cron import CronTrigger


class Updater:
    Passive = True
    Active = True

    def __init__(self, glo_setting: dict, *args, **kwargs):
        self.evn = glo_setting["verinfo"]["run-as"]
        self.path = glo_setting["dirname"]
        self.ver = glo_setting["verinfo"]
        self.setting = glo_setting

    def windows_update(self, force: bool = False, test_ver: int = 0):
        test_version = ["stable", "beta", "alpha"][test_ver]
        if not os.path.exists(os.path.join(self.path, "temp")):
            os.mkdir(os.path.join(self.path, "temp"))
        server_available = False
        for url in self.ver["check_url"]:
            try:
                response = requests.get(url)
            except requests.ConnectionError:
                continue
            if response.status_code == 200:
                server_available = True
                break
        if not server_available:
            return "无法连接服务器"
        verinfo = json.loads(response.text)
        verinfo = verinfo[test_version]
        if not (force or verinfo["version"] > self.ver["ver_id"]):
            return "已经是最新版本"
        try:
            download_file = requests.get(verinfo["url"])
        except:
            return "下载失败：{}".format(verinfo["url"])
        if download_file.status_code != 200:
            return verinfo["url"] + "code:" + str(download_file.status_code)
        fname = os.path.basename(verinfo["url"])
        with open(os.path.join(self.path, "temp", fname), "wb") as f:
            f.write(download_file.content)
        verstr = str(verinfo["version"])
        if not os.path.exists(os.path.join(self.path, "temp", verstr)):
            os.mkdir(os.path.join(self.path, "temp", verstr))
        with zipfile.ZipFile(os.path.join(self.path, "temp", fname), "r") as z:
            z.extractall(path=os.path.join(self.path, "temp", verstr))
        os.remove(os.path.join(self.path, "temp", fname))
        shutil.move(os.path.join(self.path, "temp", verstr, "yobot.exe"),
                    os.path.join(self.path, "yobot.new.exe"))
        cmd = '''
            cd "{}"
            ping 127.0.0.1 -n 2 >nul
            taskkill /pid {} /f
            ping 127.0.0.1 -n 3 >nul
            del yobot.exe
            ren yobot.new.exe yobot.exe
            powershell Start-Process -FilePath "yobot.exe"
            '''.format(self.path, os.getpid())
        with open(os.path.join(self.path, "update.bat"), "w") as f:
            f.write(cmd)
        os.system('powershell Start-Process -FilePath "{}"'.format(
            os.path.join(self.path, "update.bat")))
        sys.exit()

    def windows_update_git(self, force: bool = False, test_ver: int = 0):
        git_dir = os.path.dirname(os.path.dirname(self.path))
        cmd = '''
        cd "{}"
        taskkill /pid {} /f
        git pull
        ping 127.0.0.1 -n 3 >nul
        powershell Start-Process -FilePath "python.exe" -ArgumentList "{}"
        '''.format(self.path, os.getpid(), os.path.join(self.path, "main.py"))
        with open(os.path.join(git_dir, "update.bat"), "w") as f:
            f.write(cmd)
        os.system('powershell Start-Process -FilePath "{}"'.format(
            os.path.join(git_dir, "update.bat")))
        sys.exit()

    def linux_update(self, force: bool = False, test_ver: int = 0):
        git_dir = os.path.dirname(os.path.dirname(self.path))
        cmd = '''
        cd "{}"
        git pull
        kill {}
        sleep 1s
        cd src/client
        python3 main.py
        '''.format(git_dir, os.getpid())
        with open(os.path.join(git_dir, "update.sh"), "w") as f:
            f.write(cmd)
        os.system("chmod u+x {0} && {0}".format(
            os.path.join(git_dir, "update.sh")))
        sys.exit()

    def restart(self):
        self_pid = os.getpid()
        if platform.system() == "Windows":
            if self.evn == "exe":
                cmd = '''
                    ping 127.0.0.1 -n 2 >nul
                    taskkill /pid {} /f
                    ping 127.0.0.1 -n 3 >nul
                    powershell Start-Process -FilePath "{}"
                    '''.format(self_pid, os.path.join(self.path, "yobot.exe"))
            elif self.evn == "py" or self.evn == "python":
                cmd = '''
                    ping 127.0.0.1 -n 2 >nul
                    taskkill /pid {} /f
                    ping 127.0.0.1 -n 3 >nul
                    powershell Start-Process -FilePath "python.exe" -ArgumentList "{}"
                    '''.format(self_pid, os.path.join(self.path, "main.py"))
            with open(os.path.join(self.path, "restart.bat"), "w") as f:
                f.write(cmd)
            os.system('powershell Start-Process -FilePath "{}"'.format(
                      os.path.join(self.path, "restart.bat")))
            sys.exit()
        else:
            cmd = '''
            kill {}
            sleep 1s
            cd {}
            python3 main.py
            '''.format(self_pid, self.path)
            with open(os.path.join(self.path, "restart.sh"), "w") as f:
                f.write(cmd)
            os.system("chmod u+x {0} && {0}".format(
                os.path.join(self.path, "restart.sh")))
            sys.exit()

    @staticmethod
    def match(cmd: str) -> int:
        if cmd.startswith("更新"):
            para = cmd[2:]
            match = 0x10
        elif cmd.startswith("强制更新"):
            para = cmd[4:]
            match = 0x20
        elif cmd == "重启" or cmd == "重新启动":
            return 0x40
        else:
            return 0
        para = para.replace(" ", "")
        if para == "alpha":
            ver = 2
        elif para == "beta":
            ver = 1
        elif para == "":
            ver = 0
        else:
            return 0
        return match | ver

    def execute(self, match_num: int, msg: dict = {}) -> dict:
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

        if match_num == 0x40:
            reply = self.restart()
            return {"reply": reply, "block": True}
        match = match_num & 0xf0
        ver = match_num & 0x0f
        if match == 0x10:
            force = False
        elif match == 0x20:
            force = True
        if platform.system() == "Windows":
            if self.evn == "exe":
                reply = self.windows_update(force, ver)
            elif self.evn == "py" or self.evn == "python":
                reply = self.windows_update_git(force, ver)
        else:
            reply = self.linux_update(force, ver)
        return {
            "reply": reply,
            "block": True
        }

    def update_auto(self) -> List[Dict[str, Any]]:
        print("自动检查更新...")
        if platform.system() == "Windows":
            if self.evn == "exe":
                reply = self.windows_update()
            elif self.evn == "py" or self.evn == "python":
                reply = self.windows_update_git()
        else:
            reply = self.linux_update()
        print(reply)
        return []

    def jobs(self) -> Iterable[Tuple[CronTrigger, Callable[[], List[Dict[str, Any]]]]]:
        if not self.setting.get("auto_update", True):
            return tuple()
        time = self.setting.get("update-time", "03:30")
        hour, minute = time.split(":")
        trigger = CronTrigger(hour=hour, minute=minute)
        job = (trigger, self.update_auto)
        return (job,)


def get_version(base_version: str, base_commit: Dict[str, int]) -> dict:
    if sys.argv[0].endswith(".exe"):
        return {
            "run-as": "exe",
            "ver_name": base_version,
            "ver_id": 3000 + sum(base_commit.values()),
            "check_url": [
                "https://gitee.com/yobot/yobot/raw/master/docs/v3/ver.json",
                "https://yuudi.github.io/yobot/v3/ver.json",
                "http://api.yobot.xyz/v3/version/"
            ]
        }
    with os.popen("git diff HEAD --stat") as r:
        text = r.read()
    if text != "":
        return {
            "run-as": "python",
            "commited": False,
            "ver_name": "yobot源码版\n基于{}\n未提交的版本".format(base_version)
        }
    with os.popen("git shortlog --numbered --summary") as r:
        summary = r.read()
    with os.popen("git rev-parse HEAD") as r:
        hash_ = r.read().strip()
    logs = summary.split()
    commits = {}
    for key in base_commit.keys():
        commits[key] = -base_commit[key]
    for count, usrmail in zip(logs[::2], logs[1::2]):
        usr = usrmail.split("@")[0].split("+")[-1]
        commits[usr] = int(count) + commits.get(usr, 0)
    vername = "yobot源码版\n{}".format(base_version)
    extra_commit = ["{}: {}".format(c, commits[c])
                    for c in commits if commits[c] != 0]
    if extra_commit:
        vername += "\n额外的提交：\n" + "\n".join(extra_commit)
    vername += "\nhash: {}".format(hash_)
    return {
        "run-as": "python",
        "commited": True,
        "ver_name": vername
    }
