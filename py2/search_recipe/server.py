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

@app.route('/get_next_recipe')
def get_next_step():
    optimizer = Optimizer('personal_food_computer')
    next_step = optimizer.get_next_step()
    recipe_id = 'test'
    update_interval = 0.2
    phase_cycle = 1
    step_name = 'selected_by_optimizer'

    recipe_doc = {
        '_id':recipe_id,
        'update':True,
        'update_interval':update_interval,
        'time_units':'hours',
        'format':'flexformat',
        'phases':[
            {
                'name': step_name,
                'cycles': phase_cycle,
                'time_units' : 'hours',
                'step':next_step
            }
        ]
    }
    recipe_obj = {
        'phase':{
            'name': step_name,
            'cycles': phase_cycle,
            'time_units' : 'hours',
            'step':next_step
        },
        'update_interval_value':update_interval,
        'phase_duration':0.2
    }
    return jsonify(recipe_obj)



'''
@app.route('/echo/<thing>')
def echo(thing):
    return thing
'''
app.run(host='0.0.0.0', port=8000, debug=True)
