import time
import requests
import cchardet
import simplejson

import smtplib
from email.mime.text import MIMEText
from conf import mail_conf




def printx(data):
    tres = simplejson.dumps(data, indent=4)
    print(tres)

    return tres


def do_request(url, method="GET", data="", headers=None, allow_redirects=True, timeout=15, params=None):
    """
    如果请求成功，返回requests.response对象，否则返回None
    :return:
    """
    # 控制下速度
    time.sleep(0.5)
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


def write_file(filename, data):
    if isinstance(data, list) or isinstance(data, dict):
        data = simplejson.dumps(data, indent=4)

    ff = open(filename, "w")
    ff.write(data)
    ff.close()

    return 1


def read_file(filename):
    try:
        ff = open(filename, "r")
        content = ff.read()
        ff.close()

        return simplejson.loads(content)
    except:
        return []


def send_mail(to_mail, title, content):

    from_mail = mail_conf['mail_address']
    server = mail_conf['smtp_server']

    smtp = smtplib.SMTP_SSL()
    smtp.connect(server)
    smtp.ehlo(server)
    smtp.login(mail_conf['username'], mail_conf['password'])

    for mail in to_mail.split(','):
        msg = MIMEText(content, "html", 'utf-8')
        msg['To'] = to_mail
        msg['From'] = from_mail
        msg['Subject'] = title

        smtp.sendmail(from_mail, mail, msg.as_string())
        print('Send To: %s' % mail)

    smtp.quit()
