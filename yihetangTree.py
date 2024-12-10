# -*- coding:utf-8 -*-
"""
const $ = new Env("益禾堂种树");
cron: 0 30 10 * * *
desc: 益禾堂种树活动
变量名：YHT_COOKIE
变量值：{"token":"sfbEseVCN7X9pvN43NRgH5RLK8XTzzQRXlS-bv","mobile":"手机号","appId":"wx4080846d0cec2fd5","userId":"1032867597"}
appId不要变
"""
import json
import random
import time
from configparser import ConfigParser

import requests

import CookieUtil
import RequestUtil
import notify

# 创建解析器对象
config = ConfigParser()

# 读取配置文件
config.read('settings.ini', 'utf-8')

userMap = {}


class QM:

    def __init__(self, env, num):
        self.appId = json.loads(env)['appId']
        try:
            target = config.get('quanmai_tree', self.appId)
        except:
            return
        if not target or len(target.split("|")) < 2:
            return
        self.userId = json.loads(env)['userId']
        self.targetName = target.split("|")[0]
        self.activityId = target.split("|")[1]
        self.token = json.loads(env)['token']
        self.remark = json.loads(env)['mobile']
        self.num = num
        self.headers = {
            'content-type': 'application/json',
            'Connection': 'keep-alive',
            # 'Accept-Encoding': 'gzip,compress,br,deflate',
            'Qm-From': 'wechat',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.43(0x18002b2c) NetType/WIFI Language/zh_CN',
            'Qm-User-Token': self.token,
            'Host': 'webapi.qmai.cn',
            'Qm-From-Type': 'catering',
            'Referer': 'https://servicewechat.com/wxafec6f8422cb357b/115/page-frame.html',
            'Accept': 'v=1.0'
        }

    def activityInfo(self):
        global msg
        url = 'https://webapi.qmai.cn/web/cmk-center/nurture/activityInfo'
        payload = {"activityId": self.activityId, "appid": self.appId}
        response = RequestUtil.post(url=url, headers=self.headers, json=payload)
        res = response.json()
        if int(res['code']) == 0:
            nurtureStageVo = res['data']['nurtureStageVo']
            upgradeThreshold = nurtureStageVo['upgradeThreshold']
            nutrientUsed = nurtureStageVo['nutrientUsed']
            level = nurtureStageVo['level']
            print(
                f"账号[{self.num}][{self.remark}] [{self.targetName}]当前等级：{level}级，树进度:{nutrientUsed}/{upgradeThreshold}")
            msg += f"账号[{self.num}][{self.remark}] [{self.targetName}]当前等级：{level}级，种树进度:{nutrientUsed}/{upgradeThreshold}\n"
            if level == 3:
                print(f"账号[{self.num}][{self.remark}] [{self.targetName}]果树已成熟")
                self.sendReward()
        else:
            print(f"账号[{self.num}][{self.remark}] [{self.targetName}]种树进度异常:{res['message']}")

    def stageInfo(self):
        url = 'https://webapi.qmai.cn/web/cmk-center/nurture/stageInfo'
        payload = {"activityId": self.activityId, "appid": self.appId}
        response = RequestUtil.post(url, headers=self.headers, json=payload)
        res = response.json()
        if int(res['code']) == 0:
            data = res['data']
            level = data['level']
            nutrientRemaining = data['nutrientRemaining']
            nutrientUsed = data['nutrientUsed']
            print(
                f"账号[{self.num}][{self.remark}] [{self.targetName}]种树进度:{level}级，已使用营养液：{nutrientUsed}，剩余营养液：{nutrientRemaining}")
            return nutrientRemaining
        else:
            print(f"账号[{self.num}][{self.remark}] [{self.targetName}]获取种树进度异常:{res['message']}")
            return False

    def add(self):
        url = 'https://webapi.qmai.cn/web/cmk-center/nurture/add/nutrient'
        payload = {"activityId": self.activityId, "appid": self.appId}
        response = RequestUtil.post(url, headers=self.headers, json=payload)
        res = response.json()
        if int(res['code']) == 0:
            print(f"账号[{self.num}][{self.remark}] [{self.targetName}]施肥成功")
            return True
        else:
            print(f"账号[{self.num}][{self.remark}] [{self.targetName}]施肥异常:{res['message']}")
            return False

    def use(self):
        nutrientRemaining = self.stageInfo()
        if nutrientRemaining:
            for i in range(0, int(nutrientRemaining)):
                self.add()
                time.sleep(random.randint(1, 4))
        self.activityInfo()
        self.coupon_list()

    def userHelp(self):
        for userId, v in userMap.items():
            if userId == self.userId:
                continue
            if userMap[userId]['dailyInviteNum'] >= 3:
                continue
            url = 'https://webapi.qmai.cn/web/cmk-center/task/userHelp'
            payload = {
                "activityId": self.activityId,
                "inviteUserId": userId,
                "appid": self.appId
            }
            response = RequestUtil.post(url, headers=self.headers, json=payload)
            res = response.json()
            if int(res['code']) == 0:
                print(f"账号[{self.num}][{self.remark}] [{self.targetName}]助力成功")
                userMap[userId]['dailyInviteNum'] += 1
            else:
                print(f"账号[{self.num}][{self.remark}] [{self.targetName}]助力异常:{res['message']}")
                if '今日助力次数已达上限':
                    break

    def taskInfo(self):
        url = 'https://webapi.qmai.cn/web/cmk-center/task/taskInfo'
        payload = {
            "activityId": self.activityId,
            "appid": self.appId
        }
        response = RequestUtil.post(url, headers=self.headers, json=payload)
        res = response.json()
        if int(res['code']) == 0:
            dailyInviteNum = res['data']['dailyInviteNum']
            dailyConsumeNum = res['data']['dailyConsumeNum']
            print(
                f"账号[{self.num}][{self.remark}] [{self.targetName}]本日邀请次数：{dailyInviteNum}，本日助力次数：{dailyConsumeNum}")
            if dailyInviteNum == 3:
                return
            userMap[self.userId] = {
                'dailyInviteNum': dailyInviteNum,
                'dailyConsumeNum': dailyConsumeNum
            }
        else:
            print(f"账号[{self.num}][{self.remark}] [{self.targetName}]助力异常:{res['message']}")

    def takePartInNurture(self):
        url = 'https://webapi.qmai.cn/web/cmk-center/nurture/takePartInNurture'
        payload = {
            "activityId": self.activityId,
            "appid": self.appId
        }
        response = RequestUtil.post(url, headers=self.headers, json=payload)
        res = response.json()
        if int(res['code']) == 0:
            print(
                f"账号[{self.num}][{self.remark}] [{self.targetName}]开启种树成功")
        else:
            print(f"账号[{self.num}][{self.remark}] [{self.targetName}]开启种树异常:{res['message']}")

    def giveAmount(self):
        url = 'https://webapi.qmai.cn/web/cmk-center/nurture/giveAmount'
        payload = {
            "activityId": self.activityId,
            "appid": self.appId
        }
        response = RequestUtil.post(url, headers=self.headers, json=payload)
        res = response.json()
        if int(res['code']) == 0:
            print(
                f"账号[{self.num}][{self.remark}] [{self.targetName}]领取每日奖励成功")
        else:
            print(f"账号[{self.num}][{self.remark}] [{self.targetName}]领取每日奖励异常:{res['message']}")

    def sendReward(self):
        global msg
        url = 'https://webapi.qmai.cn/web/cmk-center/nurture/sendReward'
        payload = {
            "activityId": self.activityId,
            "appid": self.appId
        }
        response = requests.post(url, headers=self.headers, json=payload)
        res = response.json()
        if int(res['code']) == 0:
            print(
                f"账号[{self.num}][{self.remark}] [{self.targetName}]领取奖励成功，获得[{res['data'][0]['rewardName']}]")
            msg += f"账号[{self.num}][{self.remark}] [{self.targetName}]领取奖励成功，获得[{res['data'][0]['rewardName']}]\n"
        else:
            print(f"账号[{self.num}][{self.remark}] [{self.targetName}]领取奖励异常:{res['message']}")

    def coupon_list(self):
        global msg2
        url = 'https://webapi2.qmai.cn/web/catering2-apiserver/crm/coupon/list'
        payload = {"pageNo": 1, "pageSize": 1000, "useStatus": 0, "appid": self.appId}
        response = requests.post(url, headers=self.headers, json=payload)
        res = response.json()
        if int(res['code']) == 0:
            data = res['data']['data']
            for d in data:
                title = d['title']
                expire = d['endAt']
                if '种' in title:
                    print(f"账号[{self.num}][{self.remark}] [{self.targetName}]{title}-{expire}")
                    msg2 += f"账号[{self.num}][{self.remark}] [{self.targetName}]{title}-{expire}\n"


if __name__ == '__main__':
    msg = ''
    msg2 = ''
    cookies = CookieUtil.get_cookies("YHT_COOKIE")
    for num, cookie in enumerate(cookies):
        num += 1
        QM(cookie, num).takePartInNurture()
        QM(cookie, num).giveAmount()
        QM(cookie, num).taskInfo()
        time.sleep(random.randint(2, 5))

    for num, cookie in enumerate(cookies):
        num += 1
        QM(cookie, num).userHelp()
        time.sleep(random.randint(2, 5))

    for num, cookie in enumerate(cookies):
        num += 1
        QM(cookie, num).use()
        time.sleep(random.randint(2, 5))

    if msg:
        notify.send("益禾堂果树进度", msg)

    if msg2:
        notify.send("益禾堂优惠券", msg2)
