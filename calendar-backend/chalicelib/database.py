import os
import boto3
from boto3.dynamodb.conditions import Key
import uuid
import json
import time
from internalpackage import botocal
import arrow,datetime

#ここでデータベースを作る必要がなくなったのでデータは無い

#DynamoDBへの接続を取得する。
def _get_database():
    endpoint = os.environ.get("DB_ENDPOINT")
    if endpoint:
        return boto3.resource("dynamodb",endpoint_url=endpoint)
        print("endpointあります！！")
    else:
        return boto3.resource("dynamodb")

#すべてのレコードを取得する
def load_all_events():
    #table = _get_database().Table(os.environ["DB_TABLE_NAME"])
    #response = table.scan()
    #return response['Items']

    #cwd = os.getcwd()
    #datapath = os.path.join(cwd,'data.json')
    #with open(datapath) as file:
    #    return json.load(file)
    return botocal.Get_cal().assign_to_dics()

def reload_event():
    start = time.time()
    table = _get_database().Table(os.environ["DB_TABLE_NAME"])
    response = table.scan()
    #ここのタイプはおそらくリスト
    exist_item_list = response["Items"]
    #これもおそらくリスト
    new_item_list = botocal.Get_cal().assign_to_dics()
    amount_of_already_exist = 0
    amount_of_change = 0
    check_exist = 0
    add_list = []
    for put_part in new_item_list:
        #書き込みたいファイルのuidを定義
        put_uid = put_part["uid"]
        for exist_part in exist_item_list:
            exist_uid = exist_part['uid']

            #データが存在するか
            if put_uid == exist_uid:
                amount_of_already_exist += 1
                check_exist = 1
            #存在しないなら追加
                
        if check_exist == 0:
            table.put_item(Item=put_part)
            add_list.append(put_part)
            amount_of_change +=1
        check_exist = 0        
    end = time.time()
    return add_list,len(new_item_list),amount_of_change,amount_of_already_exist,end-start

def update_event():
    start = time.time()
    table = _get_database().Table(os.environ["DB_TABLE_NAME"])
    response = table.scan()
    #ここのタイプはおそらくリスト
    exist_item_list = response["Items"]
    #これもおそらくリスト
    new_item_list = botocal.Get_cal().assign_to_dics()
    amount_of_already_exist = 0 
    amount_of_update = 0
    check_exist = 0
    add_list = []
    for exist_part in exist_item_list:
        #書き込みたいファイルのuidを定義
        exist_uid = exist_part['uid']
        for put_part in new_item_list:
            put_uid = put_part["uid"]

            #データが存在するか
            if put_uid == exist_uid:
                amount_of_already_exist += 1
                check_exist = 1
            elif exist_uid == "setting":
                check_exist = 1
                
            #存在しないなら追加
                
        if check_exist == 0:
            result = table.delete_item(
                    Key={
                        "uid":exist_uid,
                        },
                    ReturnValues="ALL_OLD"
                    )
            add_list.append(exist_part)
            amount_of_update +=1
        check_exist = 0 
    end = time.time()
    return add_list,len(new_item_list),amount_of_update,amount_of_already_exist,end-start

def get_all_events():
    table = _get_database().Table(os.environ["DB_TABLE_NAME"])
    response = table.scan()
    return response['Items']
    
def get_others_list(start,stop):
    start_time = str(arrow.now().shift(days=-1))
    stop_time = str(arrow.get(stop).shift(years=2))
    print(start_time,stop_time)
    table = _get_database().Table(os.environ["DB_TABLE_NAME"])
    fe = Key('begin_time').between(start_time,stop_time);
    response = table.scan(
                        FilterExpression=fe
                                    )
    output_dic = response['Items']
    #sublist=["Nap","Programing","English","Study","Meditation","Stretch","英単語","Reading"]
    #sublistの設定をinitial_data.jsonから読みとる。
    subkey = Key('uid').eq("setting");
    sublist = table.scan(
            FilterExpression=subkey
            )
    sublist = sublist['Items'][0]["sub"]
    #print(sublist)
    sublist = sublist.split(";")
    print(sublist)
    summary_output_list = []
    summary_dic_name = {}
    for part in output_dic:
        #settingは無視するようにする。
        if part["uid"] == "setting":
            pass
        else:
            if part['sub'] == "Programming":
                name = "Programing"
            else:
                name = part['sub']
        if not name in sublist:
            print(part['duration'],len(part['duration']))
            if len(part['duration']) > 10:
                pass
            else:
                part["begin"] = part["begin_time"]
                part["begin_date"] = part["begin"].split("T")[0]
                sl = part["duration"].split(":")
                part["begin_time"] = part["begin"].split("T")[1].split("+")[0]
                part["end_time"] = str(arrow.get(part["begin"]).shift(hours=int(sl[0]),minutes=int(sl[1]),seconds=int(sl[2]))).split("T")[1].split("+")[0]
                part["time_duration"] = part["begin_time"] + "～" + part["end_time"]
                summary_output_list.append(part)
            
    summary_output_list.sort(key=lambda x: x['begin'],reverse=False)
        
    return summary_output_list

