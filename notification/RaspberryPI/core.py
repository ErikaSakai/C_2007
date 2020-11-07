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
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, ImageMessage
)

# Azure Storage Containerの名前，接続文字列
AZURE_CONTAINER_NAME = os.getenv('CONTAINER_NAME', None)
AZURE_STORAGE_CONTAINER_CONNECTION_STRING = os.getenv('ASC_CONNECTION_STRING', None)

# LINE Messaging API
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', None)
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
LINE_BOT_API = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
HANDLER = WebhookHandler(LINE_CHANNEL_SECRET)
app = Flask(__name__)

BLOB_SERVICE_CLIENT = BlobServiceClient.from_connection_string(
    AZURE_STORAGE_CONTAINER_CONNECTION_STRING
    )

MAIN_IMAGE_PATH = os.getenv('MAIN_IMAGE_PATH', None)

USERID = os.getenv('LINE_USER_ID', None)

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

        # LINE送信
        send_image_one_side(local_file_name)

    except Exception as except_var:
        print("except:"+except_var)
        abort(500)

    return 'OK' # HTTPコード 200をとりあえず返す

def send_image_one_side(filename):
    # lest_file_name = get_lest_filename_on_azure()

    print(MAIN_IMAGE_PATH + filename)
    # 画像の送信(originalとpreviewは同じ画像)
    image_message = ImageSendMessage(
        original_content_url=MAIN_IMAGE_PATH + filename,
        preview_image_url=MAIN_IMAGE_PATH + filename
    )

    LINE_BOT_API.push_message(USERID,image_message)

    return

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