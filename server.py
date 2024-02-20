from flask import Flask, jsonify, request, g, session
import function_parser
import json
from flask_cors import CORS, cross_origin
import jsonpatch
import pickle

app = Flask(__name__)
app.secret_key = 'test_private_key'
CORS(app)

function_content_dict = None

@app.before_request
def initialize_global_variable():
    global function_content_dict
    function_content_dict = function_parser.parse_function_files('Function States/')
    

@app.route('/api')
def get_message():
    return jsonify({'message': 'Hello from Flask'})

@app.route('/get_function')
def get_function():
    function_name = request.args.get('name')
    version = request.args.get('version')
    function_version = int(version)
    print(function_content_dict)
    src_function = function_content_dict[function_name][0].content
    dst_function = ''
    if function_version == 0:
        return json.dumps(src_function)
    else:
        for i in range(1, function_version + 1):
            patch = function_content_dict[function_name][i].content
            dst_function = patch.apply(src_function)
            src_function = dst_function
    return json.dumps(src_function)

@app.route('/')
def get_function_name_and_versions():
    # function_content_dict = function_parser.parse_function_files('Function States/')
    data = []
    print(function_content_dict)
    for function_name, function_list in function_content_dict.items():
        function_name_and_versions = {}
        function_name_and_versions["name"] = function_name
        function_name_and_versions["versions"] = [obj.version for obj in function_list]
        data.append(function_name_and_versions)
    return json.dumps(data)

if __name__ == '__main__':
    app.run(port=8001, debug=True)
