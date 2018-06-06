# -*- coding: utf-8 -*-
from __future__ import unicode_literals


import re
from urllib.parse import urlencode
from func import do_request, printx

headers = {
    "Cookie": "gr_session_id_8da2730aaedd7628=1a58933a-ec21-4973-a991-f49f13c695e5_true; city_code=110000; Hm_lpvt_44cc5355c0465098b069e31666df21c5=1528126091; Hm_lvt_44cc5355c0465098b069e31666df21c5=1528126033; __utma=14049387.528542935.1511010920.1511010920.1528125835.2; __utmb=14049387.4.10.1528125835; __utmc=14049387; __utmz=14049387.1528125835.2.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; CURRENT_CITY_CODE=110000; hlwyfb_m_current_city_code=110000; curUrl=other; is_duanz=0; is_duy=0; is_first=0; is_wc=0; is_whole=%20; room=%20; sArea=; sAreaThree=; sArea_line_code=; sAreas=; sKeywords=; sPrice=0; sSort=0; sSubway=; sSubway_line_code=; sSubways=; history=[{%22flag%22:%22%22%2C%22keywords%22:%22%E6%B8%85%E5%8D%8E%E4%B8%9C%E8%B7%AF%E8%A5%BF%E5%8F%A3%22}%2C{%22flag%22:%226%22%2C%22keywords%22:%22%E7%99%BE%E5%BA%A6%E5%A4%A7%E5%8E%A6%22%2C%22value%22:%22116.301396%2C40.050909%22}]; __utmt=1; PHPSESSID=6391kef3mbg5nf6rgpk3o0lfc7; gr_user_id=16fac581-3163-4d14-8653-6de85fa5fda4",
    "Connection": "keep-alive",
    "Accept": "application/json;version=6",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Mobile/15E148 Safari/604.1",
    "Accept-Language": "zh-cn",
    "Referer": "http://m.ziroom.com/BJ/search?flag=&keywords=%E6%B8%85%E5%8D%8E%E4%B8%9C%E8%B7%AF%E8%A5%BF%E5%8F%A3&value=&more=",
    "DNT": "1"
}

query_data = {
    "city_code": "110000",
    "page": "1",
    "type": "",
    "price": "1500,5000",
    "face": "",
    "rface": "",
    "hface": "",
    "feature": "",
    "around": "",
    "leasetype": "",
    "tag": "",
    "version": "",
    "area": "",
    "subway_code": "",
    "subway_station_code": "",
    "district_code": "",
    "bizcircle_code": "",
    "clng": "",
    "clat": "",
    "suggestion_type": "",
    "suggestion_value": "",
    "keywords": "",
    "sort": ""
}


def get_rooms(keywords, tag):
    """
    :param keywords: 地铁站
    :param tag:
    :return: [{}, {}]
    """
    query_data["keywords"] = keywords
    query_data["tag"] = str(tag)
    ans = []
    for i in range(1, 1000):
        query_data["page"] = i
        res = do_request("http://m.ziroom.com/v7/room/list.json", headers=headers, params=query_data)
        # printx(res.json())
        if not res or not res.json() or res.json()["error_code"] != 0 or len(res.json()["data"]["rooms"]) == 0:
            break

        ans += res.json()["data"]["rooms"]

    return ans


def filters(room):
    """
    :param room:
    :return: False 无效房源; True 有效房源
    """
    # 自如直租 & 已出租
    if room["status"] == 'ycz' and "转" not in room["type_text"]:
        print(room["type_text"])
        return False

    # 辣鸡自如，转租的时候全部标记为已出租（实际上应该分为 立即预订/已预订），单独请求一次
    if room["status"] == "ycz":
        tres = do_request("http://m.ziroom.com/v7/room/detail.json?city_code=110000&id=%s" % room["id"], headers=headers)
        if tres and tres.json()["data"]["turn"]["disabled_label"] == "已预定":
            return False

    # 楼层
    if int(room["floor"]) == 1:
        return False

    # 面积
    room["area"] = room["area"].replace("约", "")
    if float(room["area"]) < 7.5:
        return False

    # 价格
    if int(room["price"]) > 4000:
        return False

    subway_station_info = room["subway_station_info"]

    # 离15号线近
    if subway_station_info.find("15号线") < 0:
        return False

    # 离地铁站近
    mi = int(re.findall("站(\d+)米$", subway_station_info)[0])
    if mi > 1000:
        return False

    # 黑名单
    # if room["resblock_name"] not in ["半导体宿舍","文成杰作","学院路甲39号院",]:
    #     return False
    # if int(room["id"])==60173656:
    #     print room

    return True


def get_all_rooms():
    maps = {}
    rooms = []
    # rooms += get_rooms("清华东路西口", "")
    # rooms += get_rooms("五道口", "")
    # rooms += get_rooms("六道口", "")
    rooms += get_rooms("望京南", "")

    for room in rooms:
        maps[room["id"]] = room

    printx(maps)

    print("all count:", len(maps))
    print("filter ans:")

    for id, room in maps.items():
        if filters(room):
            print(room["name"] + "\t" + room["subway_station_info"] + "\t" + "http://www.ziroom.com/z/vr/%s.html" % id)


def main():
    """
    然鹅这个破接口取不到自如客转租的房子，只能用来监控装修配置中的房子
    1. 先获取小区列表
    2. 遍历小区，获取房源
    3. 遍历房源，进行过滤
    :return:
    """
    # 获取小区列表
    res = do_request("http://www.ziroom.com/map/room/count?min_lng=116.325195&max_lng=116.36269&min_lat=39.992719&max_lat=40.01583&clng=116.347442&clat=40.007402&zoom=16", headers=headers)
    if not res:
        print("Count found list")
        return

    # 从 www 接口，取 退租配置中 的房子
    room_dict = {}
    for village in res.json()["data"]:
        print("[Searching] %s" % village["name"])
        vill_res = do_request(
            "http://www.ziroom.com/map/room/list?min_lng=116.325195&max_lng=116.36269&min_lat=39.992719&max_lat=40.01583&clng=116.347442&clat=40.007402&zoom=17&p=1&resblock_id=%s" % village["code"],
            headers=headers)

        if not vill_res or len(vill_res.json()["data"]["rooms"]) == 0:
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

        print(_id, room["room_status"], price, room["usage_area"], room["room_name"], "http://" + room["url"])

    # 从 m 接口，取 转租 的房子
    mroom_dict = {}
    for village in res.json()["data"]:
        print("[Searching] %s" % village["name"])
        res = do_request("http://m.ziroom.com/v7/room/list.json?city_code=110000&page=1&type=1&price=&face=&rface=&hface=&feature=&around=&leasetype=&tag=&version=&area=&subway_code=&subway_station_code=&district_code=&bizcircle_code=&clng=&clat=&suggestion_type=4&suggestion_value=%s&keywords=%s&sort=" % (village["name"], village["name"]), headers=headers)

        for i in res.json()["data"]["rooms"]:
            mroom_dict[i["id"]] = i

    # print(mroom_dict)
    # print(len(mroom_dict))

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

        print(_id, mroom["price"], mroom["area"], mroom["name"])



if __name__ == '__main__':
    main()
    # get_all_rooms()
    # rooms, page = get_rooms("清华东路西口", "")
# print re.findall("站(\d+)米$", "距15号线六道口站1416米")
