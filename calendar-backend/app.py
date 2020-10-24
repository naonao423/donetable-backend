from chalice import Chalice,NotFoundError,BadRequestError
from chalicelib import database

app = Chalice(app_name='calendar-backend')

@app.route('/events',cors=True)
def load_all_events():
    return  database.load_all_events()

@app.route('/events/reload',methods=['POST'],cors=True)
def reload_events():
    add_list,amount_of_item,amount_of_change,amount_of_already_exist,worktime = database.reload_event()
    send_json =[{"number of items":amount_of_item},
            {"number of successful update":amount_of_change},
            {"number of already exist":amount_of_already_exist},
            {"worktime":worktime}
            ]
    send_json.append(add_list)
    return send_json

@app.route('/events/update',methods=['POST'],cors=True)
def reload_events():
    add_list,amount_of_item,amount_of_change,amount_of_already_exist,worktime = database.update_event()
    send_json =[{"number of items":amount_of_item},
            {"number of successful delete":amount_of_change},
            {"number of exist":amount_of_already_exist},
            {"worktime":worktime}
            ]
    send_json.append(add_list)
    return send_json

@app.route('/events/lists',methods=['GET'],cors=True)
def get_all_events():
    return database.get_all_events()

@app.route('/events/otherlists/{start}/{stop}',methods=['GET'],cors=True)
def get_others_list(start,stop):
    return database.get_others_list(start,stop)

@app.route('/events/summary/{start}/{stop}',methods = ['GET'],cors=True)
def get_summary_of_events(start,stop):
    return database.get_summary_of_events(start,stop)


@app.route('/events/datescale/{start}/{stop}',methods = ['GET'],cors=True)
def get_summary_of_events(start,stop):
    return database.get_datescale_of_events(start,stop)

@app.route('/events/setsub',methods = ['GET'],cors=True)
def get_setting_subject():
    return database.get_setting_subject()

@app.route('/events/setgoal',methods = ['GET'],cors=True)
def get_setting_goal():
    return database.get_setting_goal()

@app.route('/events/setting',methods = ['GET'],cors=True)
def get_setting():
    return database.get_setting()

@app.route('/events/setting_change/{data}',methods = ['PUT'],cors=True)
def get_setting(data):
    return database.change_setting(data)

@app.route('/events/setting-raw',methods = ['GET'],cors=True)
def get_setting_raw():
    return database.setting_raw()

@app.route('/events/datescaleaverage/{start}/{stop}',methods = ['GET'],cors=True)
def get_datescale_of_events_average(start,stop):
    return database.get_datescale_of_events_average(start,stop)
