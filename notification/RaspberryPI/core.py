# -*- coding utf-8 -*-
'''
PepperからのHTTPリクエストをAzureへHTTPSにして転送
'''
import sys
import time
import os
import base64
import requests

from flask import Flask, abort, jsonify, make_response, request

from azure.storage.blob import BlobServiceClient

# Azure Storage Containerの名前，接続文字列
AZURE_CONTAINER_NAME = os.getenv('CONTAINER_NAME', None)
AZURE_STORAGE_CONTAINER_CONNECTION_STRING = os.getenv('ASC_CONNECTION_STRING', None)

app = Flask(__name__)

BLOB_SERVICE_CLIENT = BlobServiceClient.from_connection_string(
    AZURE_STORAGE_CONTAINER_CONNECTION_STRING
    )

@app.route("/raspberrypi/trackid/post", methods=["POST"])
def relay_trackid_request():
    '''
    追跡番号の問い合わせをAzureへ中継
    :return:
    '''
    try:
        # PepperからのHTTPリクエスト内の"trackId"パラメータから値を取得
        # 型に注意 （文字列型で扱う）
        print(request)
        requested_trackingnumber = request.form["trackId"]
        print(requested_trackingnumber)

        #TODO:AzureへPOSTリクエストを送信
        url = 'https://porchman.azurewebsites.net/trackingnumber/get'
        
        payload = {
            "trackId":requested_trackingnumber
        }
        
        req = requests.post(url, payload)
        
        request_from_azure = req.json()
        
        
        result_value = request_from_azure["result"]
        
        print(result_value)

        # pepperへの応答
        if result_value:
            result = {
                "result":True,
            }
        else:
            result = {
                "result":True,
            }

    except Exception as except_var:
        print("except:"+except_var)
        abort(500)

    return make_response(jsonify(result))

@app.route("/raspberrypi/photo/upload", methods=["POST"])
def relay_photo_upload():
    '''
    photoをAzureへ中継
    :return:
    '''
    try:
        # PepperからのHTTPリクエスト内の"image"パラメータから値を取得
        # 型に注意 （文字列型で扱う）
        print(request)
        
        img = base64.b64decode(request.form["image"].encode())
        
        

        # ファイル名（エポックタイム.jpg）
        local_file_name = str(int(time.time())) + '.jpg'

        blob_client = BLOB_SERVICE_CLIENT.get_blob_client(
            container=AZURE_CONTAINER_NAME,
            blob=local_file_name
        )

        blob_client.upload_blob(img)

    except Exception as except_var:
        print("except:"+except_var)
        abort(500)

    return 'OK' # HTTPコード 200をとりあえず返す

if __name__ == "__main__":
    print("running porchman")
    args = sys.argv
    # コマンドライン引数があるか確認
    if len(args) > 1:
        host = args[1]
    else:
        host = "localhost"

    PORT = int(os.getenv("PORT", 5000))
    app.run(host=host, port=PORT)