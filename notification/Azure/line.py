import sys
import os
import requests
import json

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, ImageMessage
)
from azure.storage.blob import BlobServiceClient
from azure.cosmosdb.table.tableservice import TableService

# ユーザ定義モジュール
import azure

# LINEBOTAPIのURL
URL = "https://api.line.me/v2/bot/message/multicast"

# LINE Messaging API
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

main_image_path = os.getenv('MAIN_IMAGE', None)
preview_image_path = os.getenv('PREVIEW_IMAGE', None)  # ダミー

# Azure Storage Containerの名前
CONTAINER_NAME = os.getenv('CONTAINER_NAME', None)
# Azure Storage Containerの接続文字列
AZURE_STORAGE_CONTAINER_CONNECTION_STRING = os.getenv('ASC_CONNECTION_STRING', None)

# Azure Table Strageの名前，アクセスキー
STORAGE_KEY = os.getenv('AZURE_STRAGE_KEY')
STORAGE_NAME = os.getenv('AZURE_STRAGE_NAME')

AZURE_TABLENAME_TRAKINGNUMBER = 'TrackingNumber'

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
    
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

app = Flask(__name__)

# LINE APIに接続するやつ
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# Azure Table Serviceに接続するやつ
table_service = TableService(account_name=STORAGE_NAME, account_key=STORAGE_KEY)

@app.route("/callback", methods=['POST'])
def callback():
    '''
    LINEサーバへWebhookリクエストをチェック(認証)
    :return:
    '''
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    #署名を検証
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def replyMessageText(event, message: str):
    '''
    LINEメッセージを応答
    :message:応答として送信したいメッセージの文字列
    :return:
    '''
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)  # 返信メッセージ
    )

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    '''
    ユーザが送信したLINEメッセージを取得
    :return:メッセージの内容
    '''
    getMessage = event.message.text  # ユーザが送信したメッセージ(event.message.text)を取得

    #message = HandleMessageEventSwitch(event, getMessage)
    #replyMessageText(event, message)
    return getMessage


#@handler.add(MessageEvent, message=ImageMessage)
def replyImage(event):
    '''
    画像の返信　URLを指定する
    :return:
    '''    
    ...
    # 画像の送信
    image_message = ImageSendMessage(
        original_content_url=main_image_path,
        preview_image_url=main_image_path
    )

    line_bot_api.reply_message(event.reply_token, image_message)

def HandleMessageEventSwitch(event, getMessage: str):
    '''
    取得したメッセージから応答処理を実行
    :getMessage: 受信したメッセージ
    :return:応答メッセージ
    '''

    if str.isdecimal(getMessage):
        upload_to_tablestrage(getMessage)
        message = '追跡番号を登録しました．'

    elif getMessage == '追跡番号':
        message = '追跡番号を入力してください．'

    elif getMessage == '状態':
        replyImage(event)
        message = '最近の写真を表示します．'

    else :
        message = 'お客様がお望みなら、いつでもお荷物を受け取ります。\n宅配便代理受け取りサービス、ポーチマンです。'

    return message

def DownloadFlomBlob(targetfile,filepath):
    '''
    Azure BLOBからファイルをダウンロード
    :param targetfile: ダウンロードするファイル
    :param filepath: 保存先
    :return:
    '''
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONTAINER_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=targetfile)

    with open(filepath, "wb") as my_blob:
        my_blob.writelines([blob_client.download_blob().readall()])

def upload_to_tablestrage(userid="null": str,tracking_number: str):
    '''
    Azure Table Strageへ追跡番号をアップロード
    :tracking_number: 追跡番号　String型文字列
    :return:
    '''
    data = {
            # 必須のキー情報,user_idをSHA256でハッシュ化
            'PartitionKey': hashlib.sha256(userid+tracking_number).hexdigest(),
            # 必須のキー情報，ユーザID
            'RowKey': userid,
            # 追跡番号
            'number': tracking_number,
        }

    table_service.insert_or_replace_entity(
        AZURE_TABLENAME_TRAKINGNUMBER,
        data,
        timeout=None
    )

@api.route('/trackingnumber/registration', methods=['POST'])
def trackingnumber_registration():
    try:
        data = {
            # 必須のキー情報,user_idをSHA256でハッシュ化
            'PartitionKey': hashlib.sha256(request.form["user_id"]+request.form["trackingnumber"]).hexdigest(),
            # 必須のキー情報，ユーザID
            'RowKey': request.form["help_id"],
            # 追跡番号
            'number': request.form["trackingnumber"],
        }

        # 追跡番号情報をATSへ追加
        table_service.insert_or_replace_entity(AZURE_TABLENAME_TRAKINGNUMBER, data)
        print("send data to ATS")

        result = {
                "result":True,
                "data":{
                    "helpId":userdata['RowKey'],
                    "help_hash":userdata["PartitionKey"]
                    }
                }

    except Exception as except_var:
        print("except:"+except_var)
        abort(500)

    return make_response(jsonify(result))

@api.route('/trackingnumber/get', methods=['GET'])
def get_trackingnumber():
    '''
    追跡番号の問い合わせ
    :return:
    '''
    try:
        # クエリ文字列から検索するエリアを指定
        # http://address/trackingnumber/get?number=123456789
        requested_trackingnumber = request.args.get('number')

        # テーブルから検索
        result = table_service.query_entities(
            table_name=AZURE_TABLENAME_TRAKINGNUMBER,
            filter="places eq " + requested_trackingnumber
        )

        if len(result) == 1:
            result = {
                "result":True,
            }
        else:
            result = {
                "result":False,
            }

    except Exception as except_var:
        print("except:"+except_var)
        abort(500)

    return make_response(jsonify(result))

'''
メインサービス
'''
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)