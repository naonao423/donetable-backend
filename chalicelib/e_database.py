#internalpackageを消しています
import os
import boto3
from boto3.dynamodb.conditions import Key
import uuid
import json
import time
import arrow,datetime
import random

#ここでデータベースを作る必要がなくなったのでデータは無い

#DynamoDBへの接続を取得する。
def _get_database():
    endpoint = os.environ.get("DB_ENDPOINT")
    if endpoint:
        return boto3.resource("dynamodb",endpoint_url=endpoint)
        print("endpointあります！！")
    else:
        return boto3.resource("dynamodb")

def _get_ramdom_number(size,data):
    output_number = 0
    limit_sign = 0
    for n in range(10000):
        for num in range(size):
            random_number =random.randint(1,size)
            if not random_number in data:
                output_number = random_number
                data.append(random_number)
                print(data)
                break
        if len(data) == size:
            print("すべて成し遂げました！")
            break
    return output_number

if __name__ == "__main__":
    data = [1,4,7]
    print(_get_ramdom_number(100,data))

