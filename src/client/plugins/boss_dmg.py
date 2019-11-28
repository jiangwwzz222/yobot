# 把不想改的祖传代码封装一下

from plugins import dmg_record, lock_boss, reserve


class Boss_dmg:
    def __init__(self, glo_setting: dict):
        pass

    @staticmethod
    def match(cmd: str) -> int:
        func = lock_boss.Lock.match(cmd)
        if func != 0:
            return func | 0x1000
        func = dmg_record.Record.match(cmd)
        if func != 0:
            return func | 0x2000
        func = reserve.Reserve.match(cmd)
        if func != 0:
            return func | 0x3000
        return 0

    def execute(self, match_num: int, msg: dict) -> dict:
        swit = match_num & 0xf000
        func = match_num & 0x0fff
        cmd_list = (str(msg["group_id"]),
                    str(msg["sender"]["user_id"]),
                    msg["sender"]["card"])
        cmd = msg["raw_message"]
        txt_list = []
        if swit == 0x1000:
            lockboss = lock_boss.Lock(cmd_list[:3])
            lockboss.lockboss(cmd, func, comment=cmt)
            txt_list.extend(lockboss.txt_list)
        if swit == 0x2000:
            report = dmg_record.Record(cmd_list[:3])
            report.rep(cmd, func)
            txt_list.extend(report.txt_list)
            if (cmd.endswith("尾刀") or cmd.endswith("收尾")
                    or cmd.endswith("收掉") or cmd.endswith("击败")):
                rsv = reserve.Reserve(cmd_list[:3])
                rsv.rsv(cmd, 0x20)
                txt_list.extend(rsv.txt_list)
        if swit == 0x3000:
            rsv = reserve.Reserve(cmd_list[:3])
            rsv.rsv(cmd, func)
            txt_list.extend(rsv.txt_list)
        return {
            "reply": "\n".join(txt_list),
            "block": True}
