import hashlib
import os
import re
import time

import requests

import DateUtil

# 1启用 2不启用
use_proxy = os.environ.get("use_proxy") if os.environ.get("use_proxy") else "1"

# 星空代理参数 sign:apiKey;sign:apiKey 多账号\n分割
proxy_xingkong_userInfo = os.environ.get("proxy_xingkong_userInfo") if os.environ.get(
    "proxy_xingkong_userInfo") else "e80b74xxxxxxxxe7b98835d725:XK2BEF1xxxxxxxA3D62"

# 巨量代理参数 user_id:用户apiKey:接口apiKey;user_id:apiKey:授权Base64 多账号\n分割
proxy_juliang_userInfo = os.environ.get("proxy_juliang_userInfo") if os.environ.get(
    "proxy_juliang_userInfo") else "1xxxxx7:771dxxxxf0:48df69426e6d4804:xxxxxTU6ZTMydWN0ODIKIA=="

## 携趣代理参数 uid:ukey:apiUrl
proxy_xiequ_userInfo = os.environ.get("proxy_xiequ_userInfo") if os.environ.get(
    "proxy_xiequ_userInfo") else "115XXXX|CA304DE6xxxx6607A9A|http://api.xiequ.cn/VAD/GetIp.aspx?act=get&uid=114563&vkey=7062BAA71&num=1&time=30&plat=0&re=0&type=0&so=1&ow=1&spl=1&addr=&db=1"


def get_proxy_pool(num=1):
    """
    获取代理池 num 代理数量
    提取顺序
    -> 1.携趣代理
    -> 2.巨量代理
    -> 3.星空代理
    """
    auth = None
    proxy_ip_pool_list = get_xiequ_proxy_pool(proxy_xiequ_userInfo, num)
    if proxy_ip_pool_list is not None and len(proxy_ip_pool_list) > 0:
        proxy_type_ = 'xk'
    else:
        proxy_ip_pool_list, auth = get_juliang_proxy_pool(proxy_juliang_userInfo, num)
        if proxy_ip_pool_list is not None and len(proxy_ip_pool_list) > 0:
            proxy_type_ = 'jl'
        else:
            # if xkFlag == "True":
            proxy_ip_pool_list = get_xingkong_proxy_ip_pool(proxy_xingkong_userInfo, num)
            proxy_type_ = 'xk'
    result = []
    for proxy_ip in proxy_ip_pool_list:
        result.append({
            "proxy_ip": proxy_ip,
            "proxy_type": proxy_type_,
            "auth": auth
        })
    return result


def get_proxy_pool_by_type(type, num=1):
    """
    获取代理池 num 代理数量
    """
    auth = None
    proxy_ip_pool_list = []
    proxy_type_ = None
    if type == 'xq':
        proxy_ip_pool_list = get_xiequ_proxy_pool(proxy_xiequ_userInfo, num)
        proxy_type_ = 'xk'
    if type == 'jl':
        proxy_ip_pool_list, auth = get_juliang_proxy_pool(proxy_juliang_userInfo, num)
        proxy_type_ = 'jl'
    if type == 'xk':
        proxy_ip_pool_list = get_xingkong_proxy_ip_pool(proxy_xingkong_userInfo, num)
        proxy_type_ = 'xk'
    result = []
    if len(proxy_ip_pool_list) == 0:
        return []
    for proxy_ip in proxy_ip_pool_list:
        result.append({
            "proxy_ip": proxy_ip,
            "proxy_type": proxy_type_,
            "auth": auth
        })
    return result

def processException(e, businessDesc=''):
    if '502' in str(e):
        # print('代理异常：502 代理连接失败，' + businessDesc)
        return 1
    elif '407' in str(e):
        # print('代理异常：407 授权失败，' + businessDesc)
        return 2
    elif '429' in str(e):
        # print('代理异常：429 当前代理请求过多，' + businessDesc)
        return 2
    elif 'timeout' in str(e) or 'timed out' in str(e):
        # print('连接超时，' + businessDesc)
        return 1
    else:
        # print(e)
        return 3


def get_my_ip():
    while True:
        try:
            text = requests.get("http://ip111.cn/", timeout=20).text
            result = re.search("((?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d]))", text)
            current_ip = result.groups()[0]
            # print(f'本地IP：{current_ip}')
            return current_ip
        except Exception as e:
            if 'timeout' in str(e):
                print('http://ip111.cn/ 响应超时！')


