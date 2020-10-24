from chalice import Chalice,NotFoundError,BadRequestError
from chalicelib import database

app = Chalice(app_name='donetable-backend')

@app.route('/donetable',cors=True)
def load_all_events():
    return  database.get_all_tables()

@app.route('/donetable/name',cors=True)
def load_all_events():
    return  database.get_all_tablename()

@app.route('/donetable/tid',cors=True)
def load_all_tid():
    return  database._get_all_tid()

@app.route('/donetable/create/{name}/{length}/{graphrow}',methods=["POST"], cors=True)
def create_table(name,length,graphrow):
    setting = app.current_request.json_body
    return  database.create_table(name,length,graphrow,setting)

@app.route('/donetable/detail/{name_or_tid}',cors=True)
def load_all_events(name_or_tid):
    return  database.get_table_detail(name_or_tid)

@app.route('/donetable/delete/{tid}',methods=['DELETE'],cors=True)
def delete_table(tid):
    return  database.delete_table(tid)

@app.route('/donetable/recoad/{tid}/{name}',methods=['PUT'],cors=True)
def recoad_progress_to_table(name,tid):
    return  database.recoad_progress_to_table(name,tid)

@app.route('/donetable/remove/{tid}/{name}',methods=['PUT'],cors=True)
def remove_progress_to_table(name,tid):
    return  database.remove_progress_to_table(name,tid)

@app.route('/donetable/random/{tid}',methods=['GET'],cors=True)
def get_random_parameter(tid):
    return  database.get_random_parameter(tid)

@app.route('/donetable/changesetting/{tid}',methods=['PUT'],cors=True)
def change_setting_table(tid):
    setting = app.current_request.json_body
    return  database.change_setting_table(tid,setting)
