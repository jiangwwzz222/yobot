import json
import os
import shutil
import sys
import zipfile

import requests



def update(path:int, localver:int=0):
    # path = os.path.dirname(sys.argv[0])
    if not os.path.exists(os.path.join(path, "temp")):
        os.mkdir(os.path.join(path, "temp"))
    with open(os.path.join(path, "version.json"), "r", encoding="utf-8") as f:
        ver = json.load(f)
    if ver["localver"] <= localver:
        print("已经是最新版本")
        return 1
    try:
        checkver = requests.get(ver["url"])
    except:
        print("无法连接到{}".format(ver["url"]))
        return 1
    if checkver.status_code != 200:
        print(ver["url"], "code:", checkver.status_code)
        return 1
    verinfo = json.loads(checkver.text)
    try:
        download_file = requests.get(verinfo["url"])
    except:
        print("无法连接到{}".format(verinfo["url"]))
        return 1
    if download_file.status_code != 200:
        print(verinfo["url"], "code:", download_file.status_code)
        return 1
    fname = os.path.basename(verinfo["url"])
    with open(os.path.join(path, "temp", fname), "wb") as f:
        f.write(download_file.content)
    verstr = str(verinfo["version"])
    if not os.path.exists(os.path.join(path, "temp", verstr)):
        os.mkdir(os.path.join(path, "temp", verstr))
    with zipfile.ZipFile(os.path.join(path, "temp", fname), "r") as z:
        z.extractall(path=os.path.join(path, "temp", verstr))
    os.remove(os.path.join(path, "temp", fname))
    # for ufile in os.listdir(os.path.join(path, "temp", verstr)):
    #     if os.path.exists(os.path.join(path, ufile)):
    #         os.remove(os.path.join(path, ufile))
    #     shutil.move(os.path.join(path, "temp", verstr, ufile),
    #                 os.path.join(path, ufile))
    # print("更新完成，目前版本："+verinfo["vername"])
    return 0


if __name__ == "__main__":
    update()
