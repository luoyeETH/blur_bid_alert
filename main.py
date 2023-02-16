import json
import requests
from selenium import webdriver
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from dingtalkchatbot.chatbot import DingtalkChatbot

def launchSeleniumWebdriver():
    global driver
    option = webdriver.ChromeOptions()
    s = Service("chromedriver.exe")
    # 1.D:\ChromeSelenium_1修改为Chrome路径，参考chrome多开教程复制一个新的
    option.add_argument("--user-data-dir=" + r'D:\ChromeSelenium_1')
    driver = webdriver.Chrome(options=option, service=s)  # 此时将webdriver.exe 保存到python Script目录下

    return driver


def conncetMetaMask():
    driver.execute_script("window.open();")
    driver.switch_to.window(driver.window_handles[1])
    EXTENSION_ID = 'nkbihfbeogaeaoehlefnkodbefgpgknn'
    driver.get('chrome-extension://{}/home.html'.format(EXTENSION_ID))
    inputs = driver.find_elements(By.XPATH, '//input')
    # 2.AAAAAAAAAA修改为MetaMask密码
    inputs[0].send_keys('AAAAAAAAAA')
    driver.find_element(By.XPATH, '//button[text()="登录"]').click()
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(2)

def connectBlur():
    flag = checkElement('//button')
    if not flag:
        print("no connect button")
        driver.close()
        return
    driver.find_element(By.XPATH, '//button').click()
    time.sleep(3)
    # driver.find_element(By.XPATH, '//*[@id="METAMASK"]').click()
    # time.sleep(1)


def sign():
    driver.execute_script("window.open();")
    driver.switch_to.window(driver.window_handles[1])
    EXTENSION_ID = 'nkbihfbeogaeaoehlefnkodbefgpgknn'
    driver.get('chrome-extension://{}/home.html'.format(EXTENSION_ID))
    driver.find_element(By.XPATH, '//button[text()="签名"]').click()
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(2)


def getBids():
    driver.execute_script("window.open();")
    driver.switch_to.window(driver.window_handles[1])
    # 3.0x7a9e49dacfb35977762b9259df1dc8880471f898修改为自己地址
    driver.get('https://core-api.prod.blur.io/v1/collection-bids/user/0x7a9e49dacfb35977762b9259df1dc8880471f898?filters={}')
    time.sleep(1)
    #获取页面的json数据
    json_data = driver.find_element(By.XPATH, '//pre').text
    # print(json_data)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(1)
    return json_data


def getRealtimeBidPool(url):
    driver.execute_script("window.open();")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(url)
    # 获取页面的json数据
    json_data = driver.find_element(By.XPATH, '//pre').text
    # print(json_data)
    driver.close()
    # driver.switch_to.window(driver.window_handles[1])
    # driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(1)
    return json_data


if __name__ == '__main__':
    # 4.钉钉机器人配置 也可以换其他提醒 替换webhook和secret
    webhook = 'https://oapi.dingtalk.com/robot/send?access_token=aaaaaaaaaaaaaaaae53781405ce39c9a6e7e7ff7c5cb19c687bb754a'
    secret = 'SEC888888888888888888ac756092ee825f4720b74b31edd05b0538eda27dac4fcdd'
    ding_bot = DingtalkChatbot(webhook, secret=secret)
    # 5.合约地址白名单，可选，填上以后这个合约不提醒
    contract_whitelist = ['0x845a007d9f283614f403a24e3eb3455f720559ca']
    driver = launchSeleniumWebdriver()
    driver.implicitly_wait(5)
    driver.get('https://blur.io/portfolio/bids')
    conncetMetaMask()
    # 关闭其他窗口
    driver.switch_to.window(driver.window_handles[1])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    # connectBlur()
    # sign()
    # 获取bid数据
    data = getBids()
    # 将JSON字符串解析为Python字典
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
    url2_list = []
    for i in result:
        url = 'https://blur.io/collection/' + i['contractAddress'] + '/bids'
        url2 = 'https://core-api.prod.blur.io/v1/collections/' + i['contractAddress'] + '/executable-bids'
        url_list.append(url)
        url2_list.append(url2)
    while True:
        for i in range(0, len(url_list)):
            price = result[i]['price']
            contractAddress = result[i]['contractAddress']
            bidpool_data = getRealtimeBidPool(url_list[i], url2_list[i])
            # 将JSON字符串解析为Python字典
            data_dict = json.loads(bidpool_data)
            # 获取bidpool列表
            bid_pool = data_dict.get('priceLevels')
            executableSize1 = bid_pool[0]['executableSize']
            executableSize2 = bid_pool[1]['executableSize']
            if bid_pool[0]['price'] == price:
                msg = f"{contractAddress} 第一档 价格: {price} 第一档数量: {executableSize1} 第二档数量: {executableSize2}"
                print(msg)
                if contract_whitelist.count(contractAddress) == 0:
                    ding_bot.send_text(msg)
            elif bid_pool[1]['price'] == price:
                msg = f"{contractAddress} 第二档 价格: {price} 第一档数量: {executableSize1} 第二档数量: {executableSize2}"
                print(msg)
                if executableSize1 < 10 and contract_whitelist.count(contractAddress) == 0:
                    ding_bot.send_text(msg)
            elif bid_pool[2]['price'] == price:
                msg = f"{contractAddress} 第三档 价格: {price} 第一档数量: {executableSize1} 第二档数量: {executableSize2}"
                print(msg)
                if executableSize1 < 10 and executableSize2 < 10 and contract_whitelist.count(contractAddress) == 0:
                    ding_bot.send_text(msg)
            else:
                print(f"{contractAddress} 三档开外 安全")
            time.sleep(1)
        driver.refresh()
        time.sleep(60)

    print("done")
    driver.quit()
