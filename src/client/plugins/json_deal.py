import json
import re
import base64


def decodeFile(fileName):
    Path = "cont/"+fileName
    file = open(Path, 'r+')
    tmpStr = file.read()
    list =re.split('.+"(.+)".*', tmpStr)
    str = list[1]
    file.close()
    newStr = base64.b64decode(str)
    newPath = "out/"+fileName
    # os.mknod(newPath)
    newStr2 = newStr.decode("utf-8")
    newStr3 = newStr2.encode('utf-8').decode('unicode_escape')
    fp = open(newPath, "w", encoding='utf-8')
    fp.write(newStr3)
    fp.close()
    return


def decodejson( filename ):
    path = "out/"+filename
    file = open(path, 'r+', encoding='utf-8')
    tmpstr = file.read()
    tmpstr2 = tmpstr.replace('\\', '\\\\')
    delstr = json.loads(tmpstr2)
    file.close()
    return delstr
