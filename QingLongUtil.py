#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import platform
import time
import urllib.parse
from json import dumps as jsonDumps

import requests

import ParseSettings
import RequestUtil
import notify

address = ParseSettings.address
address_local = ParseSettings.address_local
client_id = ParseSettings.client_id
client_secret = ParseSettings.client_secret

wxPusherAppToken = ParseSettings.wxPusherAppToken
wxPusherUuid = ParseSettings.wxPusherUuid


class QL:
    def __init__(self, isCloud=True) -> None:
        """
        初始化
        """
        self.auth = None
        if isCloud:
            self.address = address
        else:
            self.address = address_local
        self.id = client_id
        self.secret = client_secret
        self.valid = True
        self.login()

    def log(self, content: str) -> None:
        """
        日志
        """
        print(content)

    def login(self) -> None:
        """
        登录
        """
        url = f"{self.address}/open/auth/token?client_id={self.id}&client_secret={self.secret}"
        try:
            rjson = requests.get(url).json()
            if rjson['code'] == 200:
                self.auth = f"{rjson['data']['token_type']} {rjson['data']['token']}"
            else:
                self.log(f"登录失败：{rjson['message']}")
        except Exception as e:
            self.valid = False
            self.log(f"登录失败：{str(e)}")

    def getEnvs(self, searchValue='') -> list:
        """
        获取环境变量
        """
        url = f"{self.address}/open/envs?searchValue={searchValue}"
        headers = {"Authorization": self.auth}
        try:
            rjson = requests.get(url, headers=headers).json()
            if rjson['code'] == 200:
                return rjson['data']
            else:
                self.log(f"获取环境变量失败：{rjson['message']}")
        except Exception as e:
            self.log(f"获取环境变量失败：{str(e)}")

    def deleteEnvs(self, ids: list) -> bool:
        """
        删除环境变量
        """
        url = f"{self.address}/open/envs"
        headers = {"Authorization": self.auth, "content-type": "application/json"}
        try:
            rjson = requests.delete(url, headers=headers, data=jsonDumps(ids)).json()
            if rjson['code'] == 200:
                # self.log(f"删除环境变量成功：{len(ids)}")
                return True
            else:
                self.log(f"删除环境变量失败：{rjson['message']}")
                return False
        except Exception as e:
            self.log(f"删除环境变量失败：{str(e)}")
            return False

    def addEnvs(self, envs: list) -> bool:
        """
        新建环境变量
        """
        url = f"{self.address}/open/envs"
        headers = {"Authorization": self.auth, "content-type": "application/json"}
        try:
            rjson = RequestUtil.post(url, headers=headers, data=jsonDumps(envs)).json()
            if rjson['code'] == 200:
                self.log(f"新建环境变量成功：{len(envs)}")
                return True
            else:
                self.log(f"新建环境变量失败：{rjson['message']}")
                return False
        except Exception as e:
            self.log(f"新建环境变量失败：{str(e)}")
            return False

    def updateEnv(self, env: dict) -> bool:
        """
        更新环境变量
        """
        url = f"{self.address}/open/envs"
        headers = {"Authorization": self.auth, "content-type": "application/json"}
        try:
            rjson = requests.put(url, headers=headers, data=jsonDumps(env)).json()
            if rjson['code'] == 200:
                self.log(f"更新环境变量成功")
                return True
            else:
                self.log(f"更新环境变量失败：{rjson}")
                return False
        except Exception as e:
            self.log(f"更新环境变量失败：{str(e)}")
            return False

    def disabled(self, envs: list):
        """
        更新环境变量
        """
        url = f"{self.address}/open/envs/disable"
        headers = {"Authorization": self.auth, "content-type": "application/json"}
        try:
            rjson = requests.put(url, headers=headers, data=jsonDumps(envs)).json()
            # print(rjson)
            if rjson['code'] == 200:
                self.log(f"禁用环境变量成功")
                return True
            else:
                self.log(f"禁用环境变量失败：{rjson}")
                return False
        except Exception as e:
            self.log(f"禁用环境变量失败：{str(e)}")
            return False

    def getCrons(self, searchValue='') -> list:
        """
        获取定时任务
        """
        url = f"{self.address}/open/crons?searchValue={searchValue}"
        headers = {"Authorization": self.auth}
        try:
            rjson = requests.get(url, headers=headers).json()
            if rjson['code'] == 200:
                return rjson['data']['data']
            else:
                self.log(f"获取定时任务失败：{rjson['message']}")
        except Exception as e:
            self.log(f"获取定时任务失败：{str(e)}")

    def run(self, envId):
        """
        调起定时任务
        """
        url = f"{self.address}/open/crons/run"
        headers = {
            "Authorization": self.auth,
            "Content-Type": "application/json;charset=UTF-8"
        }
        payload = [envId]
        try:
            rjson = requests.put(url, headers=headers, data=f'{payload}').json()
            if rjson['code'] == 200:
                self.log(f"定时任务调起成功")
            else:
                self.log(f"定时任务调起失败：{rjson['message']}")
        except Exception as e:
            self.log(f"定时任务调起失败：{str(e)}")


