# -*- encoding: utf-8 -*-
"""
@File    : config.py
@Time    : 2020/07/10 19:08
@Author  : iicoming@hotmail.com
"""

FLAG = False

ONLINE = {
    'src': '/home/online/apis/src',
    'dst': '/home/online/apis/dst',
    'apipath': '/home/online/apis/path'
}

DEV = {
    'src': '/Users/sec-mac/IdeaProjects/',
    'dst': '/Users/sec-mac/test/dst',
    'apipath': '/Users/sec-mac/test/apis'
}

config = ONLINE if FLAG else DEV

REDIS_IP = ""

REDIS_CONFIG = {
    "host": "{host}".format(host=REDIS_IP if FLAG else "127.0.0.1"),
    "port": 6379,
    "db": 0,
    "password": "",
    "max_connections": 100,
    "socket_timeout": 5,
    "decode_responses": True
}

mapping = {
    'mapping': [
        'DeleteMapping',
        'GetMapping',
        'PatchMapping',
        'PostMapping',
        'PutMapping',
        'RequestMapping'],
    'controller': [
        'RestController',
        'Controller']}

buildTable = ['build.gradle', 'pom.xml', 'uwsgi.ini']
