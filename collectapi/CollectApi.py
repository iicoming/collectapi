# -*- encoding: utf-8 -*-
"""
@File    : CollectApi.py
@Time    : 2020/04/14 18:39
@Author  : iicoming@hotmail.com
"""
import json
import os
import time

import javalang

from collectapi.CollectBase import CollectBase
from config.config import config
from config.config import mapping, buildTable


class CollectApi(CollectBase):

    def __init__(self):
        super().__init__()
        self.root_directory = config['src']
        self.gits = {}
        self.all_project_paths = {}

    def start(self):
        self.get_project_root_lists()
        for key in self.all_project_paths.keys():
            if 'ssm' not in key:
                continue
            self.handle_content(key, self.gits.get(key))

    @CollectBase.catch_exception
    def get_project_root_lists(self):
        lists = os.listdir(self.root_directory)
        for index, value in enumerate(lists):
            if value.startswith('.'):
                continue
            real_path = os.path.join(self.root_directory, value)

            if not self.check_create_time(real_path):
                continue

            if not os.path.exists(real_path + '/.git'):
                continue

            git_address = self.get_single_project_info(real_path)
            if not git_address:
                continue
            self.gits[real_path] = git_address
            self.all_project_paths[real_path] = []

    @CollectBase.catch_exception
    def get_allarameters(self, parameters):
        params = []
        for index, parameter in enumerate(parameters):
            params.append(parameter.type.name + '__' + parameter.name)
        params.sort()
        result = '||'.join(params)
        return result

    def extract_api_from_file(self, annotation):
        result = []
        if isinstance(annotation.element, javalang.tree.Literal):
            result.append(annotation.element.value.replace('"', ''))
        elif isinstance(annotation.element, list):
            for sub_index, su_element in enumerate(annotation.element):
                if su_element.name != 'value':
                    continue
                if isinstance(
                        su_element.value,
                        javalang.tree.ElementArrayValue):
                    for value_index, value_item in enumerate(
                            su_element.value.values):
                        if isinstance(value_item, javalang.tree.BinaryOperation):
                            operandl = type(value_item.operandl)
                            operandr = type(value_item.operandr)
                            if operandl == javalang.tree.MemberReference and operandr == javalang.tree.Literal:
                                result.append(
                                    value_item.operandr.value.replace(
                                        '"', ''))
                        else:
                            result.append(value_item.value.replace('"', ''))
                elif isinstance(su_element.value, javalang.tree.MemberReference):
                    continue
                elif isinstance(su_element.value, javalang.tree.Literal):
                    result.append(su_element.value.value.replace('"', ''))

                elif isinstance(su_element.value, javalang.tree.BinaryOperation):
                    operandl = type(su_element.value.operandl)
                    operandr = type(su_element.value.operandr)
                    if operandl == javalang.tree.MemberReference and operandr == javalang.tree.Literal:
                        result.append(
                            su_element.value.operandr.value.replace(
                                '"', ''))


                else:
                    result.append(su_element.value.value.replace('"', ''))
        elif isinstance(annotation.element, javalang.tree.ElementArrayValue):
            if isinstance(annotation.element.values, list):
                for array_index, array_item in enumerate(
                        annotation.element.values):
                    if isinstance(array_item, javalang.tree.BinaryOperation):
                        operandl = type(array_item.operandl)
                        operandr = type(array_item.operandr)
                        if operandl == javalang.tree.MemberReference and operandr == javalang.tree.Literal:
                            result.append(
                                array_item.operandr.value.replace(
                                    '"', ''))
                    elif isinstance(array_item, javalang.tree.MemberReference):
                        pass
                    else:
                        result.append(array_item.value.replace('"', ''))
        elif isinstance(annotation.element, javalang.tree.BinaryOperation):
            operandl = type(annotation.element.operandl)
            operandr = type(annotation.element.operandr)
            if operandl == javalang.tree.MemberReference and operandr == javalang.tree.Literal:
                result.append(
                    annotation.element.operandr.value.replace(
                        '"', ''))
        return result

    def hanlde_parent(self, tree):
        parent = False
        controller_flag = False
        root = []
        for parent_index, classDeclaration in tree.filter(
                javalang.tree.ClassDeclaration):
            if not classDeclaration.annotations:
                break
            for index, annotation in enumerate(classDeclaration.annotations):
                if annotation.name in mapping['controller']:
                    controller_flag = True
                    continue
                if annotation.name in mapping['mapping']:
                    if not annotation.element:
                        continue
                    parent = True
                    root = self.extract_api_from_file(annotation)

        return (parent, controller_flag, list(set(root)))

    def handle_child(self, tree, parent, root):
        apis = []
        for parent_index, methodDeclaration in tree.filter(
                javalang.tree.MethodDeclaration):
            for index, annotation in enumerate(methodDeclaration.annotations):
                if annotation.name not in mapping['mapping']:
                    continue
                if not annotation.element:
                    continue
                prefix = str(
                    annotation.name).lower().replace(
                    'mapping',
                    '') + '|||'
                parameters = methodDeclaration.parameters
                if parameters:
                    params = self.get_allarameters(parameters)
                    if params:
                        prefix = prefix + params + '|||'
                api = self.extract_api_from_file(annotation)
                if not api:
                    continue
                for api_index, api_item in enumerate(api):
                    sub_api = api_item.replace('"', '')
                    if not root:
                        real_api = prefix + \
                                   sub_api.replace('//', '/').replace('//', '/')
                        apis.append(real_api)
                    else:
                        for root_index, root_item in enumerate(root):
                            if parent:
                                real_api = root_item + "/" + sub_api
                            else:
                                real_api = sub_api
                            real_api = prefix + \
                                       real_api.replace('//', '/').replace('//', '/')
                            apis.append(real_api)
        return apis

    @CollectBase.catch_exception
    def handle_content(self, key, git):
        result = []
        hardcode = []
        build = []
        for root, dirs, files in os.walk(key):
            catalog = root.split(os.sep)[-1]
            if str(catalog).startswith('.'):
                continue
            for file in files:
                if file.startswith('.'):
                    continue
                if file.endswith('.jar'):
                    hardcode.append(file)
                if file in buildTable:
                    build.append(file)

                if not file.endswith('.java'):
                    continue
                pysical_path = root + os.sep + file
                try:
                    with open(pysical_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        content = content.replace('\ufeff', '')
                        if '@Controller' not in content and '@RestController' not in content:
                            continue
                        tree = javalang.parse.parse(content)
                        (parent, controller_flag, root_) = self.hanlde_parent(tree)
                        apis = self.handle_child(tree, parent, root_)
                        if not apis:
                            continue
                        result.extend(apis)
                except Exception as e:
                    print("File:\n\t" + pysical_path)
                    print("Exception:\n\t", e)
        if config['dst'].endswith(os.sep):
            dst = config['dst'] + \
                  git.replace(os.sep, '_').replace(":", '_').replace("/", '_')
        else:
            dst = config['dst'] + os.sep + \
                  git.replace(os.sep, '_').replace(":", '_').replace("/", '_')

        if result:
            self.import_data(git, result)
        with open(dst, 'w') as w:
            w.write(str(list(set(build))) + '\n')
            w.write(str(list(set(hardcode))) + '\n')
            w.write(str(list(set(result))))

    @CollectBase.catch_exception
    def get_real_path(self, project_info):
        if config['apipath'].endswith(os.sep):
            apipath = config['apipath'] + project_info
        else:
            apipath = config['apipath'] + os.sep + project_info
        return apipath

    @CollectBase.catch_exception
    def handle_exist_path(self, api_path, git, result):

        with open(api_path, 'r') as api_f:
            api_content = eval(api_f.read())
            difference = list(set(result).difference(set(api_content)))
            for index, item in enumerate(difference):
                tmp = {}
                tmp['timestamp'] = self.today
                tmp['git_address'] = git.split('__')[0]
                tmp['branch'] = git.split('__')[1]
                tmp['api'] = str(item).split('|||')[-1]
                tmp["method"] = str(item).split('|||')[0]
                if len(str(item).split('|||')) == 3:
                    tmp["parameters"] = str(item).split('|||')[1]
                else:
                    tmp["parameters"] = ""
                self.client.lpush("apis", json.dumps(tmp))

        with open(api_path, 'w') as w:
            w.write(str(result))

    @CollectBase.catch_exception
    def handle_not_exist_path(self, apipath, git, result):

        for index, item in enumerate(result):
            tmp = {}
            tmp['api'] = str(item).split('|||')[-1]
            tmp['timestamp'] = self.today
            tmp['git_address'] = git.split('__')[0]
            tmp['branch'] = git.split('__')[1]
            tmp["method"] = str(item).split('|||')[0]
            if len(str(item).split('|||')) == 3:
                tmp["parameters"] = str(item).split('|||')[1]
            else:
                tmp["parameters"] = ""
            self.client.lpush("apis", json.dumps(tmp))
        with open(apipath, 'w') as w:
            w.write(str(result))

    @CollectBase.catch_exception
    def import_data(self, git, result):
        project = git.replace(os.sep, '_').replace(":", '_').replace("/", '_')
        api_path = self.get_real_path(project)
        if os.path.exists(api_path):
            self.handle_exist_path(api_path, git, result)
        else:
            self.handle_not_exist_path(api_path, git, result)

    @CollectBase.catch_exception
    def check_create_time(self, real_path):
        ctime = time.ctime(os.path.getmtime(real_path))
        temp_time = time.strptime(ctime, '%a %b %d %H:%M:%S %Y')
        res_time = time.strftime('%Y-%m-%d', temp_time)
        return self.today == res_time

    def test_parse_file(self, pysical_path):
        try:
            with open(pysical_path, 'r', encoding='utf-8') as f:
                content = f.read()
                content = content.replace('\ufeff', '')
                if '@Controller' not in content and '@RestController' not in content:
                    return

                tree = javalang.parse.parse(content)
                (parent, controller_flag, root_) = self.hanlde_parent(tree)
                apis = self.handle_child(tree, parent, root_)
                if not apis:
                    return
                print(apis)
        except Exception as e:
            print("File:\n\t" + pysical_path)
            print("Exception:\n\t", e)
