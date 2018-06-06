import requests
import cchardet
import simplejson


def printx(data):
    print(simplejson.dumps(data, indent=4))


def do_request(url, method="GET", data="", headers=None, allow_redirects=True, timeout=15, params=None):
    """
    如果请求成功，返回requests.response对象，否则返回None
    :return:
    """
    if method.lower() == "post":
        if headers:
            headers["content-type"] = "application/x-www-form-urlencoded"
        else:
            headers = {"content-type": "application/x-www-form-urlencoded"}

    try:
        response = requests.request(method=method, url=url, headers=headers, data=data, timeout=(timeout, timeout),
                                    verify=False, allow_redirects=allow_redirects, params=params)
        response.encoding = cchardet.detect(response.content)['encoding']           # 修正编码
        return response
    except Exception as e:
        print(e)
        return