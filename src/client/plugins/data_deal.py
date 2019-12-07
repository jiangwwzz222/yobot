from plugins import search_data, json_deal
import os
from opencc import OpenCC


contPath = "./plugins/cont"
outPath = "./plugins/cont"


def init():
    t2s = OpenCC("t2s")
    for item in os.listdir(contPath):
        json_deal.decodeFile(item)

    for item in os.listdir(contPath):
        search_data.store[item[:-4]] = json_deal.decodejson(item)
    util_data = search_data.store['unit_data']
    unit_promotion = search_data.store['unit_promotion']
    equipment_data = search_data.store['equipment_data']
    list = {}
    list2 = {}
    list3 = {}
    for data in util_data:
        if int(data['unit_id']) < 200000:
            list[t2s.convert(data['unit_name'])] = data
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

