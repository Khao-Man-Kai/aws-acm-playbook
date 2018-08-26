# -*- coding: utf-8 -*-

import time, sys, os
from pytz import timezone
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)
import boto3
from pytz import timezone
from datetime import datetime

# 自動化ツール用S3バケット、ベースディレクトリ指定
s3 = boto3.resource('s3')
bucket = s3.Bucket('misumi-automationtool')
base_dir = 'worklog/'              # Prod
#base_dir = 'worklog/test/'         # Dev

# 作業証跡用スクリーンショット名
work_log_name = 'hourly_acm_approval_mail_list.png'
target_time = "{0}".format((datetime.now(timezone('Asia/Tokyo')).strftime("%Y/%m/%d/")))
upload_filepass = base_dir + target_time + \
                  datetime.now(timezone('Asia/Tokyo')).strftime("%H_").replace(':','_') + work_log_name

login_url = 'https://awx.acp-automation.com:8000/'
#login_url = 'https://127.0.0.1:8000/'     # headlessモードの場合、仕様上ローカルでの実行は失敗する
base_url = login_url + 'automation/mail/'
login_user_name = 'fip.zyxf.connect@misumi.co.jp'
login_user_passwd = 'Ham42323'

# 作業証跡用スクリーンショット名
work_log_img = datetime.now(timezone('Asia/Tokyo')).strftime("%H_") \
               + 'hourly_acm_approval_mail_list.png'

"""
S3へACM UIのスクリーンショットをアップロードする
"""
def upload_object():
    bucket.upload_file(
        work_log_img,
        upload_filepass,
        ExtraArgs={
            'ACL':'public-read',         # URLを知っている場合のみ公開
            'ContentType': 'image/png'   # 画像をAWSが識別するために指定
        }
    )


"""
ACM自動承認処理メイン
"""
def main():
    print("Job start ===============================================================>")
    options = Options()
    # ヘッドレスモードを有効にする（次の行をコメントアウトすると画面が表示される）。
    options.add_argument('--headless')                                             # Prod
    options.add_argument('--no-sandbox')   # root以外でも実行可能にする
    # ChromeのWebDriverオブジェクトを作成する。
    driver = webdriver.Chrome(chrome_options=options)
    # ウィンドウサイズを調整
    driver.set_window_size(800,1280)

    try:
        print('Debug1: O365ログイン画面への遷移')
        driver.get(login_url)
        time.sleep(5)
        driver.find_element_by_id('connect-button').click()
    except:
        print(' Failed: O365ログイン画面への遷移に失敗しました。10秒後にリトライします。')
        try:
            time.sleep(10)
            driver.find_element_by_id('connect-button').click()
        except:
            print(' Failed: O365ログイン画面への遷移に失敗しました。終了します。')
            sys.exit(-1)
        else:
            print(' Success: O365ログイン画面への遷移にリトライして成功しました。')
    else:
        print(' Success: O365ログイン画面への遷移に成功しました。')

    # O365ログイン画面でログインユーザ名を自動入力
    user_name = driver.find_element_by_id('i0116')
    user_name.send_keys(login_user_name)
    # O365ログイン画面でログインパスワードを自動入力
    user_passwd = driver.find_element_by_id('i0118')
    user_passwd.send_keys(login_user_passwd)

    try:
        print('Debug2: O365ログイン処理')
        # メールアドレスを入力しクリック
        driver.find_element_by_id('i0116').send_keys(Keys.RETURN)
        time.sleep(3)
        # パスワードを入力しクリック
        driver.find_element_by_id('i0118').send_keys(Keys.RETURN)
        time.sleep(1)
        # サインイン状態を保持しない、チェックボックスをオンにしページ遷移
        driver.find_element_by_id('idBtn_Back').send_keys(Keys.RETURN)
        # 読み込んだページHTMLを取得
        driver.page_source.encode('utf-8')
    except:
        print(' Failed: [' + login_url + '] へのログインに失敗しました。10秒後にリトライします。')
        try:
            time.sleep(10)
            driver.page_source.encode('utf-8')
        except:
            print(' Failed: [' + login_url + '] へのログインに失敗しました。終了します。')
            sys.exit(-1)
        else:
            print(' Success: [' + login_url + '] へのログインにリトライして成功しました。\n')
    else:
        print(' Success: [' + login_url + '] へのログインに成功しました。\n')

        # 承認リンク取得
        approvals_list  = driver.find_elements_by_link_text("Approve")   # Loop処理用
        approvals_stack = driver.find_elements_by_link_text("Approve")   # クリック処理用
        # JIRA作成ボタン取得
        jira_btn_stack = driver.find_elements_by_class_name("jira")
        # 業務データ取得
        account_data_stack = driver.find_elements_by_class_name("account_data")
        # 自動承認処理
        for i, atag in enumerate(approvals_list, 1):
            time.sleep(7)   # JIRAチケット作成を加味したスリープ（概ね作成時間は5秒::Ajaxのタイムアウトは8秒に設定）
            # Controlを押しながらリンクをクリック
            ActionChains(driver)\
                .key_down(Keys.CONTROL)\
                .click(approvals_stack.pop())\
                .key_up(Keys.CONTROL)\
                .perform()

            # Control（MacはCOMMAND）を押しながらリンクをクリック
