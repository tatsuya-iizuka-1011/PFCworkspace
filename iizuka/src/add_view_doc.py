import sys
import couchdb

if __name__ == '__main__':
    pfc_id = sys.argv[1]
    foocomputer_str = 'foodcomputer'
    if pfc_id is not None:
        foocomputer_str += pfc_id
    server_address = 'http://{}.akg.t.u-tokyo.ac.jp'.format(foocomputer_str)
    port = 5984
    db_name = 'environmental_data_point'
    view_id = 'openag/by_variable'

    server = couchdb.Server('{}:{}/'.format(server_address, port))
    db = server[db_name]

    map_fun = '''
    function(doc) {
        var recipe_var_types = [
            'recipe_start',
            'recipe_end',
            'recipe_update'
        ]
        if(recipe_var_types.indexOf(doc.variable) == -1){
            return;
        }
        if (doc.is_desired) {
            point_type = 'desired';
        }
        else {
            point_type = 'measured';
        }
        emit([doc.environment, point_type, doc.variable, doc.timestamp], doc);
    }
    '''
    doc = db['_design/openag']
    map_dict = {'map':map_fun}
    doc['views']['recipe_vars'] = map_dict
    db[doc['_id']] = doc
