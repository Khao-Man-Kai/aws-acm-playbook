# -*- coding: utf-8 -*-
# Todo: 外部モジュールとして読み込めなかったため、selenium.pyに集約。あとで対応する。
#

import boto3
from pytz import timezone
from datetime import datetime

# 自動化ツール用S3バケット、ベースディレクトリ指定
s3 = boto3.resource('s3')
bucket = s3.Bucket('misumi-automationtool')
base_dir = 'worklog/'

# 作業証跡用スクリーンショット名
work_log_img = 'hourly_acm_approval_mail_list.png'
target_time = "{0}".format((datetime.now(timezone('Asia/Tokyo')).strftime("%Y/%m/%d/")))
upload_filepass = base_dir + target_time + \
              datetime.now(timezone('Asia/Tokyo')).strftime("%H_").replace(':','_') + \
              work_log_img

"""
S3へACM UIのスクリーンショットをアップロードする
"""
def upload_object_test():
    bucket.upload_file(
        work_log_img,
        upload_filepass,
        ExtraArgs={
            'ACL':'public-read',         # URLを知っている場合のみ公開
            'ContentType': 'image/png'   # 画像をAWSが識別するために指定
        }
    )