def get_my_ip_by_proxy(proxies=None, auth=None, proxy_type='jl'):
    try:
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Host": "ip111.cn",
            "Proxy-Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36 Edg/108.0.1462.54"
        }
        if proxy_type == 'jl':
            headers['Proxy-Authorization'] = f'Basic {auth}'
        text = requests.get("http://ip111.cn/", headers=headers, proxies=proxies, timeout=30).text
        result = re.search("((?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d]))", text)
        current_ip = result.groups()[0]
        # print(f'代理IP：{current_ip}')
        return current_ip
    except Exception as e:
        if 'timeout' in str(e):
            raise MyError('timeout')
        else:
            raise


def testProxy(proxy, proxy_type, auth=None):
    """
    测试代理可用性 proxy代理地址 ip:port proxy_type代理类型 目前支持巨量(jl) 星空(xk), auth 巨量代理需要的授权header
    """
    try:
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Host": "baidu.com",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36 Edg/108.0.1462.54"
        }
        if proxy_type == 'jl':
            headers['Proxy-Authorization'] = f'Basic {auth}'
        resp = requests.get("http://www.baidu.com", proxies={"http": f"http://{proxy}", "https": f"https://{proxy}"},
                            timeout=20)
        if resp.status_code == 200:
            return True
        else:
            return False
    except:
        return False


"""
##############################
        巨量代理相关方法
##############################
"""


def get_juliang_white_list(orderId, key):
    """
    获取巨量白名单，orderId 订单号, key：订单key
    """
    while True:
        try:
            text = f'trade_no={orderId}&key={key}'
            sign = hashlib.md5(text.encode(encoding='UTF-8')).hexdigest()

            resp = requests.get(
                f'http://v2.api.juliangip.com/dynamic/getwhiteip?trade_no={orderId}&sign={sign}', timeout=20)
            res = resp.json()
            if res["code"] == 200:
                print(f'当前巨量代理白名单为{res["data"]["current_white_ip"][0]}')
                return res["data"]["current_white_ip"][0]
            else:
                return None
        except Exception as e:
            if 'timeout' in str(e):
                print('获取巨量白名单响应超时！')


def replace_juliang_white_list(orderId, key):
    """
    替换巨量白名单，orderId 订单号, key：订单key
    """
    while True:
        try:
            old_ip = get_juliang_white_list(orderId, key)
            new_ip = get_my_ip()
            while old_ip != new_ip:
                # text = f'new_ip={new_ip}&old_ip={old_ip}&trade_no={orderId}&key={key}'
                text = f'new_ip={new_ip}&reset=1&trade_no={orderId}&key={key}'
                sign = hashlib.md5(text.encode(encoding='UTF-8')).hexdigest()
                resp = requests.get(
                    f'http://v2.api.juliangip.com/dynamic/replaceWhiteIp?new_ip={new_ip}&reset=1&trade_no={orderId}&sign={sign}',
                    timeout=20)
                res = resp.json()
                # print(res)
                if res["code"] == 200:
                    replaced_ip = get_juliang_white_list(orderId, key)
                    if replaced_ip == new_ip:
                        print('替换白名单成功！')
                        time.sleep(20)
                        break
                    else:
                        print('替换白名单失败！')
                        time.sleep(20)
                        continue
            break
        except Exception as e:
            if 'timeout' in str(e):
                print('替换巨量白名单响应超时！')


def get_juliang_proxy_orders(juliang_user_id='1009307', key='bacc7b441cde42578f50559f94136e34'):
    """
    获取巨量订单信息，juliang_user_id 巨量用户ID, key：巨量用户key
    """
    while True:
        try:
            text = f'product_type=1&user_id={juliang_user_id}&key={key}'
            sign = hashlib.md5(text.encode(encoding='UTF-8')).hexdigest()

            resp = requests.get(
                f'http://v2.api.juliangip.com/users/getAllOrders?product_type=1&user_id={juliang_user_id}&sign={sign}',
                timeout=20)
            res = resp.json()
            if res["code"] == 200:
                return res["data"]["OrderList"]
            else:
                return None
        except Exception as e:
            if 'timeout' in str(e):
                print('替换巨量白名单响应超时！')


