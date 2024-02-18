import json
import jsonpatch
from pathlib import Path
import re

def parse_function_files(file_dir):
    directory = Path(file_dir)
    files = directory.glob('*')
    pattern = r'Function([A-Za-z]+)_(\d+)\.json'
    function_version_dict = {}
    function_content_dict = {}
    for file_path in files:
        with open(file_path, 'r') as file:
            function_content_dict[file_path.name] = json.load(file)
        match = re.search(pattern, file_path.name)
        if match:
            function_name = match.group(1)
            function_version = match.group(2)
            if function_name in function_version_dict:
                # If the key exists, increment the value
                function_version_dict[function_name] += 1
            else:
                # If the key does not exist, insert the key with a value of 1
                function_version_dict[function_name] = 1

    function_diff_dict = {}
    for function_name, function_version in function_version_dict.items():
        function_diff_list = []
        src_file_content = function_content_dict["Function{}_{}.json".format(function_name, 0)]
        function_diff_list.append(src_file_content)
        for i in range(1, function_version):
            full_file_name = "Function{}_{}.json".format(function_name, i)
            dst_file_content = function_content_dict[full_file_name]
            patch = jsonpatch.JsonPatch.from_diff(src_file_content, dst_file_content)
            function_diff_list.append(patch)
            src_file_content = dst_file_content
        function_diff_dict[function_name] = function_diff_list
        function_diff_list = []
    return function_diff_dict