def runOne(cronName, isCloud=True):
    ql = QL(isCloud)
    crons = ql.getCrons(cronName)
    if crons:
        cron = crons[0]
        ql.run(cron['id'])


def selectAllEnv(isCloud=True):
    ql = QL(isCloud)
    ql_result = ql.getEnvs()
    return ql_result


def selectOneEnv(cookie_name: str, env_value: str = '', isCloud=True):
    ql = QL(isCloud)
    ql_result = ql.getEnvs(env_value)
    if len(ql_result) >= 1:
        for ql_ in ql_result:
            ql_name = ql_['name']
            if cookie_name == ql_name:
                return ql_
    return None


def selectEnvByEnvName(cookie_name: str, isCloud=True):
    ql = QL(isCloud)
    ql_result = ql.getEnvs(cookie_name)
    return ql_result


def update(env: dict, isCloud=True):
    ql = QL(isCloud)
    newEnv = {
        "id": env['id'],
        "value": env['value'],
        "name": env['name'],
        "remarks": env['remarks']
    }
    ql.updateEnv(newEnv)


def add(cookie_name, env):
    ql = QL()
    envs = [{"value": json.dumps(env), "name": cookie_name}]
    ql.addEnvs(envs)


def updateQL(COOKIE_ENV_NAME, remark, env):
    print("开始更新青龙配置")
    ql_env = selectOneEnv(COOKIE_ENV_NAME, remark)
    if not ql_env:
        add(COOKIE_ENV_NAME, env)
        print(f"用户[{remark}]-青龙面板环境变量新增成功！")
    else:
        ql_env['value'] = json.dumps(env)
        update(ql_env)
        print(f"用户[{remark}]-青龙面板环境变量更新成功！")


def disabled(cookie_name: str, env_value: str = '', isCloud=True, isNotify: bool = True):
    ql = QL(isCloud)
    if env_value == '':
        env_value = cookie_name
    ql_result = ql.getEnvs(env_value)
    env_id = -1
    if len(ql_result) > 0:
        if len(ql_result) > 1:
            for ql_ in ql_result:
                ql_name = ql_['name']
                if cookie_name == ql_name:
                    env_id = ql_['id']
                    env_remark = ql_['remarks'] if ql_['remarks'] != '' else "未知用户"
        else:
            env_id = ql_result[0]['id']
            env_remark = ql_result[0]['remarks'] if ql_result[0]['remarks'] != '' else "未知用户"
        if env_id == -1:
            print(f"未发现变量名称-[{cookie_name}]，变量值-[{env_value}]的环境变量，无法禁用！")
            return
        isDisabled = ql.disabled([env_id])
        if isNotify:
            if isDisabled:
                notify.send("环境变量禁用提醒-[已禁用]",
                            f"变量名称：{cookie_name}\n"
                            f"变量内容：{env_value}\n"
                            f"变量备注：{env_remark}\n"
                            f"请及时更新Cookie~")
            else:
                notify.send("环境变量禁用提醒-[未禁用]",
                            f"变量名称：{cookie_name}\n"
                            f"变量内容：{env_value}\n"
                            f"变量备注：{env_remark}\n"
                            f"请及时更新Cookie~")
        time.sleep(2)


def deleteCookieByContent(COOKIE_ENV_NAME, remark):
    ql = QL()
    ql_env = selectOneEnv(COOKIE_ENV_NAME, remark)
    if not ql_env:
        print(f"未发现指定Cookie")
    else:
        env_id = ql_env['id']
        ql.deleteEnvs([f'{env_id}'])


