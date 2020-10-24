
import os
import boto3
from boto3.dynamodb.conditions import Key
import uuid
import json
import time
import arrow,datetime
import random
import urllib.parse

#ここでデータベースを作る必要がなくなったのでデータは無い

#DynamoDBへの接続を取得する。
def _get_database():
    endpoint = os.environ.get("DB_ENDPOINT")
    if endpoint:
        return boto3.resource("dynamodb",endpoint_url=endpoint)
        print("endpointあります！！")
    else:
        return boto3.resource("dynamodb")

def _get_ramdom_number(size,done_list):
    output_number = 0
    limit_sign = 0
    for num in range(size):
        if len(done_list) == size:
            print("すべて成し遂げました！")
            break
        random_number =random.randint(1,size)
        if not str(random_number in done_list):
            output_number = random_number
            print(done_list)
            break
    return output_number

def get_all_tables():
    table = _get_database().Table(os.environ['DB_TABLE_NAME'])
    response = table.scan()
    print(response['Items'])
    return response['Items']

def get_all_tablename():
    table = _get_database().Table(os.environ['DB_TABLE_NAME'])
    response = table.scan()
    response_item = response['Items']
    output_list = []
    for part in response_item:
        name_tid_list={"table_name":part['table_name'],"tid":part['tid']}
        print(name_tid_list,type(name_tid_list))
        output_list.append(name_tid_list)
    output_list.append({"table_length":len(response_item)})

    return output_list

def _get_all_tid():
    table = _get_database().Table(os.environ['DB_TABLE_NAME'])
    response = table.scan()
    response_item = response['Items']
    output_list = []
    for part in response_item:
        output_list.append(int(part['tid']))

    return output_list

def get_table_detail(name_or_tid):
    #at first, this will search the table by name
    table = _get_database().Table(os.environ['DB_TABLE_NAME'])
    fe=Key("table_name").eq(name_or_tid);
    response = table.scan(
            FilterExpression=fe
            )
    if response['Items'] == []:
        fe2 = Key("tid").eq(name_or_tid);
        response = table.scan(
                FilterExpression = fe2
                )
        return response['Items']
    else:
        return response['Items']

def create_table(name,length,graphrow,setting):
    if "tags" in setting.keys():
        tags = setting['tags']
    else:
        tags = []
    table = _get_database().Table(os.environ['DB_TABLE_NAME'])
    put_table={}
    try:
        name = urllib.parse.unquote(name)
    except:
        print("デコードできませんでした")
    tid_list = _get_all_tid()
    print("今存在するtidは以下です\n",tid_list)
    x = 1
    num = 1
    while(x == 1):
        if not num in tid_list:
            tid = num
            break
        else:
            num += 1
    print("今回使うtidは以下です\n",num)
    put_table['tid'] = str(tid)
    put_table['len'] = int(length)
    put_table['done'] = []
    put_table['alldone_times'] = 0
    put_table['table_name'] = name
    put_table['detail'] = []
    put_table['graphrow'] = graphrow 
    put_table['row_desplay'] = []
    put_table['tags'] = tags
    table.put_item(Item=put_table)
    return put_table

#todoを消す
def delete_table(tid):
    table = _get_database().Table(os.environ['DB_TABLE_NAME'])
    
    #データを削除する
    result = table.delete_item(
            Key={
                'tid':tid,
                },
            ReturnValues='ALL_OLD'
            )
    return result['Attributes']

def recoad_progress_to_table(name,tid):
    table = _get_database().Table(os.environ['DB_TABLE_NAME'])
    fe = Key("tid").eq(tid);
    response = table.scan(
            FilterExpression = fe
            )
    response_item = response['Items']
    exist_check = 0
    for table_list in response_item:
        if table_list['tid'] == str(tid):
            response_item = table_list
            exist_check += 1
    if exist_check == 0:
        print("選択したtidが存在しません")
        return "tidalart"
    if exist_check >1 :
        print("おかしい計算がされています")
    #入力するものが数字か特定の文字かを判断します。
    print(type(response_item['len']))
    try:
        ident = int(response_item['len'])
        if 0 < int(name) and int(name) <= response_item['len']:
            pass
        else:
            print("指定外の数字です")
            return("error")
    except:
        print("入力するものが文字です")
        #まだ未実装#
    #これはリスト型
    response_detail = response_item['detail']
    detail_times_list = []
    for detail_part in response_detail:
        if name == detail_part['name']:
            detail_times_list.append(detail_part['times'])
    print(detail_times_list)
    #print(max(detail_times_list))
    append_detail_dic = {}
    #detail部分
    done_times = 0
    if detail_times_list == []:
        print("今回が初めてです")
        append_detail_dic['date'] = str(arrow.now().to("Asia/Tokyo"))
        append_detail_dic['name'] = name
        append_detail_dic['times'] = 1
        done_times = 0
        response_item["detail"].append(append_detail_dic)
    #    print(response_detail)
    else: 
        maxtimes = 1 + max(detail_times_list)
        append_detail_dic['date'] = str(arrow.now().to("Asia/Tokyo"))
        append_detail_dic['name'] = name
        append_detail_dic['times'] = maxtimes
        done_times = maxtimes - 1 
        response_item["detail"].append(append_detail_dic)
    #    print(response_detail)
    #ここからdone部分
    if response_item['alldone_times'] == done_times:
        response_item['done'].append(name)
    if len(response_item['done']) == response_item['len']:
        response_item['alldone_times'] += 1
        done_append_list=[]
        for part in response_item['detail']:
            if part['times'] == response_item['alldone_times'] + 1: 
                done_append_list.append(str(part['name']))
        response_item['done'] = done_append_list
    #print(response_item)
    table.put_item(Item=response_item)
    return response_item


