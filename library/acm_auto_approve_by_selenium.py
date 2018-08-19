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
from utils import upload_object_test

#login_url = 'https://awx.acp-automation.com:8000/'
login_url = 'https://127.0.0.1:8000/'
base_url = login_url + 'automation/mail/'
#login_user_name = 'yohei.q8hb.matsumoto@misumi.co.jp'
#login_user_passwd = 'Dkgy8526'
login_user_name = 'fip.zyxf.connect@misumi.co.jp'
login_user_passwd = 'Ham42323'

# 作業証跡用スクリーンショット名
work_log_img = datetime.now(timezone('Asia/Tokyo')).strftime("%H_") \
               + 'hourly_acm_approval_mail_list.png'


"""
ACM自動承認処理メイン
"""
def main():
    options = Options()
    # ヘッドレスモードを有効にする（次の行をコメントアウトすると画面が表示される）。
#    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    # ChromeのWebDriverオブジェクトを作成する。
    driver = webdriver.Chrome(chrome_options=options)
    # ウィンドウを最大化
    driver.set_window_size(1024,1680)

    try:
        driver.get(login_url)
        time.sleep(5)
        driver.find_element_by_id('connect-button').click()
    except:
        print('O365ログイン画面への遷移に失敗。処理を終了。')
        driver.save_screenshot("login.png")
        sys.exit(-1)
    else:
        print('O365ログイン画面への遷移に成功。')

    # O365ログイン画面でログインユーザ名を自動入力
    user_name = driver.find_element_by_id('i0116')
    user_name.send_keys(login_user_name)
    # O365ログイン画面でログインパスワードを自動入力
    user_passwd = driver.find_element_by_id('i0118')
    user_passwd.send_keys(login_user_passwd)

    try:
        # メールアドレスを入力しクリック
        driver.find_element_by_id('i0116').send_keys(Keys.RETURN)
        time.sleep(1)
        # パスワードを入力しクリック
        driver.find_element_by_id('i0118').send_keys(Keys.RETURN)
        # サインイン状態を保持しない、チェックボックスをオンにしページ遷移
        driver.find_element_by_id('idBtn_Back').send_keys(Keys.RETURN)
        # 読み込んだページHTMLを取得
        data = driver.page_source.encode('utf-8')
    except:
        print('[' + login_url + '] へのログインに失敗。処理を終了。')
        sys.exit(-1)
    else:
        print('[' + login_url + '] へのログインに成功。')

        # 承認リンク取得
        approvals_list  = driver.find_elements_by_link_text("Approve")   # Loop用
        approvals_stack = driver.find_elements_by_link_text("Approve")   # クリック用
        # JIRA作成ボタン取得
        btn_stack = driver.find_elements_by_class_name("jira")
        # 業務情報取得
        account_data_stack = driver.find_elements_by_class_name("account_data")
        # 自動承認処理
        for i, atag in enumerate(approvals_list, 1):
            time.sleep(7)   # JIRAチケット作成を加味したスリープ（概ね作成時間は5秒::Ajaxのタイムアウトは8秒に設定）
            # Controlを押しながらリンクをクリック
#            ActionChains(driver)\
#                .key_down(Keys.CONTROL)\
#                .click(approvals_stack.pop())\
#                .key_up(Keys.CONTROL)\
#                .perform()

            # Control（MacはCOMMAND）を押しながらリンクをクリック
            ActionChains(driver) \
                .key_down(Keys.COMMAND) \
                .click(approvals_stack.pop()) \
                .key_up(Keys.COMMAND) \
                .perform()

            # AWS承認ページの新タブに移動
            print("Debug0: [i]: {}".format(i))
            print("Debug0: driver.window_handles[i]: {}".format(driver.window_handles[i]))
            driver.save_screenshot("Debug0.png")
            driver.switch_to.window(driver.window_handles[i])
            time.sleep(5)

            try:
                # 自動承認実行: [I Approve]ボタンクリック
#               print(driver.find_element_by_name("commit"))
                driver.find_element_by_name("commit").click()
                print("Debug1: Click_to_approve_button")
                time.sleep(2)

                # 承認結果を格納
                business_data = driver.find_element_by_tag_name("h2").text
#               inspection_result = 'Success!'

                # 承認結果判定: 承認に成功した場合はJIRAチケットを作成する
                if business_data == 'Success!':
                    pass
                    # ACM承認依頼メールリストのメインタブに戻る
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(2)
                    print("Debug2: Business_data")
#                    print(account_data_stack.pop().get_attribute("value"))
                    print("Debug3: Click_to_jira_button")
                    btn_stack.pop().click()
                else:
                    print("Fail: \n")
            except:
                print('Fail: (name=commit) or <h2>Success!</h2>要素が存在しないため、承認処理/JIRAチケット作成をスキップ。\n')
                # 承認処理できないためJIRA作成はスキップ
                btn_stack.pop()
                account_data_stack.pop()
            else:
                print("ACM承認成功")
                print("JIRAチケット作成完了")

            # ACM承認依頼メールリストのメインタブに戻る
            driver.switch_to.window(driver.window_handles[0])

        time.sleep(3)
        # 作業証跡としてACM UIのスクリーンショットを取得
        driver.save_screenshot(work_log_img)
        print("Debug4: Save_screenshot")
        # 作業証跡および、メール添付用としてS3へUpload
        upload_object_test()
        print("Debug5: Upload_a_screenshot_to_S3")
        # 不要ファイル削除
#        os.remove(work_log_img)
        # 作業証跡メール送付
        driver.find_element_by_class_name("sendmail").click()
        time.sleep(5)
        # Exit
        print("Debug6: Successful!\n")
        driver.quit()


if __name__ == '__main__':
    main()

