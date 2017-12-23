import time

class Optimizer:
    def __init__(self, growth_id):
        self.growth_id = growth_id
        print('init')

    def optimize(self):
        return 0

    def get_next_step(self):
        temp_test_json = { "air_temperature": [
            {"start_time": 0, "end_time": 0.1, "value": time.time()},
            {"start_time": 0.1, "end_time": 0.2, "value": 21}]
        }
        return temp_test_json

