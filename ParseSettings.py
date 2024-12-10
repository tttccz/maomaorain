from configparser import ConfigParser

# 创建解析器对象
config = ConfigParser()

# 读取配置文件
config.read('settings.ini', 'utf-8')

# 读取database部分的配置项
address = config.get('qinglong', 'address')
address_local = config.get('qinglong', 'address_local')
client_id = config.get('qinglong', 'client_id')
client_secret = config.get('qinglong', 'client_secret')

# 读取application部分的配置项
wxPusherAppToken = config.get('wxPush', 'wxpusherapptoken')
wxPusherUuid = config.get('wxPush', 'wxpusheruuid')

