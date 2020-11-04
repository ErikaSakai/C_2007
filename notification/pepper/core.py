'''
pepperで動かす
Python2.X系で書く
'''
from azure.storage.blob import BlockBlobService

AZURE_CONTAINER_NAME = 'photo'

# TODO:環境変数使えるか確認
block_blob_service = BlockBlobService(
    account_name='accountname',
    account_key='accountkey'
    )

def upload_photo_to_azure():
    '''
    Azureに写真をアップロードしよう
    '''
    # TODO:アップロードする写真のファイルパス
    target_filepath = "~/filepath/*.jpg"

    # TODO:アップロードする写真のファイル名
    local_file_name = "*.jpg"
    
    with open(target_filepath, "w") as fp:
        # Azure ストレージコンテナへアップロード
        block_blob_service.create_blob_from_path(
            AZURE_CONTAINER_NAME,
            local_file_name,
            target_filepath
        )