def get_summary_of_events(start,stop):
    #start_time = str(arrow.get(start))
    #stop_time = str(arrow.get(stop))
    start_time = str(arrow.get(start).shift(days=1))
    stop_time = str(arrow.get(stop).shift(days=1))
    print(start_time,stop_time)
    table = _get_database().Table(os.environ["DB_TABLE_NAME"])
    fe = Key('begin_time').between(start_time,stop_time);
    response = table.scan(
                        FilterExpression=fe
                                    )
    output_dic = response['Items']
    #sublist=["Nap","Programing","English","Study","Meditation","Stretch","英単語","Reading"]
    #sublistの設定をinitial_data.jsonから読みとる。
    subkey = Key('uid').eq("setting");
    sublist = table.scan(
            FilterExpression=subkey
            )
    sublist = sublist['Items'][0]["sub"]
    print(sublist)
    sublist = sublist.split(";")
    print(sublist)
    summary_output_list = []
    summary_dic_name = {}
    for subject in sublist:
        summary_dic = {"hour":0,"minute":0,"second":0}
        if subject == "Others":
            for part in output_dic:
                #settingは無視するようにする。
                if part["uid"] == "setting":
                    pass
                else:
                    if part['sub'] == "Programming":
                        name = "Programing"
                    else:
                        name = part['sub']
                    if not name in sublist:
                        print(part['duration'])
                        if len(part['duration']) > 1:
                            pass
                        else:
                            duration = part['duration'].split(',')[-1]
                            (hour,minute,second) = duration.split(":")
                            summary_dic['hour'] += int(hour)
                            summary_dic['minute'] += int(minute)
                            summary_dic['second'] += int(second)
                            if summary_dic['second'] >= 60:
                                summary_dic['second'] -=60
                                summary_dic['minute'] += 1
                            if summary_dic['minute'] >= 60:
                                summary_dic['minute'] -=60
                                summary_dic['hour'] += 1
                #settingは無視するようにする。
        else:
            for part in output_dic:
                if part["uid"] == "setting":
                    pass
                else:
                    if part['sub'] == "Programming":
                        name = "Programing"
                    else:
                        name = part['sub']
                    if name == subject:
                        duration = part['duration'].split(',')[-1]
                        (hour,minute,second) = duration.split(":")
                        summary_dic['hour'] += int(hour)
                        summary_dic['minute'] += int(minute)
                        summary_dic['second'] += int(second)
                        if summary_dic['second'] >= 60:
                            summary_dic['second'] -=60
                            summary_dic['minute'] += 1
                        if summary_dic['minute'] >= 60:
                            summary_dic['minute'] -=60
                            summary_dic['hour'] += 1
        summary_dic_name[subject] = summary_dic
    #summary_output_list.append(summary_dic_name)
    #return summary_output_list
    return summary_dic_name
        
    
