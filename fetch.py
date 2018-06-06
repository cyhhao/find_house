# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from func import do_request, printx, write_file, read_file, send_mail

headers = {
    "Cookie": "gr_session_id_8da2730aaedd7628=1a58933a-ec21-4973-a991-f49f13c695e5_true; city_code=110000; Hm_lpvt_44cc5355c0465098b069e31666df21c5=1528126091; Hm_lvt_44cc5355c0465098b069e31666df21c5=1528126033; __utma=14049387.528542935.1511010920.1511010920.1528125835.2; __utmb=14049387.4.10.1528125835; __utmc=14049387; __utmz=14049387.1528125835.2.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; CURRENT_CITY_CODE=110000; hlwyfb_m_current_city_code=110000; curUrl=other; is_duanz=0; is_duy=0; is_first=0; is_wc=0; is_whole=%20; room=%20; sArea=; sAreaThree=; sArea_line_code=; sAreas=; sKeywords=; sPrice=0; sSort=0; sSubway=; sSubway_line_code=; sSubways=; history=[{%22flag%22:%22%22%2C%22keywords%22:%22%E6%B8%85%E5%8D%8E%E4%B8%9C%E8%B7%AF%E8%A5%BF%E5%8F%A3%22}%2C{%22flag%22:%226%22%2C%22keywords%22:%22%E7%99%BE%E5%BA%A6%E5%A4%A7%E5%8E%A6%22%2C%22value%22:%22116.301396%2C40.050909%22}]; __utmt=1; PHPSESSID=6391kef3mbg5nf6rgpk3o0lfc7; gr_user_id=16fac581-3163-4d14-8653-6de85fa5fda4",
    "Connection": "keep-alive",
    "Accept": "application/json;version=6",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Mobile/15E148 Safari/604.1",
    "Accept-Language": "zh-cn",
    "Referer": "http://m.ziroom.com/BJ/search?flag=&keywords=%E6%B8%85%E5%8D%8E%E4%B8%9C%E8%B7%AF%E8%A5%BF%E5%8F%A3&value=&more=",
    "DNT": "1"
}

HOUSE_URL = "http://www.ziroom.com/z/vr/{HOUSE_ID}.html"
LOCATION_STR = "min_lng=116.325195&max_lng=116.36269&min_lat=39.992719&max_lat=40.01583&clng=116.347442&clat=40.007402"


def get_villages():
    """
    获取小区列表
    :return:
    """
    result = []
    res = do_request("http://www.ziroom.com/map/room/count?{location}&zoom=16".format(location=LOCATION_STR), headers=headers)
    if not res:
        print("Count found list")
        return result

    return res.json()["data"]


def get_www(villages):
    """
    从 www 接口，取 退租配置中 的房子
    然鹅这个破接口取不到自如客转租的房子，只能用来监控装修配置中的房子
    1. 先获取小区列表
    2. 遍历小区，获取房源
    3. 遍历房源，进行过滤
    :return: [{
        "id": "", "status": "", "price": "", "area": "", "name": ""
    }]
    """
    result = []
    room_dict = {}
    for village in villages:
        print("[Searching] %s" % village["name"])

        vill_res = do_request("http://www.ziroom.com/map/room/list?{location}&zoom=17&resblock_id={village_id}".format(
            village_id=village["code"], location=LOCATION_STR
        ), headers=headers)

        if not vill_res or not vill_res.json() or len(vill_res.json()["data"]["rooms"]) == 0:
            continue

        for i in vill_res.json()["data"]["rooms"]:
            room_dict[i["id"]] = i

    for _id, room in room_dict.items():

        # 不考虑装修配置中和整租的房子
        if room["room_status"] in ["zxpzz", "dzz", "ycz"] or room["type_text"] == "整":
            continue

        # 不考虑价格太贵的
        price = min(room["sell_price"], room["sell_price_duanzu"]) if room["sell_price_duanzu"] != 0 else room["sell_price"]
        if price > 4000:
            continue

        result.append({
            "id": _id, "status": room["room_status"], "price": price,
            "area": room["usage_area"], "name": room["room_name"], "url": HOUSE_URL.format(HOUSE_ID=_id)
        })

    return result


def get_m(villages):
    """
    从 m 接口，取 转租 的房子
    :param villages:
    :return:
    """
    result = []
    mroom_dict = {}
    for village in villages:
        print("[Searching] %s" % village["name"])

        res = do_request("http://m.ziroom.com/v7/room/list.json?city_code=110000&page=1&type=1&price=&face=&rface=&hface=&feature=&around=&leasetype=&tag=&version=&area=&subway_code=&subway_station_code=&district_code=&bizcircle_code=&clng=&clat=&suggestion_type=4&suggestion_value=%s&keywords=%s&sort=" % (village["name"], village["name"]), headers=headers)

        for i in res.json()["data"]["rooms"]:
            mroom_dict[i["id"]] = i

    for _id, mroom in mroom_dict.items():

        # 只保留转租的房子
        if mroom["turn"] != 1 or mroom["status"] != "ycz":
            continue

        if mroom["price"] > 4000:
            continue

        # 辣鸡自如，转租的时候全部标记为已出租（实际上应该分为 立即预订/已预订），单独请求一次
        if mroom["status"] == "ycz":
            tres = do_request("http://m.ziroom.com/v7/room/detail.json?city_code=110000&id=%s" % _id,
                              headers=headers)

            if tres and tres.json()["data"]["turn"]["status"] == "yxd":
                continue

        result.append({
            "id": _id, "status": "转租中", "price": mroom["price"], "area": mroom["area"], "name": mroom["name"],
            "url": HOUSE_URL.format(HOUSE_ID=_id)
        })

    return result


def get_new_house(last, now):
    last_id = [i["id"] for i in last]
    now_id = [i["id"] for i in now]

    new_id = list(set(now_id) - set(last_id))
    result = []
    for i in now:
        if i["id"] in new_id:
            result.append(i)

    return result



def main():
    """
    1. 先获取小区列表
    2. 筛选出符合要求的房源
    3. 记录到
    :return:
    """
    villages = get_villages()
    result = []

    result.extend(get_www(villages))
    result.extend(get_m(villages))

    # 读取上一次的房源列表
    last_result = read_file("/home/fr1day/find_house/cache/last.json")

    # 对比一下差异
    new_houses = get_new_house(last_result, result)

    # 打印下日志
    printx(result)

    if new_houses:
        # 如果有新房出现，那么覆盖记录
        write_file("/home/fr1day/find_house/cache/last.json", result)

        mail_content = ""
        for i in new_houses:
            mail_content += "<a href=%s>%s</a> %d %d %s<br/>" % (i["url"], i["name"], i["price"], i["area"], i["status"])

        # 发现新房源，发送邮件提醒
        send_mail("649321688@qq.com", "发现自如新房源！！", mail_content)


if __name__ == '__main__':
    main()
    # send_mail("649321688@qq.com", "发现自如新房源！！", "2333")
    # get_all_rooms()
    # rooms, page = get_rooms("清华东路西口", "")
# print re.findall("站(\d+)米$", "距15号线六道口站1416米")