def deleteCookie(isCloud=True):
    ql = QL(isCloud)
    ql_result = ql.getEnvs()
    for env in ql_result:
        status = env['status']
        env_id = env['id']
        if status == 1:
            print(env)
            ql.deleteEnvs([f'{env_id}'])


def wxPusher(uuid, title, content):
    if uuid:
        send_msg = f'{title}\n{content}'
        url_encode_msg = urllib.parse.quote_plus(send_msg)
        url = f"https://wxpusher.zjiecode.com/demo/send/custom/{uuid}?content={url_encode_msg}"
        requests.request("GET", url)
    else:
        print("未配置微信推送id，过期提醒推送失败！")


def readFile(name):
    current_path = os.path.abspath(__file__)
    # 获取当前文件所在目录的路径
    folder_path = os.path.dirname(current_path)
    # 列出文件夹中的所有文件
    file_list = os.listdir(folder_path)
    json_files = [file for file in file_list if file.endswith(name)]
    if len(json_files) == 0:
        print("未发现指定的json文件")
        return None
    # 输出 JSON 文件列表
    # print(f'读取到文件：{json_files}')
    if len(json_files) >= 1:
        file_name = json_files[0]
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    return None


def writeFile(file_name, data):
    current_path = os.path.abspath(__file__)
    # 获取当前文件所在目录的路径
    folder_path = os.path.dirname(current_path)
    # 列出文件夹中的所有文件
    file_list = os.listdir(folder_path)

    with open(file_name, 'a', encoding='utf-8') as f:
        f.seek(0)
        f.truncate()
        f.writelines(json.dumps(data))


def ts_qb(title, data):
    # WxPusher API地址
    api_url = 'https://wxpusher.zjiecode.com/api/send/message'

    # 按照序号字段对数据进行排序
    sorted_data = sorted(data, key=lambda x: x['序号'])

    # 构造要推送的表格内容
    table_content = ''
    for row in sorted_data:
        table_content += f"<tr><td style='border: 1px solid #ccc; padding: 6px;'>{row['序号']}</td><td style='border: 1px solid #ccc; padding: 6px;'>{row['用户']}</td><td style='border: 1px solid #ccc; padding: 6px;'>{row['今日积分']}</td><td style='border: 1px solid #ccc; padding: 6px;'>{row['总积分']}</td><td style='border: 1px solid #ccc; padding: 6px;'>{row['备注']}</td></tr>"

    table_html = f"<table style='border-collapse: collapse;'><tr style='background-color: #f2f2f2;'><th style='border: 1px solid #ccc; padding: 8px;'>🆔</th><th style='border: 1px solid #ccc; padding: 8px;'>用户</th><th style='border: 1px solid #ccc; padding: 8px;'>今日积分</th><th style='border: 1px solid #ccc; padding: 8px;'>总共积分</th><th style='border: 1px solid #ccc; padding: 8px;'>备注</th></tr>{table_content}</table>"

    # 构造请求参数
    params = {
        "appToken": wxPusherAppToken,
        'content': table_html,
        'contentType': 3,  # 表格类型
        'topicIds': [],  # 接收消息的用户ID列表，为空表示发送给所有用户
        "summary": title,
        "uids": [wxPusherUuid],
    }

    # 发送POST请求
    response = requests.post(api_url, json=params)

    # 检查API响应
    if response.status_code == 200:
        result = response.json()
        if result['code'] == 1000:
            print('🎉管理员汇总推送成功')
        else:
            print(f'💔管理员汇总推送失败，错误信息：{result["msg"]}')
    else:
        print('⛔️管理员汇总推送请求失败')


def isLocal():
    system_name = platform.system()
    if system_name == "Windows":
        return  True
    else:
        return False
# if __name__ == "__main__":
#     wxPusher("UID_pQ6VwWBCxoOGka0hS5f2JlqXPzUC", "全棉时代账号已过期", "222")
#     ql = QL(address, client_id, client_secret)
#     ql_result = ql.getEnvs('musi')
#     for env in ql_result:
#         print(env)
#         envId = env['id']
# ql.run(envId)
# sys.exit()
#     status = env['status']
#     id = env['id']
#     if status == 1:
#         print(env)
#         ql.deleteEnvs([f'{id}'])
