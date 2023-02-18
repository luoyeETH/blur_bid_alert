import json
from selenium import webdriver
import time

from selenium.common import NoSuchWindowException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os
import sys
import configparser
import traceback
import requests

try:
    # 获取可执行文件所在目录的绝对路径
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

    # 读取INI配置文件
    config_path = os.path.join(base_path, 'config.ini')

    # 创建ConfigParser对象
    config = configparser.ConfigParser()

    # 读取配置文件
    config = configparser.ConfigParser()
    with open('config.ini', 'r', encoding='utf-8') as f:
        config.read_file(f)

    # 获取配置信息
    path = config.get('config', 'path')
    password = config.get('config', 'password')
    address = config.get('config', 'address')
    limit0 = int(config.get('config', 'limit0'))
    limit1 = int(config.get('config', 'limit1'))
    limit2 = int(config.get('config', 'limit2'))
    cd = int(config.get('config', 'cd'))
    cancel = config.get('config', 'cancel')
    telegram_bot_token = config.get('config', 'telegram_bot_token')
    telegram_id = config.get('config', 'telegram_id')
    whitelist_str = config.get('config', 'whitelist')
    whitelist = [i.strip() for i in whitelist_str.split(',')]


    def launchSeleniumWebdriver():
        global driver
        option = webdriver.ChromeOptions()
        s = Service("chromedriver.exe")
        option.add_argument("--user-data-dir=" + path)
        # option.add_argument('--headless')

        driver = webdriver.Chrome(options=option, service=s)  # 此时将webdriver.exe 保存到python Script目录下

        return driver


    def conncetMetaMask():
        driver.execute_script("window.open();")
        driver.switch_to.window(driver.window_handles[1])
        EXTENSION_ID = 'nkbihfbeogaeaoehlefnkodbefgpgknn'
        driver.get('chrome-extension://{}/home.html'.format(EXTENSION_ID))
        inputs = driver.find_elements(By.XPATH, '//input')
        inputs[0].send_keys(password)
        driver.find_element(By.XPATH, '//button[text()="登录"]').click()
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(2)


    def getBids():
        driver.execute_script("window.open();")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(f'https://core-api.prod.blur.io/v1/collection-bids/user/{address}')
        time.sleep(1)
        json_data = driver.find_element(By.XPATH, '//pre').text
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(1)
        return json_data


    def getRealtimeBidPool(url):
        driver.execute_script("window.open();")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(url)
        json_data = driver.find_element(By.XPATH, '//pre').text
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return json_data


    def getPoints():
        driver.execute_script("window.open();")
        driver.switch_to.window(driver.window_handles[1])
        driver.get("https://core-api.prod.blur.io/v1/user/rewards/wallet-compact")
        json_data = driver.find_element(By.XPATH, '//pre').text
        data_dict = json.loads(json_data)

        point_data = data_dict.get('wallet')
        print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} 总积分: {point_data.get("bidTotalXp")}')
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(1)


    def tg_bot(message):
        TOKEN = telegram_bot_token
        chat_id = telegram_id
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
        requests.get(url)  # this sends the message


    def cancel_bid(contract):
        if cancel == "on":
            driver.maximize_window()
            driver.execute_script("window.open();")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(f"https://blur.io/portfolio/bids?contractAddress={contractAddress}")
            driver.find_element(By.XPATH, '//button[@title="cancel bid"]').click()
            tg_bot(f"{contract} 已取消现有bid,请重新bid")
            time.sleep(0.5)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            driver.minimize_window()
            time.sleep(0.5)


    if __name__ == '__main__':
        tg_bot(f"[连通性检查]\n查询冷却时间 {cd}s\n推送时自动撤单 {cancel=='on'}\n[预警逻辑]\n当bid位于第一档时且第一档剩余bid总数低于{limit0}\n当bid"
               f"位于第二档时且第一档剩余bid总数低于{limit1}\n当bid位于第三档时且第一档与第二档剩余bid总数低于{limit2}")
        contract_whitelist = whitelist
        driver = launchSeleniumWebdriver()
        driver.implicitly_wait(5)
        driver.get('https://blur.io/portfolio/bids')
        conncetMetaMask()
        # 关闭其他窗口
        try:
            driver.switch_to.window(driver.window_handles[1])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except NoSuchWindowException:
            # 如果窗口不存在，则不执行任何操作
            pass
        driver.minimize_window()
        while True:
            # 获取bid数据
            data = getBids()
            data_dict = json.loads(data)
            # 获取priceLevels列表
            price_levels = data_dict.get('priceLevels')
            # 只保留priceLevels中的executableSize大于0的数据
            result = []
            for level in price_levels:
                if level.get('executableSize', 0) > 0:
                    result.append({'contractAddress': level['contractAddress'], 'price': level['price']})

            # 打印结果
            print(result)

            # 获取url列表
            url_list = []
            for i in result:
                url = 'https://core-api.prod.blur.io/v1/collections/' + i['contractAddress'] + '/executable-bids'
                url_list.append(url)

            for i in range(0, len(url_list)):
                price = result[i]['price']
                contractAddress = result[i]['contractAddress']
                bidpool_data = getRealtimeBidPool(url_list[i])
                data_dict = json.loads(bidpool_data)
                # 获取bidpool列表
                bid_pool = data_dict.get('priceLevels')
                num_levels = len(bid_pool)
                if num_levels == 1:
                    executableSize1 = bid_pool[0]['executableSize']
                    executableSize2 = 9999
                else:
                    executableSize1 = bid_pool[0]['executableSize']
                    executableSize2 = bid_pool[1]['executableSize']

                if bid_pool[0]['price'] == price:
                    msg = f"{contractAddress} 第一档 价格: {price} 第一档数量: {executableSize1} 第二档数量: {executableSize2}\n直达链接: " \
                          f"https://blur.io/portfolio/bids?contractAddress={contractAddress}"
                    print("\033[31m" + msg + "\033[0m")
                    if executableSize1 < limit0 and contract_whitelist.count(contractAddress) == 0:
                        tg_bot(msg)
                        cancel_bid(contractAddress)
                    else:
                        print("合约地址在白名单中，不推送消息")
                elif bid_pool[1]['price'] == price:
                    msg = f"{contractAddress} 第二档 价格: {price} 第一档数量: {executableSize1} 第二档数量: {executableSize2}\n直达链接: " \
                          f"https://blur.io/portfolio/bids?contractAddress={contractAddress} "
                    print(msg)
                    if executableSize1 < limit1 and contract_whitelist.count(contractAddress) == 0:
                        tg_bot(msg)
                        cancel_bid(contractAddress)
                elif bid_pool[2]['price'] == price:
                    msg = f"{contractAddress} 第三档 价格: {price} 第一档数量: {executableSize1} 第二档数量: {executableSize2}\n直达链接: " \
                          f"https://blur.io/portfolio/bids?contractAddress={contractAddress} "
                    print(msg)
                    if (executableSize1 + executableSize2) < limit2 and contract_whitelist.count(
                            contractAddress) == 0:
                        tg_bot(msg)
                        cancel_bid(contractAddress)
                elif bid_pool[3]['price'] == price:
                    msg = f"{contractAddress} 第四档 价格: {price} 第一档数量: {executableSize1} 第二档数量: {executableSize2}\n直达链接: " \
                          f"https://blur.io/portfolio/bids?contractAddress={contractAddress} "
                    print(msg)
                elif bid_pool[4]['price'] == price:
                    msg = f"{contractAddress} 第五档 价格: {price} 第一档数量: {executableSize1} 第二档数量: {executableSize2}\n直达链接: " \
                          f"https://blur.io/portfolio/bids?contractAddress={contractAddress} "
                    print(msg)
                else:
                    print(f"{contractAddress} 五档开外 安全")

                time.sleep(0.5)
            getPoints()
            driver.refresh()
            print(f"{cd}秒后开始新一轮检查")
            time.sleep(cd)

        print("done")
        driver.quit()

except Exception as e:
    # 捕获异常并打印错误信息
    print('Error: ')
    print(traceback.format_exc())
    input('Press Enter to exit...')


