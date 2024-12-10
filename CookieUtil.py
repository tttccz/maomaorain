#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 获取系统变量值
import json
import os
import time
from functools import partial

import DateUtil
import EncryptUtil
import QingLongUtil

print = partial(print, flush=True)


def format_cookies(cookies, split_symbol):
    cookies_result = []
    for cookie in cookies:
        if split_symbol in cookie:
            for ck in cookie.split(split_symbol):
                cookies_result.append(ck)
        elif '&' in cookie:
            for ck in cookie.split('&'):
                cookies_result.append(ck)
        else:
            cookies_result.append(cookie)
    return cookies_result


def get_cookies(param_name, isCloud=False, split_symbol="\n", isFormat=True):
    Cookies = []
    isCloud = QingLongUtil.isLocal()
    if os.environ.get(param_name) and isFormat:
        print(f"{'=' * 6}已获取并使用Env环境 Cookie{'=' * 6}")
        if '\n' in os.environ[param_name]:
            Cookies = os.environ[param_name].split('\n')
        elif '&' in os.environ[param_name]:
            Cookies = os.environ[param_name].split('&')
        else:
            Cookies = [os.environ[param_name]]
        # return Cookies
    else:
        if isCloud:
            print(f"本地未获取到可运行CK，尝试远端获取，当前青龙面板地址：{QingLongUtil.address}")
        else:
            print(f"本地未获取到可运行CK，尝试远端获取，当前青龙面板地址：{QingLongUtil.address_local}")
        envs = QingLongUtil.selectEnvByEnvName(param_name, isCloud)
        if envs is None:
            print(f"远端青龙环境连接异常！")
            exit(0)
        if len(envs) == 0:
            print(f"未获取合适环境变量！")
            exit(0)
        for env in envs:
            if env['status'] != 1:
                Cookies.append(env['value'])

    print(
        f"{'=' * 6}脚本执行- 北京时间(UTC+8)：{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())}{'=' * 6}\n")
    if isFormat:
        Cookies = format_cookies(Cookies, split_symbol)
    print(f"{'=' * 6} 共发现{len(Cookies)}个账号Cookie {'=' * 6}")
    return Cookies


def decryptJwtInfo(cookie, num, remark):
    msg = ''
    if cookie.startswith("eyJ"):
        targetCookiePart = ""
        cookieArr = cookie.split(".")
        if len(cookieArr) == 1:
            targetCookiePart = cookieArr[0]
        if len(cookieArr) >= 3:
            targetCookiePart = cookieArr[1]
        if targetCookiePart:
            targetCookiePart = targetCookiePart + "=="
            try:
                decryptJwt = EncryptUtil.base64Decode(targetCookiePart)
                # print(decryptJwt)
                decryptJwt2 = decryptJwt[decryptJwt.find("{"): decryptJwt.rfind("}") + 1]
                decryptJwtJson = json.loads(decryptJwt2)
                print(decryptJwtJson)
                info = ""
                if 'exp' in decryptJwtJson.keys():
                    info = f"账号[{num}][{remark}] 预计过期时间为 [{DateUtil.timestamp_to_date_str(decryptJwtJson['exp'])}]\n"
                if 'expiredat' in decryptJwtJson.keys():
                    try:
                        info = f"账号[{num}][{remark}] 预计过期时间为 [{DateUtil.timestamp_to_date_str(decryptJwtJson['expiredat'])}]\n"
                    except:
                        info = f"账号[{num}][{remark}] 预计过期时间为 [{decryptJwtJson['expiredat']}]\n"
                msg += info
            except Exception as e:
                print(e)
                return None
    print(msg)
    return msg

if __name__ == '__main__':
    msg = ''
    decryptJwtInfo(
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJwZXJtaXNzaW9ucyI6WyJzZWxmIl0sImlzcyI6ImF1dGgwIiwiaWQiOiIxMTE5NzAzNiIsIm9wZXJhdGlvblNvdXJjZSI6IkZUTVNfRU5KT1kiLCJleHAiOjE3MzQwMTE1NzQsIm9wZXJhdG9yTmFtZSI6InVzZXIiLCJub25jZSI6ImNkMDMyMzRhYjk4NDQ1ZDk5NmVmMDlkOWI3MjIxODgwIiwiaXNPcGVyYXRvciI6ZmFsc2V9.SfvucNtrGFFYlucnupyOWgPHs2k8GxcJJcaArFVIhHF9plrZLtYoyiU6faRGk3TltmXjSE3TNOdGLeaMhgDTLQ"
        , "test", 1)
    print(msg)
