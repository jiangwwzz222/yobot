import json
import os
import platform
import shutil
import sys
import time
import zipfile

import requests


class Updater:
    def __init__(self, glo_setting: dict):
        self.evn = glo_setting["run-as"]
        self.path = glo_setting["dirname"]
        self.ver = glo_setting["version"]

    def check_ver(self) -> bool:
        return True

    def windows_update(self, force: bool = False):
        if not os.path.exists(os.path.join(self.path, "temp")):
            os.mkdir(os.path.join(self.path, "temp"))
        for url in self.ver["check_url"]:
            response = requests.get(url)
            if response.status_code == 200:
                break
        if response.status_code != 200:
            return "无法连接服务器"
        verinfo = json.loads(response.text)
        if not (force or verinfo["version"] > self.ver["ver_id"]):
            return "已经是最新版本"
        try:
            download_file = requests.get(verinfo["url"])
        except:
            return "无法连接到{}".format(verinfo["url"])
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
        cmd = '''@echo off
            cd /d "%~dp0"
            cacls.exe "%SystemDrive%\System Volume Information" >nul 2>nul
            if %errorlevel%==0 goto Admin
            if exist "%temp%\getadmin.vbs" del /f /q "%temp%\getadmin.vbs"
            echo Set RequestUAC = CreateObject^("Shell.Application"^)>"%temp%\getadmin.vbs"
            echo RequestUAC.ShellExecute "%~s0","","","runas",1 >>"%temp%\getadmin.vbs"
            echo WScript.Quit >>"%temp%\getadmin.vbs"
            "%temp%\getadmin.vbs" /f
            if exist "%temp%\getadmin.vbs" del /f /q "%temp%\getadmin.vbs"
            exit

            :Admin
            taskkill /f /im yobot.exe
            ping -n 1 127.0.0.1>nul
            del yobot.exe
            ren yobot.new.exe yobot.exe
            start yobot.exe
            exit
            '''
        with open(os.path.join(self.path, "update.bat"), "w") as f:
            f.write(cmd)
        os.system("start " + os.path.join(self.path, "update.bat"))
        return "更新完成"

    def linux_update(self, force: bool = False):
        git_dir = os.path.dirname(os.path.dirname(self.path))
        os.system("{}/update.sh".format(git_dir))
        raise KeyboardInterrupt()

    @staticmethod
    def match(cmd: str) -> int:
        if cmd == "更新":
            return 1
        elif cmd == "强制更新":
            return 2
        return 0

    def execute(self, match_num: int, msg: dict) -> dict:
        if match_num == 1:
            force = False
        elif match_num == 2:
            force = True
        if platform.system() == "Windows":
            if self.evn == "exe":
                reply = self.windows_update(force)
            elif self.evn == "py" or self.evn == "python":
                reply = self.windows_update_git(force)
        else:
            reply = self.linux_update(force)
        return {
            "reply": reply,
            "block": True
        }