def get_juliang_proxy_pool_one(orderId, apiKey, num=1):
    """
    获取巨量IP主方法，juliang_user_id 巨量用户ID, key：巨量用户key
    """
    while True:
        try:
            text = f'num={num}&pt=1&result_type=json&trade_no={orderId}&key={apiKey}'
            sign = hashlib.md5(text.encode(encoding='UTF-8')).hexdigest()
            resp = requests.get(
                f'http://v2.api.juliangip.com/dynamic/getips?num={num}&pt=1&result_type=json&trade_no={orderId}&sign={sign}',
                timeout=20)
            res = resp.json()
            if res["code"] == 200:
                print(f'[{DateUtil.get_today()}]获取巨量代理成功，当前账号剩余{res["data"]["surplus_quantity"]}个代理可提取')
                return res["data"]["proxy_list"]
            else:
                return None
        except Exception as e:
            if 'timeout' in str(e):
                print('替换巨量白名单响应超时！')


def get_juliang_proxy_pool(proxy_juliang_userInfo, num=1):
    """
    获取巨量IP池，proxy_juliang_userInfo 巨量用户信息 userId:userKey num 提取数量
    """
    proxy_pool = []
    if '\n' in proxy_juliang_userInfo:
        proxy_juliang_userInfos = proxy_juliang_userInfo.split("\n")
        k = 0
        for proxy_juliang_user in proxy_juliang_userInfos:
            user_id = proxy_juliang_user.split(":")[0]
            key = proxy_juliang_user.split(":")[1]
            orderList = get_juliang_proxy_orders(user_id, key)
            k += 1
            if orderList is None or len(orderList) == 0:
                continue
            orderId = orderList[0]
            print(f'巨量代理：获取第{k}个账号订单编号成功：{orderId}')
            apiKey = proxy_juliang_user.split(":")[2]
            auth = proxy_juliang_user.split(":")[3]
            replace_juliang_white_list(orderId, apiKey)
            while len(proxy_pool) < num:
                proxy = get_juliang_proxy_pool_one(orderId, apiKey, 1)
                if proxy is None or len(proxy) == 0:
                    print('当前账号代理套餐已用完')
                    break
                proxyStatus = testProxy(proxy[0], 'jl', auth)
                if proxyStatus:
                    proxy_pool.append(proxy[0])
                else:
                    print('当前代理失效，重新获取')
                time.sleep(10)
            if proxy_pool is not None and len(proxy_pool) >= num:
                return proxy_pool, auth
    else:
        user_id = proxy_juliang_userInfo.split(":")[0]
        key = proxy_juliang_userInfo.split(":")[1]
        orderList = get_juliang_proxy_orders(user_id, key)
        if orderList is not None and len(orderList) > 0:
            orderId = orderList[0]
            apiKey = proxy_juliang_userInfo.split(":")[2]
            auth = proxy_juliang_userInfo.split(":")[3]
            replace_juliang_white_list(orderId, apiKey)
            while len(proxy_pool) < num:
                proxy = get_juliang_proxy_pool_one(orderId, apiKey, 1)
                if proxy is None or len(proxy) == 0:
                    print('当前账号代理套餐已用完')
                    break
                proxyStatus = testProxy(proxy[0], 'jl', auth)
                if proxyStatus:
                    proxy_pool.append(proxy[0])
                else:
                    print('当前代理失效，重新获取')
                time.sleep(10)
            if proxy_pool is not None and len(proxy_pool) >= num:
                return proxy_pool, auth

    return None, None


"""
##############################
        星空代理相关方法
##############################
"""


def get_xingkong_proxy_ip_pool_one(proxy_api_apikey, proxy_api_sign, threadsNum=1):
    """
    获取星空代理主方法，proxy_api_apikey 星空代理apiKey, proxy_api_sign：星空代理apiSign
    """
    proxy_ip_pool = []
    retryTime = 0
    while True:
        retryTime += 1
        if retryTime >= 10:
            break
        resp = requests.get(
            f'http://api2.xkdaili.com/tools/XApi.ashx?apikey={proxy_api_apikey}&qty={threadsNum}&format=json&split=0&sign={proxy_api_sign}',
            timeout=20)
        res = resp.json()
        if res["status"] == 100:
            print(f'[{DateUtil.get_today()}]获取星空代理成功，本次获取了{threadsNum}个IP')
            for ip_info in res['data']:
                ip = ip_info['ip']
                port = ip_info['port']
                prov = ip_info['prov']
                city = ip_info['city']
                print(f'代理信息：{ip} 归属地：{prov}-{city}')
                proxy_ip_pool.append(f'{ip}:{port}')
            break
        elif res['status'] == 435:
            print(f'获取代理失败：代理IP状态异常，重新获取ip')
            time.sleep(10)
        elif res['status'] == 203 or res['status'] == 204:
            print(res['status'])
            print(f'获取代理失败：套餐已过期')
            break
        elif res['status'] == 206:
            print(f'获取代理失败：提取速度过快！')
            time.sleep(10)
        else:
            print(f'获取代理失败：异常未知！')
            break
    if len(proxy_ip_pool) > 0:
        return proxy_ip_pool
    else:
        current_ip = get_my_ip()
        # print(f'本地ip：{current_ip}')
        return None


