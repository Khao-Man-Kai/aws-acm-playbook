# -*- coding: utf-8 -*-

import time, sys, os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

login_url = 'https://awx.acp-automation.com:8000/'
#login_url = 'https://127.0.0.1:8000/'     # headlessモードの場合、仕様上ローカルでの実行は失敗する
base_url = login_url + 'automation/mail/'
login_user_name = 'fip.zyxf.connect@misumi.co.jp'
login_user_passwd = 'Ham42323'


"""
ACM Daily Reportメイン
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
    driver.set_window_size(840,1680)

    try:
        print('Debug0: O365ログイン画面への遷移')
        print("Debug 00-------------->")
        driver.get(login_url)
        print("Debug 01-------------->")
        time.sleep(5)
        print("Debug 02-------------->")
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
        print('Debug1: O365ログイン処理')
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

    try:
        time.sleep(3)
        # Daily Reportボタンクリック
        print('Debug2: Daily Reportボタンクリック')
        driver.find_element_by_class_name("send_daily_report").click()
        time.sleep(3)
    except:
        print(' Failed: [Send Daily Report] ボタンのクリックに失敗しました。終了します。')
    else:
        print(' Success: [Send Daily Report] ボタンのクリックに成功しました。')

        # Exit
        print("Job finished ============================================================>")
        driver.quit()


if __name__ == '__main__':
    main()
