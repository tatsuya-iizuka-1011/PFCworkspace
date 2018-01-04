import time
from recipe_vector import RecipeVector


class Optimizer:
    def __init__(self, growth_id):
        self.growth_id = growth_id

    def optimize(self):
        return 0

    def get_next_step(self, search_func, arg):
        search_funcs = {
            'day_duration_search':self.day_duration_search
        }
        if search_func not in search_funcs:
            # TODO write erorr process
            a = search_funcs['day_duration_search'](arg)
        a = search_funcs[search_func](arg)
        rv = RecipeVector(a)
        step_obj = rv.make_step_obj()
        return step_obj
    def day_duration_search(self, arg):
        next_phase = 0
        if 'next_phase' in arg:
            next_phase = int(arg['next_phase'])
        day_duration = min(24, 12+next_phase*4)
        a = {
            'cycle_duration':24,
            'day_duration':day_duration,
            'light_intensity_white':[1,0],
            'air_temperature':[26, 23],
            'air_flush':[2, 2],
            'water_potential_hydrogen':[6.0, 6.0],
            'nutrient_flora_duo_a':[0],
            'nutrient_flora_duo_b':[0]
        }
        return a

    def make_recipe_obj_from_step(self, next_step):
        recipe_id = 'test'
        phase_cycle = 1
        phase_duration = 24
        update_interval = phase_duration * 0.9
        step_name = 'selected_by_optimizer'
        recipe_obj = {
            'phase':{
                'name': step_name,
                'cycles': phase_cycle,
                'time_units' : 'hours',
                'step':next_step
            },
            'update_interval_value':update_interval,
            'phase_duration':phase_duration
        }
        return recipe_obj

    def get_next_recipe(self, search_func, arg):
        next_step = self.get_next_step(search_func=search_func, arg=arg)
        recipe_obj = self.make_recipe_obj_from_step(next_step)
        return recipe_obj