#            ActionChains(driver) \
#                .key_down(Keys.COMMAND) \
#                .click(approvals_stack.pop()) \
#                .key_up(Keys.COMMAND) \
#                .perform()

            # AWS承認ページの新タブに移動
            print("Debug3: [i]: {}".format(i))
            print("Debug3: driver.window_handles[i]: {}".format(driver.window_handles[i]))
            driver.save_screenshot("Debug0.png")
            driver.switch_to.window(driver.window_handles[i])
            time.sleep(5)

            try:
                # 自動承認実行: [I Approve]ボタンクリック
                print("Debug4: Click_to_approve_button")
#                driver.find_element_by_name("commit").click()                # Prodコード
                driver.find_element_by_name("commit")                         # Devコード
                time.sleep(2)

                # 承認結果を格納
#                result = driver.find_element_by_tag_name("h2").text          # Prodコード
                result = 'Success!'                                           # Devコード

                # 承認結果判定: 承認に成功した場合はJIRAチケットを作成する
                if result == 'Success!':
                    print(" Success: ACM承認成功")
                    # ACM承認依頼メールリストのメインタブに戻る
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(2)
                    try:
                        print("Debug5: Click_to_jira_button")
                        jira_btn_stack.pop().click()
                    except:
                        print(" Failed: JIRAチケット作成エラー")
                    else:
                        print(" Success: JIRAチケット作成完了＋業務データ保存完了")
                    time.sleep(3)
                else:
                    print(" Failed: 不明なエラー")
            except:
                print(' Failed: [name=commit)] or [<h2>Success!</h2>]要素が存在しません。')
                print(' 承認リンクのタイムアウト or 承認クリックが正常に処理されなかったため')
                print(' 承認処理/JIRAチケット作成をスキップします。')
                # 承認処理できないためJIRA作成はスキップ
                jira_btn_stack.pop()
                account_data_stack.pop()
            else:
                print("メインタブ[0]に戻る\n")

            # ACM承認依頼メールリストのメインタブに戻る
            driver.switch_to.window(driver.window_handles[0])

        time.sleep(3)
        # 作業証跡としてACM UIのスクリーンショットを取得
        print("Debug6: Save_screenshot")
        driver.save_screenshot(work_log_img)

        # 作業証跡および、メール添付用としてS3へUpload
        print("Debug7: Upload_a_screenshot_to_S3")
        upload_object()

        # 不要ファイル削除
        os.remove(work_log_img)

        # 作業証跡メール送付
        print("Debug8: Send_job_completion_notification_e-mail")
        driver.find_element_by_class_name("sendmail").click()
        time.sleep(5)

        # Exit
        print("Job finished ============================================================>")
        driver.quit()

if __name__ == '__main__':
    main()
