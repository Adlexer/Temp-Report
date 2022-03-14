import urllib.error
from urllib import request
import json
import time
import requests


def get_local_date() -> str:
    time_stamp = int(time.time())
    time_array = time.localtime(time_stamp)
    return time.strftime("%Y-%m-%d", time_array)


def get_local_date_and_time() -> str:
    time_stamp = int(time.time())
    time_array = time.localtime(time_stamp)
    return time.strftime("[%Y-%m-%d %H:%M:%S]", time_array)


def wx_login(open_id="54b748176155d8bf71e384f30a36244f") -> str:
    try:
        # GET request
        req = requests.get(url="http://fanxiao.ujn.edu.cn:80/wxUser/wxLoginByOpenId?openId=" + open_id)
    except requests.exceptions:
        return ""
    print(get_local_date_and_time() + " get cookies: " + req.cookies.values()[0] + " by open id: " + open_id)
    return req.cookies.values()[0]


def health_report() -> int:
    print(get_local_date_and_time() + " waiting wx login...")
    # use local user id
    cookies = wx_login("e89ed52de0f2563d4ec35510029189fc")
    if cookies == "":
        print(get_local_date_and_time() + " get cookies failed")
        return 0

    date_string = get_local_date()
    print(get_local_date_and_time() + " sending request...")

    request_data = "reportTime=" + date_string + "&isOut=2&address=&travelMode=&temperatureAm=36.5&temperaturePm=36.5&reserveOne=36.5"
    request_header = {
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": "sid=" + cookies
    }
    try:
        # POST request
        req = request.Request(url="http://fanxiao.ujn.edu.cn:80/temperatureRecord/createTemperatureRecordCopy",
                              headers=request_header,
                              data=request_data.encode("utf-8"))
    except urllib.error:
        print(get_local_date_and_time() + " error request, trying to resend...")
        return 0

    reps = json.loads(request.urlopen(req).read().decode("utf-8"))
    print(get_local_date_and_time() + " get message: " + reps["msg"])
    if reps["status"] == 1:
        return 1
    else:
        if reps["status"] == 0:
            return 1
        else:
            return 0


def main():
    print(get_local_date_and_time() + " program start")
    # params
    report_hour = 18
    check_out_minutes = 1
    time_out_minutes = 5
    time_out_count = 3

    while True:
        time_stamp = int(time.time())
        time_array = time.localtime(time_stamp)
        hour = int(time.strftime("%H", time_array))
        print(get_local_date_and_time() + " checking hour...")
        if hour == report_hour:
            print(get_local_date_and_time() + " report hour reached")
            ret = health_report()
            if ret == 0:
                # failure count
                cnt = 0
                while True:
                    time.sleep(time_out_minutes * 60)
                    ret = health_report()
                    if ret == 0:
                        cnt = cnt + 1
                    else:
                        break

                    if cnt >= time_out_count:
                        print(get_local_date_and_time() + " trying too many times")
                        break
            time.sleep(3600)
        else:
            print(get_local_date_and_time() + " ignored")
            time.sleep(check_out_minutes * 60)


if __name__ == "__main__":
    main()
