#
import json
import time
import urllib.parse

import requests
import urllib3

import DateUtil
import utils_proxy

try:
    from urllib3.util import create_urllib3_context
except Exception as e:
    print(e)


def post(url, headers, data=None, json=None, timeout=10):
    return request_avoid_exception("POST", url, headers, data, json=json, timeout=timeout)


def put(url, headers, data=None):
    return request_avoid_exception("PUT", url, headers, json.dumps(data), timeout=10)


def get(url, headers, allow_redirects=True):
    return request_avoid_exception("GET", url, headers, timeout=10, allow_redirects=allow_redirects)


def request_avoid_exception(method, url, headers, data='', json=None, timeout=10, allow_redirects=True):
    retryTime = 0
    while True:
        try:
            response = requests.request(method, url, headers=headers, data=data, json=json, timeout=timeout,
                                        allow_redirects=allow_redirects)
            return response
        except Exception as e:
            print(e)
            retryTime += 1
            if retryTime >= 5:
                return None
            time.sleep(5)
            continue


def request_avoid_exception_unsafe(method, url, headers, data=None, json=None, timeout=10):
    ctx = create_urllib3_context()
    ctx.load_default_certs()
    ctx.options |= 0x4  # ssl.OP_LEGACY_SERVER_CONNECT
    retryTime = 0
    while True:
        try:
            with urllib3.PoolManager(ssl_context=ctx, timeout=urllib3.Timeout(connect=5.0, read=10.0)) as http:
                if method == "GET":
                    r = http.request(method, url=url, headers=headers)
                else:
                    if data:
                        r = http.request(method, url=url, headers=headers, body=data, timeout=timeout)
                    if json:
                        r = http.request(method, url=url, headers=headers, json=json, timeout=timeout)
                return r
        except Exception as e:
            print(e)
            retryTime += 1
            if retryTime >= 10:
                return None
            print("接口调用异常，重试...")
            time.sleep(5)
            continue


def post_proxy(url, headers, data=None, json=None, timeout=10, retry=5, proxy_type='xq'):
    proxy = create_proxy(proxy_type)
    proxies = {}
    while retry > 0:
        try:
            proxy.get_proxy()
        except Exception as e:
            print(f"获取代理异常，停止采用代理请求。{e}")
            return post(url, headers, data=data, json=json, timeout=timeout)
        try:
            proxy_type = proxy.proxy_type
            proxies = proxy.proxies
            http_proxy = proxies['http']
            proxies['https'] = http_proxy
            if proxy_type == 'jl':
                proxy_auth = proxy.proxy_auth
                headers['Proxy-Authorization'] = f'Basic {proxy_auth}'
            print(f"{DateUtil.get_today()} 开始执行代理请求")
            response = requests.request("POST", url, headers=headers, data=data, json=json, timeout=timeout,
                                        proxies=proxies)
            return response
        except Exception as e:
            print(f"{DateUtil.get_today()} 执行代理请求异常：{e}")
            if 'Your proxy appears to only use HTTP and not HTTPS' in str(e):
                http_proxy = proxies['http']
                proxies['https'] = http_proxy
                try:
                    print(f"{DateUtil.get_today()} 开始执行代理请求")
                    response = requests.request("POST", url, headers=headers, data=data, json=json, timeout=timeout,
                                                proxies=proxies)
                except Exception as e:
                    print(f"{DateUtil.get_today()} 替换Https代理执行代理请求异常：{e}")
                    pass
            retry -= 1
            continue
    if retry == 0:
        return post(url, headers, data=data, json=json, timeout=timeout)


class create_proxy:

    def __init__(self, proxy_type):
        self.proxy_auth = None
        self.proxies = None
        self.proxy_type = proxy_type

    def get_proxy(self):
        proxy_results = utils_proxy.get_proxy_pool_by_type(self.proxy_type)
        if len(proxy_results) > 0:
            proxy_result = proxy_results[0]
            proxy_ip = proxy_result['proxy_ip']
            self.proxies = {
                "http": f"http://{proxy_ip}",
                "https": f"https://{proxy_ip}"
            }
            self.proxy_type = proxy_result['proxy_type']
            self.proxy_auth = proxy_result['auth']
        else:
            utils_proxy.ThrowErr("获取代理失败")


def decodeParam(param):
    return urllib.parse.unquote(param)

def encodeParam(param):
    return urllib.parse.quote_plus(param)