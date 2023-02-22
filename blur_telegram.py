import json
from selenium import webdriver
import time
import re
from web3 import Web3
from selenium.common import NoSuchWindowException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os
import sys
import configparser
import traceback
import requests
from decimal import Decimal

global driver
restart = False
while True:
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
        if re.match("^0x[0-9a-fA-F]{40}$", address) and address == address.lower():
            pass
        else:
            print("The address is not valid or not all lowercase.")
            raise Exception("地址填写错误")
        limit0 = int(config.get('config', 'limit0'))
        limit1 = int(config.get('config', 'limit1'))
        limit2 = int(config.get('config', 'limit2'))
        cd = int(config.get('config', 'cd'))
        cancel = config.get('config', 'cancel')
        sign = config.get('config', 'sign')
        rebid = config.get('config', 'rebid')
        alert_contract_str = config.get('config', 'alert_contract')
        alert_contract = [i.strip() for i in alert_contract_str.split(',')]
        alert_price_str = config.get('config', 'alert_price')
        if not alert_price_str == "":
            alert_price = [float(x) for x in alert_price_str.split(',')]
        else:
            alert_price = []
        telegram_bot_token = config.get('config', 'telegram_bot_token')
        telegram_id = config.get('config', 'telegram_id')
        whitelist_str = config.get('config', 'whitelist')
        whitelist_array = [i.strip() for i in whitelist_str.split(',')]
        whitelist = [s.lower() for s in whitelist_array]
        blacklist_str = config.get('config', 'blacklist')
        blacklist_array = [i.strip() for i in blacklist_str.split(',')]
        blacklist = [s.lower() for s in blacklist_array]


        def launchSeleniumWebdriver():

            option = webdriver.ChromeOptions()
            s = Service("chromedriver.exe")
            option.add_argument("--user-data-dir=" + path)
            option.add_argument('log-level=INT')
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


        def checkElement(xpath):
            try:
                element = driver.find_element(By.XPATH, xpath)
            except NoSuchElementException:
                # print(f"no element {xpath}")
                return False
            else:
                return True


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
            # 发送带有链接的消息，并禁用链接预览
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            params = {"chat_id": chat_id, "text": message, "disable_web_page_preview": True}
            response = requests.post(url, params=params)

            # 检查是否成功发送消息
            if response.status_code == 200:
                pass
            else:
                print(f"发送消息失败，错误代码：{response.status_code}")


        def cancel_bid(contract, price, size):
            if cancel == "on":
                driver.maximize_window()
                collectionSlug = getcollectionSlug(contract)
                driver.execute_script("window.open();")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(f"https://blur.io/portfolio/bids?contractAddress={contract}")
                flag = checkElement('//button[@title="cancel bid"]')
                time.sleep(3)
                if flag:
                    driver.find_element(By.XPATH, '//button[@title="cancel bid"]').click()
                    tg_bot(f"[取消BID]\n{collectionSlug} 已取消现有bid,请重新bid\n直达链接: https://blur.io/{contract}/bids")
                else:
                    time.sleep(3)
                    flag = checkElement('//button[@title="cancel bid"]')
                    if flag:
                        driver.find_element(By.XPATH, '//button[@title="cancel bid"]').click()
                        tg_bot(f"[取消BID]\n{collectionSlug} 已取消现有bid,请重新bid\n直达链接: https://blur.io/collection/{contract}/bids")
                    else:
                        print("取消bid失败")
                time.sleep(1)
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                driver.minimize_window()
                time.sleep(0.5)
                bid_price = str(Decimal(price) - Decimal("0.01"))
                bid_size = int(size)
                if bid_size > 100:
                    bid_size = 100
                result = re_bid(collectionSlug, bid_price, bid_size)
                if result:
                    tg_bot(f"[自动bid]\nbid项目{collectionSlug}成功\nbid价格: {bid_price} eth, bid数量: {bid_size} 个")


        def bid_price_alert(contract, price):
            url = 'https://core-api.prod.blur.io/v1/collections/' + contract + '/executable-bids'
            bidpool_data = getRealtimeBidPool(url)
            data_dict = json.loads(bidpool_data)
            # 获取bidpool列表
            bid_pool = data_dict.get('priceLevels')
            if float(bid_pool[0]['price']) >= price:
                tg_bot(
                    f"[高价BID提示]\n{contract}出现 {price} eth及以上出价 \n"
                    f"价格: {bid_pool[0]['price']} eth, 数量: {bid_pool[0]['executableSize']}个\n"
                    f"确认BID: https://blur.io/collection/{contract}/bids\n"
                    f"接受BID: https://blur.io/portfolio?contractAddress={contract}")


        def check_pass(addr):

            # 连接到以太坊节点
            w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.g.alchemy.com/v2/cvMn6fHiMcsyT82Ms5MRB6yBGcEciIez'))

            # 以太坊ERC721合约地址
            contract_address = '0xF3B866a14b7e80B7A7968413117CA8926b85602e'

            # ERC721合约ABI
            abi = [{
                "constant": True,
                "inputs": [
                    {
                        "name": "_owner",
                        "type": "address"
                    }
                ],
                "name": "balanceOf",
                "outputs": [
                    {
                        "name": "",
                        "type": "uint256"
                    }
                ],
                "payable": False,
                "stateMutability": "view",
                "type": "function"
            }]

            # 实例化ERC721合约对象
            myContract = w3.eth.contract(contract_address, abi=abi)

            # 要验证的地址
            address_to_check = Web3.toChecksumAddress(addr)

            # 调用balanceOf函数获取地址持有的NFT数量
            nft_count = myContract.functions.balanceOf(address_to_check).call()

            # 验证地址是否持有至少一个指定NFT
            if nft_count > 0:
                print(f'地址 {address_to_check} Pass卡验证通过')
                return True
            else:
                print(f'地址 {address_to_check} 无效')
                return False


        def sign_bid():
            if sign == "on":
                driver.execute_script("window.open();")
                driver.switch_to.window(driver.window_handles[2])
                EXTENSION_ID = 'nkbihfbeogaeaoehlefnkodbefgpgknn'
                driver.get('chrome-extension://{}/home.html'.format(EXTENSION_ID))
                flag = checkElement('//i')
                if flag:
                    driver.find_element(By.XPATH, '//i').click()
                driver.find_element(By.XPATH, '//button[text()="签名"]').click()
                driver.close()
                driver.switch_to.window(driver.window_handles[1])
                try:
                    if len(driver.window_handles) > 2:
                        driver.switch_to.window(driver.window_handles[2])
                        driver.close()
                        driver.switch_to.window(driver.window_handles[1])
                except NoSuchWindowException:
                    # 如果窗口不存在，则不执行任何操作
                    pass
                time.sleep(2)
            else:
                time.sleep(10)

        def bid(collectionSlug, price, size):
            try:
                driver.maximize_window()
                try:
                    if len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[1])
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                except NoSuchWindowException:
                    # 如果窗口不存在，则不执行任何操作
                    pass
                driver.execute_script("window.open();")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(f"https://blur.io/collection/{collectionSlug}/bids")
                time.sleep(1)
                flag = checkElement('//div[text()="place collection bid"]')
                if flag:
                    driver.find_element(By.XPATH, '//div[text()="place collection bid"]').click()
                input1 = driver.find_element(By.XPATH, '//input[@placeholder="0.00"]')
                input1.send_keys(price)
                input2 = driver.find_element(By.XPATH, '//input[@placeholder="1"]')
                input2.clear()
                time.sleep(1)
                input2.click()
                input2.clear()
                input2.send_keys(str(size))
                driver.find_element(By.XPATH, '//div[text()="place bid"]').click()
                time.sleep(5)
                sign_bid()
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                return True
            except Exception:
                driver.close()
                print(traceback.format_exc())
                driver.switch_to.window(driver.window_handles[0])
                return False


        def re_bid(collectionSlug, price, size):
            if rebid == "on":
                try:
                    driver.maximize_window()
                    try:
                        if len(driver.window_handles) > 1:
                            driver.switch_to.window(driver.window_handles[1])
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                    except NoSuchWindowException:
                        # 如果窗口不存在，则不执行任何操作
                        pass
                    driver.execute_script("window.open();")
                    driver.switch_to.window(driver.window_handles[1])
                    driver.get(f"https://blur.io/collection/{collectionSlug}/bids")
                    time.sleep(1)
                    flag = checkElement('//div[text()="place collection bid"]')
                    if flag:
                        driver.find_element(By.XPATH, '//div[text()="place collection bid"]').click()
                    input1 = driver.find_element(By.XPATH, '//input[@placeholder="0.00"]')
                    input1.send_keys(price)
                    input2 = driver.find_element(By.XPATH, '//input[@placeholder="1"]')
                    input2.clear()
                    time.sleep(1)
                    input2.click()
                    input2.clear()
                    input2.send_keys(str(size))
                    driver.find_element(By.XPATH, '//div[text()="place bid"]').click()
                    time.sleep(5)
                    sign_bid()
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    return True
                except Exception:
                    driver.close()
                    print(traceback.format_exc())
                    driver.switch_to.window(driver.window_handles[0])
                    return False
            else:
                return False


        def getContract(collectionSlug):
            driver.execute_script("window.open();")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(f"https://core-api.prod.blur.io/v1/collections/{collectionSlug}")
            json_data = driver.find_element(By.XPATH, '//pre').text
            data_dict = json.loads(json_data)
            collection_data = data_dict.get('collection')
            time.sleep(0.5)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            return collection_data["contractAddress"]


        def getcollectionSlug(contract):
            driver.execute_script("window.open();")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(f"https://core-api.prod.blur.io/v1/collections/{contract}")
            json_data = driver.find_element(By.XPATH, '//pre').text
            data_dict = json.loads(json_data)
            collection_data = data_dict.get('collection')
            time.sleep(0.5)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            return collection_data["collectionSlug"]

        def auto_bid(balance, depth, day, level):
            driver.get('https://blur.io/collections')
            conncetMetaMask()
            try:
                if len(driver.window_handles) > 1:
                    driver.switch_to.window(driver.window_handles[1])
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
            except NoSuchWindowException:
                # 如果窗口不存在，则不执行任何操作
                pass
            driver.refresh()
            time.sleep(1)
            # div_element = driver.find_element(By.XPATH, '//div[@role="rowgroup"]')
            #
            # # 执行 JavaScript 代码，实现 div 内部滚动
            # driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", div_element)
            # time.sleep(1)
            collections = driver.find_elements(By.XPATH, "//a[contains(@href, '/collection/')]")
            collectionSlug_list = []
            for i in range(0, len(collections)):
                route = collections[i].get_attribute('href')
                collectionSlug_list.append(route.replace("https://blur.io/collection/", ""))
            print(f"获取到的项目数{len(collectionSlug_list)}")
            success_count = 0
            for i in range(0, len(collectionSlug_list)):
                if success_count >= depth:
                    break
                contractAddr = getContract(collectionSlug_list[i])
                # 判断合约创建时间
                #
                #
                if contractAddr in blacklist:
                    print(f"项目{collectionSlug_list[i]}在黑名单, 不进行bid")
                    continue
                api_url = 'https://core-api.prod.blur.io/v1/collections/' + contractAddr + '/executable-bids'
                bidpool_data = getRealtimeBidPool(api_url)
                data_dict = json.loads(bidpool_data)
                # 获取bidpool列表
                bid_pool = data_dict.get('priceLevels')
                num_levels = len(bid_pool)
                if num_levels < level:
                    print(f"项目{collectionSlug_list[i]}档位不足, 不进行bid")
                    continue
                bid_price = float(bid_pool[level - 1]['price'])
                bid_size = int(balance // bid_price)
                if bid_size == 0:
                    bid_price = balance
                    bid_size = 1
                if bid_size > 100:
                    bid_size = 100
                result = bid(collectionSlug_list[i], bid_price, bid_size)
                if result:
                    success_count += 1
                    tg_bot(f"[自动bid]\nbid项目{collectionSlug_list[i]}成功\nbid价格: {bid_price} eth, bid数量: {bid_size} 个")

            # tg_bot(f"[自动出价]\n自动bid完成,bid成功了{}项目")
            # driver.quit()


        def check_bid(contractAddress, price, size):
            url = f"https://core-api.prod.blur.io/v1/collections/{contractAddress}/executable-bids"
            bidpool_data = getRealtimeBidPool(url)
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
                msg = f"BID处于第一档 价格: {price} 第一档数量: {executableSize1} 第二档数量: {executableSize2} 合约: {contractAddress}" \
                      f"\n直达链接: https://blur.io/portfolio/bids?contractAddress={contractAddress}"
                print("\033[31m" + msg + "\033[0m")
                if executableSize1 < limit0 and contract_whitelist.count(contractAddress) == 0:
                    tg_bot(f"[预警提示]\n" + msg)
                    cancel_bid(contractAddress, price, size)
            elif bid_pool[1]['price'] == price:
                msg = f"BID处于第二档 价格: {price} 第一档数量: {executableSize1} 第二档数量: {executableSize2} 合约: {contractAddress}" \
                      f"\n直达链接: https://blur.io/portfolio/bids?contractAddress={contractAddress}"
                print(msg)
                if executableSize1 < limit1 and contract_whitelist.count(contractAddress) == 0:
                    tg_bot(f"[预警提示]\n" + msg)
                    cancel_bid(contractAddress, price, size)
            elif bid_pool[2]['price'] == price:
                msg = f"BID处于第三档 价格: {price} 第一档数量: {executableSize1} 第二档数量: {executableSize2} 合约: {contractAddress}" \
                      f"\n直达链接: https://blur.io/portfolio/bids?contractAddress={contractAddress}"
                print(msg)
                if (executableSize1 + executableSize2) < limit2 and contract_whitelist.count(
                        contractAddress) == 0:
                    tg_bot(f"[预警提示]\n" + msg)
                    cancel_bid(contractAddress, price, size)
            elif bid_pool[3]['price'] == price:
                msg = f"BID处于第四档 价格: {price} 第一档数量: {executableSize1} 第二档数量: {executableSize2} 合约: {contractAddress}" \
                      f"\n直达链接: https://blur.io/portfolio/bids?contractAddress={contractAddress}"
                print(msg)
            elif bid_pool[4]['price'] == price:
                msg = f"BID处于第五档 价格: {price} 第一档数量: {executableSize1} 第二档数量: {executableSize2} 合约: {contractAddress}" \
                      f"\n直达链接: https://blur.io/portfolio/bids?contractAddress={contractAddress}"
                print(msg)
            else:
                print(f"BID处于五档以外 合约: {contractAddress}")

            time.sleep(0.5)


        if __name__ == '__main__':
            is_allow = check_pass(address)
            if not is_allow:
                raise Exception("缺少Pass卡")
            driver = launchSeleniumWebdriver()
            driver.implicitly_wait(5)
            if not restart:

                mode = input("1.检查bid情况\n"
                             "2.自动bid\n"
                             "请选择模式 (1 或 2): ")

                if mode == "2":
                    balance = input("请输入Blur-pool余额 (单位: eth): ")
                    balance = float(balance)
                    depth = input("请输入要bid项目的数量: ")
                    depth = int(depth)
                    day = input("请输入nft已创建天数最小值: ")
                    level = input("请输入要bid的档位: ")
                    level = int(level)
                    if level == "1":
                        ask = input("第一档接盘风险很大，确认继续?[y/n]:")
                        if not ask == "y":
                            raise Exception("取消bid")
                    print("开始自动bid")
                    tg_bot(f"[连通性检查]\n开始自动bid")
                    auto_bid(balance, depth, day, level)
                    print("--------------------------------------------")
                    print("自动bid完成 开始开始检查bid情况")
                else:
                    print("开始检查bid情况")

            tg_bot(f"[连通性检查]\n查询冷却时间 {cd}s\n推送时自动撤单 {cancel == 'on'}\n撤单后补回bid {rebid == 'on'}\n自动签名 {sign == 'on'}\n"
                   f"[预警逻辑]\n当bid位于第一档时且第一档剩余bid总数低于{limit0}\n当bid位于第二档时且第一档剩余bid总数低于{limit1}\n"
                   f"当bid位于第三档时且第一档与第二档剩余bid总数低于{limit2}")
            contract_whitelist = whitelist
            driver.get('https://blur.io/portfolio/bids')
            conncetMetaMask()
            # 关闭其他窗口
            try:
                if len(driver.window_handles) > 1:
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
                        result.append({'contractAddress': level['contractAddress'],
                                       'price': level['price'], 'executableSize': level['executableSize']})

                # 打印结果
                print(result)

                # 获取url列表
                url_list = []
                for i in result:
                    url = 'https://core-api.prod.blur.io/v1/collections/' + i['contractAddress'] + '/executable-bids'
                    url_list.append(url)

                for i in range(0, len(url_list)):
                    contractAddress = result[i]['contractAddress']
                    price = result[i]['price']
                    size = result[i]['executableSize']
                    check_bid(contractAddress, price, size)

                getPoints()
                for contract, price in zip(alert_contract, alert_price):
                    bid_price_alert(contract, price)
                driver.refresh()
                print(f"{cd}秒后开始新一轮检查")
                time.sleep(cd)

    except Exception as e:
        # 捕获异常并打印错误信息
        print('Error: ')
        print(traceback.format_exc())
        driver.quit()
        restart = True
        continue
