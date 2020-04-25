import json
from xmlrpc import client

from ImgEngine_pub import *


class ImageEngineClient:
    def __init__(self, proxy: str):
        self.__proxy = proxy
        self.__client = client.ServerProxy(self.__proxy, allow_none=True)

    @staticmethod
    def __get_data(path_or_img, is_img=False):
        if is_img:
            data = img2data(path_or_img)
        else:
            img = Image.open(path_or_img)
            data = img2data(img)
        return data

    def read_data(self, html_path: str):
        callback = self.__client.read_data(html_path)
        return callback

    def search_img(self, path_or_img, is_img=False):
        data = self.__get_data(path_or_img, is_img=is_img)
        callback = self.__client.search_img(data)
        callback = json.loads(callback)
        return callback

    def add_data(self, path_or_img, is_img=False, metadata=None):
        data = self.__get_data(path_or_img, is_img=is_img)
        callback = self.__client.add_data(data, metadata=metadata)
        return callback
