# coding=utf-8
import json
import os
import sys

import check_ver
import dmg_record
import gacha
import jjc_consult
import lock_boss
import reserve
import switcher
import yobot_msg


class File_error(IOError):
    def __init__(self, s="file error"):
        self.error_filename = s


class Yobot:
    def __init__(self):
        dirname = os.path.dirname(sys.argv[0])
        config_f_path = os.path.join(dirname, "yobot_config.json")
        if not os.path.exists(config_f_path):
            raise File_error(config_f_path + " not exists")
        with open(config_f_path, "r", encoding="utf-8") as config_file:
            try:
                self.glo_setting = json.load(config_file)
            except:
                raise File_error(config_f_path + " been damaged")
        self.glo_setting["dirname"] = dirname

        # todo:先写上，等全部改好再回来改参数
        self.check = check_ver.Check(self.glo_setting)
        self.msg = yobot_msg.Message(self.glo_setting)
        self.gach = gacha.Gacha(self.glo_setting)
        self.jjc = jjc_consult.Consult(self.glo_setting)
        self.lok = lock_boss.Lock(self.glo_setting)
        self.record = dmg_record.Record(self.glo_setting)
        self.res = reserve.Reserve(self.glo_setting)

    def __del__(self):
        pass
