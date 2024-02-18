import json
import jsonpatch
from pathlib import Path
import re
import bisect

class FunctionStates:
    def __init__(self, version, content):
        self.version = int(version)
        self.content = content
        self.is_diff = False
    
    def setIsDiff(self, is_diff):
        self.is_diff = is_diff

    def updateContent(self, content):
        self.content = content
    
    def getVersion(self):
        return self.version

def parse_function_name_version(filename):
    pattern = r'Function([A-Za-z]+)_(\d+)\.json'
    match = re.search(pattern, filename)
    if match:
        return match.group(1), match.group(2)
    return None, None

def parse_file_content_to_dict(files):
    function_content_dict = {}
    for file in files:
        function_name, function_version = parse_function_name_version(file.name)
        if function_name is not None and function_version is not None:
            function_obj = FunctionStates(function_version, read_file_content(file))
            if function_name not in function_content_dict:
                function_states = [function_obj]
                function_content_dict[function_name] = function_states
            else:
                function_states = function_content_dict[function_name]
                bisect.insort(function_states, function_obj, key=sort_by_version)
        else:
            raise ValueError("Function Name/Version is null")
    return function_content_dict

def create_diff_states(function_content_dict):
    for f in function_content_dict.items():
        function_states = f[1]
        src = function_states[0].content
        for i in range(1, len(function_states)):
            dst = function_states[i].content
            diff = jsonpatch.JsonPatch.from_diff(src, dst)
            function_states[i].content = diff
            function_states[i].is_diff = True
            src = dst

def sort_by_version(x):
    return x.version

def read_file_content(file):
    with open(file, 'r') as f:
            return json.load(f)

def parse_function_files(file_dir):
    directory = Path(file_dir)
    files = directory.glob('*')
    function_content_dict = parse_file_content_to_dict(files)
    create_diff_states(function_content_dict)
    return function_content_dict
    # for file_path in files:
    #     with open(file_path, 'r') as file:
    #         function_content_dict[file_path.name] = json.load(file)
    #     match = re.search(pattern, file_path.name)
    #     if match:
    #         function_name = match.group(1)
    #         function_version = match.group(2)
    #         if function_name in function_version_dict:
    #             # If the key exists, increment the value
    #             function_version_dict[function_name] += 1
    #         else:
    #             # If the key does not exist, insert the key with a value of 1
    #             function_version_dict[function_name] = 1

    # function_diff_dict = {}
    # for function_name, function_version in function_version_dict.items():
    #     function_diff_list = []
    #     src_file_content = function_content_dict["Function{}_{}.json".format(function_name, 0)]
    #     function_diff_list.append(src_file_content)
    #     for i in range(1, function_version):
    #         full_file_name = "Function{}_{}.json".format(function_name, i)
    #         dst_file_content = function_content_dict[full_file_name]
    #         patch = jsonpatch.JsonPatch.from_diff(src_file_content, dst_file_content)
    #         function_diff_list.append(patch)
    #         src_file_content = dst_file_content
    #     function_diff_dict[function_name] = function_diff_list
    #     function_diff_list = []
    # return function_diff_dict