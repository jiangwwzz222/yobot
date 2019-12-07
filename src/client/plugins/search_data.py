

store = {}


def calc_util_equip( utilid ):
    # if utilname in store['unit_data']:
    #     utilid = store['unit_data'][utilname]['unit_id']
    equipdata = store['unit_promotion'][utilid]
    rec = {}
    for key in equipdata:
        if equipdata[key]['equip_slot_1'] not in rec:
            rec[equipdata[key]['equip_slot_1']] = 0
        rec[equipdata[key]['equip_slot_1']] += 1

        if equipdata[key]['equip_slot_2'] not in rec:
            rec[equipdata[key]['equip_slot_2']] = 0
        rec[equipdata[key]['equip_slot_2']] += 1

        if equipdata[key]['equip_slot_3'] not in rec:
            rec[equipdata[key]['equip_slot_3']] = 0
        rec[equipdata[key]['equip_slot_3']] += 1

        if equipdata[key]['equip_slot_4'] not in rec:
            rec[equipdata[key]['equip_slot_4']] = 0
        rec[equipdata[key]['equip_slot_4']] += 1

        if equipdata[key]['equip_slot_5'] not in rec:
            rec[equipdata[key]['equip_slot_5']] = 0
        rec[equipdata[key]['equip_slot_5']] += 1

        if equipdata[key]['equip_slot_6'] not in rec:
            rec[equipdata[key]['equip_slot_6']] = 0
        rec[equipdata[key]['equip_slot_6']] += 1
    retstr = ""
    for key in rec:
        if int(key) < 500000:
            name = store['equipment_data'][key]['equipment_name']
            count = rec[key]
            retstr += name + ":" + str(count)
            retstr += "#换行符"
    return retstr
    # else:
    #     return ""