def get_xingkong_proxy_ip_pool(proxy_xingkong_userInfo, num=1):
    """
    获取星空代理池，proxy_xingkong_userInfo 星空用户信息 num 提取数量
    """
    proxy_pool = []
    if '\n' in proxy_xingkong_userInfo:
        proxy_xingkong_userInfos = proxy_xingkong_userInfo.split("\n")
        k = 0
        for proxy_xingkong_user in proxy_xingkong_userInfos:
            k += 1
            proxy_api_sign = proxy_xingkong_user[0]
            proxy_api_apikey = proxy_xingkong_user[1]
            while len(proxy_pool) < num:
                proxy = get_xingkong_proxy_ip_pool_one(proxy_api_apikey, proxy_api_sign, 1)
                if proxy is None or len(proxy) == 0:
                    print('当前账号代理套餐已用完')
                    break
                print(f'====星空代理：第{k}个账号====')
                proxyStatus = testProxy(proxy[0], 'xk')
                if proxyStatus:
                    proxy_pool.append(proxy[0])
                else:
                    print('当前代理失效，重新获取')
                time.sleep(10)
            if proxy_pool is not None and len(proxy_pool) >= num:
                return proxy_pool
    else:
        proxy_api_sign = proxy_xingkong_userInfo.split(":")[0]
        proxy_api_apikey = proxy_xingkong_userInfo.split(":")[1]
        while len(proxy_pool) < num:
            proxy = get_xingkong_proxy_ip_pool_one(proxy_api_apikey, proxy_api_sign, 1)
            if proxy is None or len(proxy) == 0:
                print('当前账号代理套餐已用完')
                break
            proxyStatus = testProxy(proxy[0], 'xk')
            if proxyStatus:
                proxy_pool.append(proxy[0])
            else:
                print('当前代理失效，重新获取')
            time.sleep(10)
        if proxy_pool is not None and len(proxy_pool) >= num:
            return proxy_pool
    return None


"""
##############################
        携趣代理相关方法
##############################
"""


def get_xiequ_white_list(uid, ukey):
    resp = requests.get(f'http://op.xiequ.cn/IpWhiteList.aspx?uid={uid}&ukey={ukey}&act=get', timeout=20)
    while True:
        try:
            if resp.status_code == 200:
                res = resp.text
                if res != '':
                    # print(f'白名单：{res}')
                    return res
                else:
                    return None
            else:
                return None
        except:
            # print('get_xiequ_white_list->调用失败！')
            time.sleep(2)


def clear_all_xiequ_white_list(uid, ukey):
    resp = requests.get(f'http://op.xiequ.cn/IpWhiteList.aspx?uid={uid}&ukey={ukey}&act=del&ip=all', timeout=20)
    while True:
        try:
            if resp.status_code == 200:
                res = resp.text
                if res == 'success':
                    # print(f'白名单清除成功！')
                    return True
                else:
                    print(f'白名单清除失败：{res}')
                    return False
            else:
                return False
        except:
            # print('clear_all_xiequ_white_list->调用失败！')
            time.sleep(2)


def add_xiequ_white_list(uid, ukey, current_ip):
    resp = requests.get(f'http://op.xiequ.cn/IpWhiteList.aspx?uid={uid}&ukey={ukey}&act=add&ip={current_ip}',
                        timeout=20)
    while True:
        try:
            if resp.status_code == 200:
                res = resp.text
                if res == 'success':
                    print(f'{current_ip}，新增白名单成功！')
                    return True
                else:
                    print(f'{res}')
                    if res == 'IpRep':
                        return True
                    if '频繁' in 'res':
                        return True
                    return False
            else:
                # print(f'add_xiequ_white_list->接口调用失败！')
                time.sleep(2)
                return False
        except:
            print('add_xiequ_white_list->调用失败！')
            time.sleep(2)


