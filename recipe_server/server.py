from flask import Flask, request, json, jsonify
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from optimizer import Optimizer

app = Flask(__name__, static_folder='.', static_url_path='')


@app.route('/')
def home():
    print("return index.html")
    return app.send_static_file('index.html')


@app.route('/initGame', methods=['POST'])
def init_game():
    return ""

@app.route('/test', methods=['GET'])
def test():
    return "test string"

@app.route('/get_next_recipe', methods=['GET'])
def get_next_recipe():
    optimizer = Optimizer('personal_food_computer')

    #TODO get parameters from GET request and make variable "arg"
    #arg = request.args.get()
    search_func = 'default_func'
    arg = request.args
    if 'search_func' in arg:
        search_func = arg['search_func']
    else:
        print('search_func is not defined')
    recipe_obj = optimizer.get_next_recipe(search_func=search_func, arg=arg)
    return jsonify(recipe_obj)



'''
@app.route('/echo/<thing>')
def echo(thing):
    return thing
'''
app.run(host='0.0.0.0', port=8000, debug=True)