def get_datescale_of_events(start,stop):
    #start_time = (arrow.get(start))
    start = (arrow.get(start))
    #stop_time = (arrow.get(stop))
    stop = (arrow.get(stop))
    start_time = arrow.get(start).shift(days=1)
    stop_time = arrow.get(stop).shift(days=1)
    ident = int(str(start_time-stop_time).split(" ")[0])
    time_list = []
    if ident < 0:
        print('時間を一日ごとに分けます')
        k = 1
        while(k <=3):
            time_list.append(str(start_time))
            print(start_time)
            start_time = start_time.shift(days=1)
            if start_time == stop_time :
                k += 1
            elif k != 1:
                k += 1
    print(time_list)
    len_time_list = len(time_list)
    date_scale_dic = {}
    output_dic =[]
    table = _get_database().Table(os.environ["DB_TABLE_NAME"])
    fe = Key('begin_time').between(str(start),str(stop.shift(days=+2)));
    response = table.scan(
                        FilterExpression=fe
                                    )
    
    output_dic = response['Items']
    subkey = Key('uid').eq("setting");
    sublist = table.scan(
            FilterExpression=subkey
            )
    sublist = sublist['Items'][0]["sub"]
    sublist = sublist.split(";")
    for num in range(len_time_list-1):            
        #sublist=["Nap","Programing","English","Study","Meditation","Stretch","英単語","Reading"]
        #sublistの設定をinitial_data.jsonから読みとる。
        summary_output_list = []
        summary_dic_name = {}
        for subject in sublist:
            summary_dic = {"minute":0}
            for part in output_dic:
                #settingは無視するようにする。
                if part["uid"] == "setting":
                    pass
                else:
                    if part['sub'] == "Programming":
                        name = "Programing"
                    else:
                        name = part['sub']
                    if name == subject and part['begin_time'].split("T")[0] == time_list[num].split("T")[0]:
                        duration = part['duration'].split(',')[-1]
                        (hour,minute,second) = duration.split(":")
                        summary_dic['minute'] += (int(hour)*60 + int(minute) + int(second)/60)
            summary_dic_name[subject] = summary_dic
        date_scale_dic[time_list[num]] = summary_dic_name
    #summary_output_list.append(summary_dic_name)
    #return summary_output_list
    return date_scale_dic

def get_datescale_of_events_average(start,stop):
    start_time = arrow.get(start).shift(days=1)
    stop_time = arrow.get(stop).shift(days=1)
    #start_time = (arrow.get(start))
    start = (arrow.get(start))
    #stop_time = (arrow.get(stop))
    start_time_before_a_week = start_time.shift(days=-7)
    print(start_time,stop_time)
    print(start_time_before_a_week)
    stop = (arrow.get(stop))
    day_list = []
    days = start_time_before_a_week
    for num in range(100):
        day_list.append(days)
        if days == stop_time:
           break 
        days = days.shift(days=+1)
    print(day_list)


    len_day_list = len(day_list)
    date_scale_dic = {}
    output_dic =[]
    for num in range(len_day_list-7):
        output_dic.append(str(day_list[num+7]))
    print(output_dic)
    len_output_dic = len(output_dic)


    table = _get_database().Table(os.environ["DB_TABLE_NAME"])
    fe = Key('begin_time').between(str(start_time_before_a_week),str(stop_time));
    response = table.scan(
                        FilterExpression=fe
                                    ) 
    get_dic = response['Items']
    subkey = Key('uid').eq("setting");
    sublist = table.scan(
            FilterExpression=subkey
            )
    sublist = sublist['Items'][0]["sub"]
    sublist = sublist.split(";")
    get_scale_dic = {}
    for num in range(len_output_dic):            
        #sublist=["Nap","Programing","English","Study","Meditation","Stretch","英単語","Reading"]
        #sublistの設定をinitial_data.jsonから読みとる。
        summary_output_list = []
        summary_dic_name = {}
        for subject in sublist:
            summary_dic = {"minute":0}
            for part in get_dic:
                #settingは無視するようにする。
                if part["uid"] == "setting":
                    pass
                else:
                    if part['sub'] == "Programming":
                        name = "Programing"
                    else:
                        name = part['sub']
                    identification = str(arrow.get(part['begin_time'].split("T")[0]) - arrow.get(str(day_list[num]).split("T")[0])).split(' ')
                    if len(identification) == 1:
                        identification = 0
                    else:
                        identification = int(identification[0])
                    #print(identification)
                    if name == subject and 0 <= identification and identification <= 7:
                        duration = part['duration'].split(',')[-1]
                        (hour,minute,second) = duration.split(":")
                        summary_dic['minute'] += (int(hour)*60 + int(minute) + int(second)/60)/7
            summary_dic_name[subject] = summary_dic
        print(output_dic[num])
        get_scale_dic[output_dic[num]] = summary_dic_name
    return get_scale_dic


def get_setting_subject():
    table = _get_database().Table(os.environ["DB_TABLE_NAME"])
    fe = Key('uid').eq("setting");
    response = table.scan(
                        FilterExpression=fe
                                    )
    output_dic = response['Items'][0]["sub"]
    if type(output_dic) == dict:
        output_dic = output_dic['S']
    output_dic1 = output_dic.split(";")
    return output_dic1

