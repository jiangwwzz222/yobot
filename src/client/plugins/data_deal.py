from plugins import search_data, json_deal
import os

contPath = "cont"
outPath = "cont"


def init():
    print(os.listdir(contPath))
    for top, dirs, nondirs in os.listdir(contPath):
        for item in nondirs:
            print("json init" + item)
            json_deal.decodeFile(item)

    for top, dirs, nondirs in os.walk(outPath):
        for item in nondirs:
            print("out init" + item)
            search_data.store[item[:-4]] = json_deal.decodejson(item)
    util_data = search_data.store['unit_data']
    unit_promotion = search_data.store['unit_promotion']
    equipment_data = search_data.store['equipment_data']
    list = {}
    list2 = {}
    list3 = {}
    for data in util_data:
        if int(data['unit_id']) < 200000:
            list[data['unit_name']] = data
    search_data.store['unit_data'] = list
    for data in unit_promotion:
        if data['unit_id'] in list2:
            list2[data['unit_id']][data['promotion_level']] = data
        else:
            list2[data['unit_id']] = {}
            list2[data['unit_id']][data['promotion_level']] = data
    search_data.store['unit_promotion'] = list2
    for data in equipment_data:
        if int(data['equipment_id']) < 500000:
            list3[data['equipment_id']] = data
    search_data.store['equipment_data'] = list3

