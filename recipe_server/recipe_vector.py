class RecipeVector():
    def __init__(self, recipe_vector):
        self.recipe_vector = recipe_vector
        self.recipe_env_variables = set((
            'light_intensity_white', 'air_temperature', 'water_potential_hydrogen',
            'air_flush', 'nutrient_flora_duo_a', 'nutrient_flora_duo_b'))
        self.recipe_time_variables = set(('cycle_duration', 'day_duration'))
        self.raw_value_envs =  set(('light_intensity_white', 'air_temperature', 'water_potential_hydrogen'))
        self.interval_value_envs = {'air_flush':0.25}
        self.nutrients_rate = {'nutrient_flora_duo_a':400, 'nutrient_flora_duo_b':400}
        self.prop = {}
        self.prop['start'] = 'start_time'
        self.prop['end'] = 'end_time'
        self.prop['value'] = 'value'

        if not self.validate_vector():
            print('recipe_vector is not validated')
            return None

    def validate_vector(self):
        for env_var in self.recipe_env_variables:
            if env_var in self.recipe_vector and type(self.recipe_vector[env_var]) == list:
                list_length = 2
                if env_var == 'nutrient_flora_duo_a' or env_var == 'nutrient_flora_duo_b':
                    list_length = 1
                if len(self.recipe_vector[env_var]) != list_length:
                    return False
            else:
                return False
        return True

    def make_step_obj(self):
        step_obj = {}
        a = self.recipe_vector
        start, end, value = (self.prop['start'], self.prop['end'], self.prop['value'] )

        for env_variable in self.raw_value_envs:
            step_obj[env_variable] = [
                {start:0, end:a['day_duration'], value:a[env_variable][0]},
                {start:a['day_duration'], end:a['cycle_duration'], value:a[env_variable][1]}
            ]
        for nutirent, doser_rate in self.nutrients_rate.iteritems():
            doser_duration = a[nutirent][0] / doser_rate
            step_obj[nutirent] = [
                {start:0, end:doser_duration, value:doser_rate},
                {start:doser_duration, end:a['cycle_duration'], value:0}
            ]
        for env_variable, operating_time in self.interval_value_envs.iteritems():
            step_obj[env_variable] = []
            for i in range(2):
                if operating_time > a[env_variable][i]:
                    print('value of interval_value_envs must be more than operating_time')
                    return None
                start_time, end_time, duration = (-operating_time, 0, a['day_duration'])
                if i ==1:
                    start_time += a['day_duration']
                    end_time += a['day_duration']
                    duration = a['cycle_duration'] - a['day_duration']
                num_cycle_day = int(duration // a[env_variable][i])
                for j in range(num_cycle_day):
                    start_time += a[env_variable][i]
                    end_time += a[env_variable][i]
                    step_obj[env_variable] .append({start:start_time, end:end_time, value:1})
        return step_obj
    