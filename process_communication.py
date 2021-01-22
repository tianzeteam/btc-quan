# encoding=utf-8


from multiprocessing.managers import BaseManager


# 定义一个Manager类
class InfoManager(BaseManager):
    pass


class ShareItem:
    def __init__(self, ):
        self.items = dict()

    def set(self, key, value):
        self.items[key] = value

    def get(self, key):
        return self.items.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)


# 为这个manager类注册存储容器，也就是通过这个manager类实现的共享的变量，
# 这个变量最好是一个类实例，自己定义的或者python自动的类的实例都可以
# 这里不能把d改成dict()，因为Client那边执行d['keyi']='value'的时候会报错：d这个变量不能修改
share_item = ShareItem()
InfoManager.register('share_item', callable=lambda: share_item)


class ManagerServer:
    """
      multiprocess Manager服务类
    """
    def __init__(self, domain, port, auth_key):
        self.domain = domain
        self.port = port
        self.auth_key = auth_key
        self.queue_manager = None
        self.share_item = None
        self.server = None

    def start_manager_server(self):
        self.queue_manager = InfoManager(address=('', self.port), authkey=self.auth_key)
        self.server = self.queue_manager.get_server()

    def run(self):
        self.start_manager_server()
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()


class ManagerClient:
    """
    访问 mutiprocess Manager的类
    """

    def __init__(self, domain, port, auth_key):
        self.domain = domain
        self.port = port
        self.auth_key = auth_key
        self.info_manager = InfoManager(address=(self.domain, self.port), authkey=self.auth_key)
        self.info_manager.connect()

    def get_share_data(self):
        return self.info_manager.share_item()

    if __name__ == '__main__':
        pass
