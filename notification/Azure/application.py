'''
Azureで実行するファイル
'''
import sys
import time
import os
import hashlib
import base64

from flask import Flask, abort, jsonify, make_response, request
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

# LINE Messaging API
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', None)
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

# LINEで表示する画像のURL,コア部分のみ
MAIN_IMAGE_PATH = os.getenv('MAIN_IMAGE', None)
PREVIEW_IMAGE_PATH = os.getenv('PREVIEW_IMAGE', None)  # ダミー

# Azure Storage Containerの名前，接続文字列
AZURE_CONTAINER_NAME = os.getenv('CONTAINER_NAME', None)
AZURE_STORAGE_CONTAINER_CONNECTION_STRING = os.getenv('ASC_CONNECTION_STRING', None)

# Azure Table Strageの名前，アクセスキー
AZURE_STORAGE_KEY = os.getenv('AZURE_STRAGE_KEY')
AZURE_STORAGE_NAME = os.getenv('AZURE_STRAGE_NAME')

AZURE_TABLENAME_TRAKINGNUMBER = 'tracknumber'

app = Flask(__name__)

# LINE APIに接続するやつ
LINE_BOT_API = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
HANDLER = WebhookHandler(LINE_CHANNEL_SECRET)

# Azure Table Serviceに接続するやつ
TABLE_SERVICE = TableService(account_name=AZURE_STORAGE_NAME, account_key=AZURE_STORAGE_KEY)
# BLOCK_BLOB_SERVICE = BlockBlobService(account_name=AZURE_STORAGE_NAME, account_key=AZURE_STORAGE_KEY)

BLOB_SERVICE_CLIENT = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONTAINER_CONNECTION_STRING)

@app.route("/callback", methods=['POST'])
def callback():
    '''
    LINEサーバへWebhookリクエストをチェック(認証)
    :return:
    '''
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    # app.logger.info("Request body: " + body)

    #署名を検証
    try:
        HANDLER.handle(body, signature)

    except LineBotApiError as except_msg:
        print("Got exception from LINE Messaging API: %s\n" % except_msg.message)
        for message in except_msg.error.details:
            print("  %s: %s" % (message.property, message.message))
        print("\n")

    except InvalidSignatureError:
        abort(400)

    return 'OK'

@HANDLER.add(MessageEvent, message=TextMessage)
def handle_message(event):
    '''
    ユーザが送信したLINEメッセージを取得
    :return:メッセージの内容
    '''
    # ユーザが送信したメッセージ(event.message.text)を取得
    get_message = event.message.text
    print('get message:' + get_message)

    reply_message = handle_message_event_switch(event, get_message)
    reply_message_text(event, reply_message)

    return

def reply_message_text(event, message):
    '''
    LINEメッセージを応答
    :message:応答として送信したいメッセージの文字列
    :return:
    '''
    print('send message' + message)
    LINE_BOT_API.reply_message(
        event.reply_token,
        TextSendMessage(text=message)  # 返信メッセージ
    )
    return

#@HANDLER.add(MessageEvent, message=ImageMessage)
def reply_image(event):
    '''
    画像の返信　URLを指定する
    :return:
    '''
    ...
    lest_file_name = get_lest_filename_on_azure()

    # 画像の送信
    image_message = ImageSendMessage(
        original_content_url=MAIN_IMAGE_PATH + lest_file_name,
        preview_image_url=MAIN_IMAGE_PATH + lest_file_name
    )

    LINE_BOT_API.reply_message(event.reply_token, image_message)
    return

def handle_message_event_switch(event, get_message):
    '''
    取得したメッセージから応答処理を実行
    :get_message: 受信したメッセージ
    :return:応答メッセージ
    '''

    if str.isdecimal(get_message):
        upload_to_tablestrage(get_message, event.source.user_id)
        message = '追跡番号('+get_message+')を登録しました．'

    elif get_message == '追跡番号':
        message = '追跡番号を入力してください．'

    elif get_message == '状態':
        reply_image(event)
        message = '最近の写真を表示します．'

    else:
        message = 'お客様がお望みなら、いつでもお荷物を受け取ります。\n宅配便代理受け取りサービス、ポーチマンです。'

    return message

def download_flom_blob(target_file, filepath):
    '''
    Azure BLOBからファイルをダウンロード
    :param targetfile: ダウンロードするファイル
    :param filepath: 保存先
    :return:
    '''
    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_STORAGE_CONTAINER_CONNECTION_STRING
        )
    blob_client = blob_service_client.get_blob_client(
        container=AZURE_CONTAINER_NAME,
        blob=target_file
        )

    with open(filepath, "wb") as my_blob:
        my_blob.writelines([blob_client.download_blob().readall()])

    return

@app.route("/image/upload", methods=["POST"])
def upload_to_blob():
    '''
    POSTされた画像をBLOBとしてアップロード
    '''
    userdata = {
        'image_data': request.form["image"]
    }
    # print(userdata['image_data'])

    img = base64.b64decode(userdata['image_data'].encode())

    local_file_name = str(int(time.time())) + '.jpg'

    blob_client = BLOB_SERVICE_CLIENT.get_blob_client(
        container=AZURE_CONTAINER_NAME,
        blob=local_file_name
        )
    blob_client.upload_blob(img)

    return 'OK'

def upload_to_tablestrage(tracking_number, userid="null"):
    '''
    Azure Table Strageへ追跡番号をアップロード
    :tracking_number: 追跡番号　String型文字列
    :return:
    '''
    try:
        prekey = str(userid) + str(tracking_number)

        data = {
            # 必須のキー情報,user_idをSHA256でハッシュ化
            'PartitionKey': hashlib.sha256(prekey.encode()).hexdigest(),
            # 必須のキー情報，ユーザID
            'RowKey': userid,
            # 追跡番号
            'number': tracking_number,
        }

        TABLE_SERVICE.insert_or_replace_entity(
            AZURE_TABLENAME_TRAKINGNUMBER,
            data,
            timeout=None
        )
        return

    except Exception as except_var:
        print("except:"+except_var)
        abort(500)

    return

@app.route('/trackingnumber/get', methods=['POST'])
def get_trackingnumber():
    '''
    追跡番号の問い合わせ
    :return:
    '''
    try:
        # クエリ文字列から検索するエリアを指定
        # https://porchman.azurewebsites.net/trackingnumber/get

        # 型に注意 （文字列型で扱う）
        requested_trackingnumber = request.form["trackId"]

        # テーブルから検索
        serch_result = TABLE_SERVICE.query_entities(
            table_name=AZURE_TABLENAME_TRAKINGNUMBER,
            filter="places eq " + requested_trackingnumber
        )

        counter = 0
        for entry in serch_result:
            print(entry.number)
            counter = counter + 1

        if len(counter) == 1:
            result = {
                "result":True,
            }
        else:
            result = {
                "result":False,
            }

    except Exception as except_var:
        print(except_var)
        abort(500)

    return make_response(jsonify(result))

def get_lest_filename_on_azure():
    '''
    Blobから最新のファイル名を取得．ファイル名はエポック秒のはず
    '''
    container_client = BLOB_SERVICE_CLIENT.create_container(AZURE_CONTAINER_NAME)

    # 最大値（最新時間の値）を格納
    buff = 0
    # List the blobs in the container
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        name_len = len(blob)

        # 最大値を探索（最新の画像）
        if str.isdecimal(blob[0:name_len-4]):
            if int(blob[0:name_len-4]) > buff:
                buff = int(blob[0:name_len-4])

    return str(buff)+".jpg"

'''
メインサービス
'''
if __name__ == "__main__":
    print("running porchman")
    PORT = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)
    