# -*- coding:utf-8 -*-
"""
DateUtil：时间工具类
"""
import datetime
import time


def get_current_timestamp_13():
    """
    获取当前时间的13位时间戳
    @return 当亲13位时间戳
    """
    return int(time.time() * 1000)


def get_current_timestamp_10():
    """
    获取当前时间的10位时间戳
    @return 当亲10位时间戳
    """
    return int(time.time())


def date_str_to_timestamp_13(date: str, form: str = "%Y-%m-%d %H:%M:%S"):
    """
    日期转13位时间戳
    @param: date 2023-09-26 10:57:57
    @param: form %Y-%m-%d %H:%M:%S
    @return 13位时间戳
    """
    timeArray = time.strptime(date, form)
    timestamp = time.mktime(timeArray)
    return int(timestamp * 1000)


def date_str_to_timestamp_10(date: str, form: str = "%Y-%m-%d %H:%M:%S"):
    """
    日期转10位时间戳
    @param: date 2023-09-26 10:57:57
    @param: form %Y-%m-%d %H:%M:%S
    @return 10位时间戳
    """
    timeArray = time.strptime(date, form)
    timestamp = time.mktime(timeArray)
    return int(timestamp)


def timestamp_to_date_str(timestamp: int, form: str = "%Y-%m-%d %H:%M:%S"):
    """
    时间戳转时间
    @param: timestamp 时间戳
    @param: form %Y-%m-%d %H:%M:%S
    @return 格式化后时间戳
    """
    timestampStr = str(timestamp)
    if len(timestampStr) != 13 and len(timestampStr) != 10:
        raise ValueError("timestamp必须为13位或者10位")
    if len(timestampStr) == 13:
        timestamp = int(timestamp / 1000)
    timeArray = time.localtime(timestamp)
    formatTime = time.strftime(form, timeArray)
    return formatTime


def is_before(hour=8, minute=0, second=0):
    """
    判断当前时间是否早于当天目标时间
    @param hour 小时
    @param minute 分钟
    @param second 秒
    @return True早于 False 晚于
    """
    today = datetime.datetime.today()
    targetTime = datetime.datetime.combine(today, datetime.time(hour=hour, minute=minute, second=second))
    now = datetime.datetime.now()
    return now < targetTime


def is_after(hour=8, minute=0, second=0):
    """
    判断当前时间是否晚于当天目标时间

    @param hour 小时
    @param minute 分钟
    @param second 秒
    @return True晚于 False 早于
    """
    return not is_before(hour, minute, second)


def is_between(beforeHour=8, beforeMinute=0, beforeSecond=0,
               afterHour=9, afterMinute=0, afterSecond=0):
    """
    判断当前时间是否在时间区间内

    @param beforeHour 目标时间区间开始-小时
    @param beforeMinute 目标时间区间开始-分钟
    @param beforeSecond 目标时间区间开始-秒
    @param afterHour 目标时间区间结束-小时
    @param afterMinute 目标时间区间结束-分钟
    @param afterSecond 目标时间区间结束-秒
    """
    return is_after(beforeHour, beforeMinute, beforeSecond) and is_before(afterHour, afterMinute, afterSecond)


def get_today(form: str = "%Y-%m-%d %H:%M:%S"):
    """
    获取当天时间

    @param form 格式化方式
    @return 当天时间
    """
    return timestamp_to_date_str(int(time.time()), form)


def get_today_date(form: str = "%Y-%m-%d"):
    """
    获取当天日期

    @param form 格式化方式
    @return 当天日期
    """
    return timestamp_to_date_str(int(time.time()), form)


def get_today_time(form: str = "%H:%M:%S"):
    """
    获取当天时间

    @param form 格式化方式
    @return 当天时间
    """
    return timestamp_to_date_str(int(time.time()), form)


def day_of_week():
    """
    获取今天是周几

    @return 星期几
    """
    weekday = datetime.datetime.today().weekday() + 1
    return str(weekday)


def day_of_month():
    """
    获取今天是一个月的第几天

    @return 一个月几号
    """
    today = get_today_date()
    return int(today.split("-")[2])


def get_month():
    """
    获取当前日期的月份

    @return 几月份
    """
    return int(get_today_date().split("-")[1])


def isTime(current_time, day, hour, minute=0, second=0, microsecond=0):
    tomorrow = current_time + datetime.timedelta(days=day)
    tomorrow_zero = tomorrow.replace(hour=hour, minute=minute, second=second, microsecond=microsecond)
    # 判断是否是第 day 天的 hour 时 minute 分 second 秒
    if current_time >= tomorrow_zero:
        # print(f"原时间-{current_time}，已过第{day}天的{hour}时{minute}分{second}秒")
        return 0
    else:
        # print(f"原时间-{current_time}，未过第{day}天的{hour}时{minute}分{second}秒")
        time_difference = tomorrow_zero - current_time
        return time_difference.total_seconds()


def get_now_utc():
    now = datetime.datetime.utcnow()
    return now.strftime('%Y%m%dT%H%M%SZ')


def get_date_range(start_date, end_date):
    """
    获取两个日期之间的所有日期（包含起始日期和结束日期）。

    :param start_date: 开始日期，字符串格式 'YYYY-MM-DD'
    :param end_date: 结束日期，字符串格式 'YYYY-MM-DD'
    :return: 日期列表，每个日期为字符串格式 'YYYY-MM-DD'
    """
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    delta = datetime.timedelta(days=1)

    date_list = []
    current_date = start
    while current_date <= end:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += delta

    return date_list

if __name__ == '__main__':
    start_date = '2024-07-01'
    end_date = '2024-07-10'
    date_range = get_date_range(start_date, end_date)
    print(date_range)
