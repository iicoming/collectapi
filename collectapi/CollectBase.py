# -*- encoding: utf-8 -*-
"""
@File    : CollectBase.py
@Time    : 2020/7/10 19:08
@Author  : iicoming@hotmail.com
"""

import subprocess
import sys
import time

import redis

from config.config import REDIS_CONFIG


class CollectBase:
    def __init__(self):

        self.today = time.strftime("%Y-%m-%d", time.localtime())
        self.client = redis.StrictRedis(**REDIS_CONFIG)

    def catch_exception(func):
        time_now = time.strftime("%Y-%m-%d", time.localtime())

        def wrapper(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
                return res
            except Exception as e:
                print(time_now +
                      ': Error method: \n\t%s,\nException info:\n\t%s' %
                      (func.__name__, e))
                print("Paramters:")
                print('\t', *args)
                sys.exit()

        return wrapper

    @catch_exception
    def get_single_project_info(self, path):
        branch, stderr_branch = subprocess.Popen('git -C {path} branch -v'.format(path=path),
                                                 shell=True, stdout=subprocess.PIPE).communicate()

        git_address, stderr_git_address = subprocess.Popen(
            'git -C {path} remote -v'.format(path=path), shell=True,
            stdout=subprocess.PIPE).communicate()
        real_branch = '_'.join(str(branch, 'utf-8').split(' ')[1:3])
        real_git_address = str(git_address, 'utf-8').split(' ')[0].split('\t')[1].replace(' ', '')

        return real_git_address + '__' + real_branch