def replace_xiequ_white_list(uid, ukey, current_ip):
    isClear = False
    isAdded = False
    whiteIps = get_xiequ_white_list(uid, ukey)
    if whiteIps is not None:
        if current_ip in whiteIps:
            return True
        else:
            # isClear = clear_all_xiequ_white_list(uid, ukey)
            # time.sleep(2)
            isAdded = add_xiequ_white_list(uid, ukey, current_ip)
            # time.sleep(1)
    else:
        isAdded = add_xiequ_white_list(uid, ukey, current_ip)
        time.sleep(1)


def get_xiequ_proxy(apiUrl, num=1):
    proxy_list = []
    resp = requests.get(apiUrl, timeout=30)
    try:
        res = resp.json()
        # print(str(res))
        if res['success']:
            for proxy_info in res['data']:
                proxy_ip = proxy_info["IP"]
                proxy_port = proxy_info["Port"]
                proxy_address = proxy_info["IpAddress"]
                print(f'[{DateUtil.get_today()}]获取携趣代理成功：{proxy_ip}:{proxy_port}，{proxy_address}')
                proxy_list.append(f'{proxy_ip}:{proxy_port}')
        else:
            print(str(res))
        return proxy_list
    except:
        print(f'获取携趣代理失败')
        return None


def getOrders(uid, ukey):
    resp = requests.get(
        f'http://op.xiequ.cn/ApiUser.aspx?act=suitdt&uid={uid}&ukey={ukey}', timeout=20)
    try:
        res = resp.json()
        if res['success']:
            # print(res)
            if len(res['data']) > 0:
                # print(f'获取携趣代理订单成功')
                return True
            else:
                return False
        else:
            return False
    except:
        # print(f'获取携趣代理失败')
        return False


def get_xiequ_proxy_pool(proxy_xiequ_userInfo, num=1):
    proxy_pool = []
    current_ip = get_my_ip()
    if '\n' in proxy_xiequ_userInfo:
        k = 0
        proxy_xiequ_userInfos = proxy_xiequ_userInfo.split("\n")
        for proxy_xiequ_user in proxy_xiequ_userInfos:
            k += 1
            uid = proxy_xiequ_user.split("|")[0]
            ukey = proxy_xiequ_user.split("|")[1]
            apiUrl = proxy_xiequ_user.split("|")[2]
            hasOrder = getOrders(uid, ukey)
            if hasOrder:
                replace_xiequ_white_list(uid, ukey, current_ip)
                while len(proxy_pool) < num:
                    proxy = get_xiequ_proxy(apiUrl)
                    if proxy is None or len(proxy) == 0:
                        time.sleep(10)
                        clear_all_xiequ_white_list(uid, ukey)
                        time.sleep(10)
                        # print('当前账号代理套餐已用完')
                        break
                    print(f'====携趣代理：第{k}个账号====')
                    proxyStatus = testProxy(proxy[0], 'xk')
                    if proxyStatus:
                        proxy_pool.append(proxy[0])
                if proxy_pool is not None and len(proxy_pool) >= num:
                    return proxy_pool
    else:
        uid = proxy_xiequ_userInfo.split("|")[0]
        ukey = proxy_xiequ_userInfo.split("|")[1]
        apiUrl = proxy_xiequ_userInfo.split("|")[2]
        replace_xiequ_white_list(uid, ukey, current_ip)
        while len(proxy_pool) < num:
            proxy = get_xiequ_proxy(apiUrl)
            if proxy is None or len(proxy) == 0:
                # print('当前账号代理套餐已用完')
                time.sleep(10)
                clear_all_xiequ_white_list(uid, ukey)
                time.sleep(10)
                break
            proxyStatus = testProxy(proxy[0], 'xk')
            if proxyStatus:
                proxy_pool.append(proxy[0])
            # else:
            #     print('当前代理失效，重新获取')
            time.sleep(2)
        if proxy_pool is not None and len(proxy_pool) >= num:
            return proxy_pool
    return None


class MyError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


## 定义随机异常
def ThrowErr(desc):
    raise MyError(desc)