def remove_progress_to_table(name,tid):
    table = _get_database().Table(os.environ['DB_TABLE_NAME'])
    fe = Key("tid").eq(tid);
    response = table.scan(
            FilterExpression = fe
            )
    response_item = response['Items']
    exist_check = 0
    for table_list in response_item:
        if table_list['tid'] == str(tid):
            response_item = table_list
            exist_check += 1
    if exist_check == 0:
        print("選択したtidが存在しません")
        return "tidalart"
    if exist_check >1 :
        print("おかしい計算がされています")
    #入力するものが数字か特定の文字かを判断します。
    print(type(response_item['len']))
    try:
        ident = int(response_item['len'])
        if 0 < int(name) and int(name) <= response_item['len']:
            pass
        else:
            print("指定外の数字です")
            return("error")
    except:
        print("入力するものが文字です")
        #まだ未実装#
    #これはリスト型
    response_detail = response_item['detail']
    detail_times_list = []
    for detail_part in response_detail:
        if name == detail_part['name']:
            detail_times_list.append(detail_part['times'])
    print(detail_times_list)
    #print(max(detail_times_list))
    append_detail_dic = {}
    #detail部分
    done_times = 0
    if detail_times_list == []:
        print("今回が初めてですなので削除するものがありません")
        return('error')
    else: 
        for part in response_item['detail']:
            #print(part)
            print(max(detail_times_list),part['times'],name,part['name'])
            if max(detail_times_list) == part['times'] and name == part['name']:
                print(part)
                remove_done = part['times']
                remove_done_name = part['name']
                response_item["detail"].remove(part)
        if int(remove_done) == response_item["alldone_times"] + 1:
            print(remove_done,response_item['done'])
            response_item['done'].remove(str(remove_done_name))
        elif int(remove_done) == response_item["alldone_times"]:
            done_list = []
            response_item['alldone_times'] -= 1
            try:
                ident = int(response_item['len'])
            except:
                print("入力するものが文字です")
            for num in range(ident):
                if not str(num+1) == remove_done_name:
                    done_list.append(str(num+1))
            response_item['done'] = done_list
            

    #print(response_item)
    table.put_item(Item=response_item)
    return response_item

def get_random_parameter(tid):
    detail = get_table_detail(tid)
    #print(detail[0])
    #print(detail[0]['len'])
    #print(detail[0]['done'])
    return _get_ramdom_number(int(detail[0]['len']),detail[0]['done'])    


def change_setting_table(tid,data):
    print(data['name'])
    if not data['name'] == "":
        updatepass_name = 1
    else:
        updatepass_name = 0 
    
    table = _get_database().Table(os.environ['DB_TABLE_NAME'])
    if updatepass_name == 1:
        responce = table.update_item(
            ExpressionAttributeValues={
                ':n':data['name'],
                ':r':{
                    'L':data['rowdesplay'],
                    },
                ':t':data['tags'],
                },
            Key ={
                'tid':str(tid)
                },
            ReturnValues="ALL_NEW",
            TableName=os.environ['DB_TABLE_NAME'],
            UpdateExpression="SET table_name=:n,row_desplay=:r,tags=:t",
            )
    else:
        response = table.update_item(
            ExpressionAttributeValues={
                ':r':{
                    'L':data['rowdesplay'],
                    },
                ':t':data['tags'],
                },
            Key ={
                'tid':str(tid)
                },
            ReturnValues="ALL_NEW",
            TableName=os.environ['DB_TABLE_NAME'],
            UpdateExpression="SET row_desplay=:r,tags=:t",
            )
    return(response['Attributes'])

    


if __name__ == "__main__":
    
    data = [1,4,7]
    print(_get_ramdom_number(10,data))


































































