def get_setting_goal():
    table = _get_database().Table(os.environ["DB_TABLE_NAME"])
    fe = Key('uid').eq("setting");
    response = table.scan(
                        FilterExpression=fe
                                    )
    output_dic = response['Items'][0]["begin_time"]
    if type(output_dic) == dict:
        output_dic = output_dic['S']
    output_dic1 = output_dic.split(";")
    return output_dic1

def get_setting():
    return_list = []
    table = _get_database().Table(os.environ["DB_TABLE_NAME"])
    fe = Key('uid').eq("setting");
    response = table.scan(
                        FilterExpression=fe
                                    )
    output_dic_sub = response['Items'][0]["sub"]
    output_dic_goal = response['Items'][0]["begin_time"]
    if type(output_dic_goal) == dict:
        output_dic_goal = output_dic_goal['S']
    if type(output_dic_sub) == dict:
        output_dic_sub= output_dic_goal['S']
    print(output_dic_goal,type(output_dic_goal))
    output_dic_sub1 = output_dic_sub.split(";")
    output_dic_goal1 = output_dic_goal.split(";")
    for num in range(len(output_dic_sub1)):
        combine_dic = {}
        combine_dic['sub'] = output_dic_sub1[num]
        combine_dic['goal'] = output_dic_goal1[num]
        return_list.append(combine_dic)
    return return_list

def change_setting(data):
    table = _get_database().Table(os.environ["DB_TABLE_NAME"])
    #fe = Key('uid').eq("setting");
    #response = table.scan(
    #                    FilterExpression=fe
    #                                )
    #output_dic = response['Items'][0]["sub"]
    
    print(data,type(data))
    #output_dic1 = output_dic.split(";")
    response = table.update_item(
    ExpressionAttributeValues={
        ':t': data
    },
    Key={
        'uid':'setting'
    },
    ReturnValues='ALL_NEW',
    TableName='Events',
    UpdateExpression='SET begin_time = :t',
    )

    print(response['Attributes'])


def setting_raw():
    table = _get_database().Table(os.environ["DB_TABLE_NAME"])
    fe = Key('uid').eq("setting");
    response = table.scan(
                        FilterExpression=fe
                                    )
    return response['Items']









#指定されたIDのレコードを取得する。
#def get_todo(todo_id):
#    table = _get_database().Table(os.environ["DB_TABLE_NAME"])
#    response = table.query(
#            KeyConditionExpression = Key('id').eq(todo_id)
#            )
#    items = response['Items']
#    return items[0] if items else None
#         
##Todoを作成する。
#def create_todo(todo):
#    #登録内容を作成する
#    item ={
#            'id':uuid.uuid4().hex,
#            'title':todo['title'],
#            'memo':todo['memo'],
#            'priority':todo['priority'],
#            'completed':False,
#            }
#    #登録内容をDynamoDBに登録する。
#    table = _get_database().Table(os.environ['DB_TABLE_NAME'])
#    table.put_item(Item=item)
#    return item
#           
##データを更新する
#def update_todo(todo_id,changes):
#    table = _get_database().Table(os.environ['DB_TABLE_NAME'])
#    #クエリを構築する(ここでは変更内容のみを保存している)
#    #list型で保存している
#    update_expression=[]
#    #辞書型で保存している
#    expression_attribute_values = {}
#    for key in ['title', 'memo', 'priority', 'completed']:
#        if key in changes:
#            update_expression.append(f"{key} = :{key[0:1]}")
#            #変化したものを変化した属性の頭文字をkeyとしてvalueに変更内容を格納する.
#            expression_attribute_values[f":{key[0:1]}"] = changes[key]
#    #こっちでtodo_idを選択してそのidに対して変更内容を適用している。
#    #DynamoDBのデータを更新する
#    result = table.update_item(
#            Key={
#                "id" : todo_id,
#                },
#            #更新したものを表示する変数
#            UpdateExpression='set '+ ','.join(update_expression),
#            ExpressionAttributeValues = expression_attribute_values,
#            ReturnValues='ALL_NEW'
#            )
#    return result['Attributes']
#
##todoを消す
#def delete_todo(todo_id):
#    table = _get_database().Table(os.environ['DB_TABLE_NAME'])
#    
#    #データを削除する
#    result = table.delete_item(
#            Key={
#                'id':todo_id,
#                },
#            ReturnValues='ALL_OLD'
#            )
#    return result['Attributes']




