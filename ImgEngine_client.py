import json
from configparser import ConfigParser
from xmlrpc import client

import paramiko

from ImgEngine_pub import *


class ImageEngineClient:
    def __init__(self, server_host: str, server_port: int, ssh_port: int = 22):
        """

        :param server_host: server ip/domain,like xxx.xxx.xxx.xxx or abc.example.com
        :param server_port: the port witch server listening to
        :param ssh_port: the ssh port of server
        """
        self.__server_host = server_host
        self.__server_port = server_port
        self.__ssh_port = ssh_port
        self.__client = client.ServerProxy(f'http://{self.__server_host}:{self.__server_port}', allow_none=True)

    def __get_data(self, path_or_img):
        if isinstance(path_or_img, Image.Image):
            data = img2data(path_or_img)
            file_ext = '.jpg'
        elif type(path_or_img) == str and os.path.exists(path_or_img):
            _, file_ext = os.path.splitext(path_or_img)
            if file_ext.lower() == '.jpg':
                img = Image.open(path_or_img)
                data = img2data(img)
            elif file_ext.lower() in ['.gif', '.mp4']:
                data = self.__send_file(path_or_img)
            else:
                print('Invalid format')
                data = None
                file_ext = ''
        else:
            print('Something went wrong while reading data!')
            data = None
            file_ext = ''
        return data, file_ext

    def __send_file(self, file, dir_path='/tmp'):
        config = ConfigParser()
        config.read('server.ini')
        transport = paramiko.Transport((self.__server_host, self.__ssh_port))
        transport.connect(username=config['SSH']['username'], password=config['SSH']['password'])
        sftp = paramiko.SFTPClient.from_transport(transport)
        fullname = os.path.basename(file)
        fullpath = f'{dir_path}/{fullname}'
        sftp.put(file, fullpath)
        transport.close()
        return fullpath

    def read_data(self, html_path: str, tags: list = None):
        callback = self.__client.read_data(html_path)
        return callback

    def search_img(self, path_or_img):
        data, file_ext = self.__get_data(path_or_img)
        if data:
            callback = self.__client.search_img(data, file_ext)
            callback = json.loads(callback)
        else:
            callback = None
        return callback

    def add_data(self, path_or_img, message):
        data, file_ext = self.__get_data(path_or_img)
        if data:
            callback = self.__client.add_data(data, file_ext, message)
        else:
            callback = None
        return callback
