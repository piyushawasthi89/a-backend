import json
import jsonpatch
from pathlib import Path
import re
import bisect

from openai_client import call_openai_api

class FunctionStates:
    def __init__(self, version, content, problem_statement):
        self.version = int(version)
        self.content = content
        self.is_diff = False
        self.problem = problem_statement
    
    def setIsDiff(self, is_diff):
        self.is_diff = is_diff

    def updateContent(self, content):
        self.content = content
    
    def getVersion(self):
        return self.version
    
    def updateProblemStatement(self, problem_statement):
        self.problem = problem_statement

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
            json_data = read_file_content(file)
            function_obj = FunctionStates(function_version, json_data, json_data['problem'])
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
        messages = []
        function_states = f[1]
        src = function_states[0].content
        messages.append(create_message(f"given initial problem statement: {function_states[0].problem}  json {src}", "user"))
        for i in range(1, len(function_states)):
            dst = function_states[i].content
            diff = jsonpatch.JsonPatch.from_diff(src, dst)
            messages.append(create_message(f"given following json diff: {diff.patch}", "user"))
            messages.append(create_message(f"update the following problem statement: {function_states[i-1].problem}", "user"))
            updated_problem_statement = update_problem_statement(messages)
            function_states[i].content = diff
            function_states[i].is_diff = True
            function_states[i].problem = updated_problem_statement
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

def update_problem_statement(messages):
    response = call_openai_api(messages)
    if response:
        updated_problem = response['choices'][0]['message']['content']
        matches = re.findall(r'"(.*?)"', updated_problem)
        if matches:
            updated_problem = matches[0]
            return updated_problem
        matches = re.findall(r'(?<=:).*', updated_problem)
        if matches:
            updated_problem = matches[0]
            return updated_problem
        return updated_problem
        # messages.append(create_message(updated_problem, "assistant"))
    raise ValueError("failed to get response from OpenAI")

def create_message(message, role):
    return {
        "content": message,
        "role": role
    }     