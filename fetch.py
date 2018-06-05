# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import re
import requests

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


def query(data):
    req = requests.get("http://m.ziroom.com/v7/room/list.json", headers=headers, params=data)
    res = json.loads(req.text)
    # print req.text
    if res["error_code"] == 0:
        rooms = res["data"]["rooms"]
        return rooms
    else:
        print "Error!"
        return []


def get_rooms(keywords, tag):
    query_data["keywords"] = keywords
    query_data["tag"] = str(tag)
    ans = []
    for i in xrange(1, 1000):
        query_data["page"] = i
        rooms = query(query_data)
        if len(rooms) == 0:
            break
        ans += rooms
    return ans


def filters(room):
    # 已出租、配置中
    if room["status"] == 'ycz' or 'pzz' in room["status"]:
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
    rooms = get_rooms("清华东路西口", "")
    rooms += get_rooms("五道口", "")

    for room in rooms:
        maps[room["id"]] = room

    print "all count:", len(maps)
    print "filter ans:"
    for id, room in maps.iteritems():
        if filters(room):
            print room["name"] + "\t" + room["subway_station_info"] + "\t" + "http://www.ziroom.com/z/vr/%s.html" % id


if __name__ == '__main__':
    get_all_rooms()
# print re.findall("站(\d+)米$", "距15号线六道口站1416米")
