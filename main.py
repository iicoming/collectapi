# -*- encoding: utf-8 -*-
"""
@File    : main.py
@Time    : 2020/07/10 19:08
@Author  : iicoming@hotmail.com
"""

import time

from collectapi.CollectApi import CollectApi

if __name__ == '__main__':
    start = time.time()
    collectApi = CollectApi()
    collectApi.start()
    end = time.time()
    print(end - start, '\n')
