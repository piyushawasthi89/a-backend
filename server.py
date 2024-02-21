from flask import Flask, jsonify, request, g, session, abort
import function_parser
import json
from flask_cors import CORS, cross_origin
import jsonpatch
import pickle

app = Flask(__name__)
app.secret_key = 'test_private_key'
CORS(app)

function_content_dict = None

def are_parameters_valid(function_name, function_version):
    if function_name in function_content_dict and function_version < len(function_content_dict[function_name]):
        return True
    return False

# @app.before_request
# def initialize_global_variable():
#     global function_content_dict
#     function_content_dict = function_parser.parse_function_files('Function States/')
    

@app.route('/api')
def get_message():
    return jsonify({'message': 'Hello from Flask'})

@app.route('/get_function')
def get_function():
    function_name = request.args.get('name')
    version = request.args.get('version')
    function_version = int(version)
    src_function = function_content_dict[function_name][0].content
    dst_function = ''
    if are_parameters_valid(function_name, function_version):
        if function_version == 0:
            return json.dumps(src_function)
        else:
            for i in range(1, function_version + 1):
                patch = function_content_dict[function_name][i].content
                problem = function_content_dict[function_name][i].problem
                dst_function = patch.apply(src_function)
                src_function = dst_function
        response = {"function": src_function, "updated_prompt": problem}
        return json.dumps(response)
    else:
        abort(400, "Invalid request")
    

@app.route('/get_updated_prompt')
def get_updated_prompt():
    function_name = request.args.get('name')
    version = request.args.get('version')
    function_version = int(version)
    if are_parameters_valid(function_name, function_version):
        return json.dumps({"value": function_content_dict[function_name][function_version].problem})
    else:
        abort(400, "Invalid request")

@app.route('/')
def get_function_name_and_versions():
    global function_content_dict
    function_content_dict = function_parser.parse_function_files('Function States/')
    data = []
    for function_name, function_list in function_content_dict.items():
        function_name_and_versions = {}
        function_name_and_versions["name"] = function_name
        function_name_and_versions["versions"] = [obj.version for obj in function_list]
        data.append(function_name_and_versions)
    return json.dumps(data)

if __name__ == '__main__':
    app.run(port=8001, debug=True)
