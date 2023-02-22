# blur_bid_alert
Blur bid提醒/自动撤单 使用selenium实现

> Blur里面割韭菜的太多，目前我自己刷分亏麻，这个项目不准备维护了，最新版本已经全部开源

## 使用教程

### Release版本
下载压缩包 并按教程配置

### 源码

### 环境要求
* Windows 或 Mac 操作系统
* Python 3.10
* Chrome 浏览器

### 安装 Python
#### Windows
访问 https://www.python.org/downloads/windows/ 下载 Windows 版本的 Python 安装程序。
运行安装程序，根据提示安装 Python。
#### Mac
访问 https://www.python.org/downloads/mac-osx/ 下载 Mac 版本的 Python 安装程序。
运行安装程序，根据提示安装 Python。

### 安装 PyCharm
PyCharm 是一个 Python 集成开发环境（IDE），可以方便地编写和调试 Python 代码。如果你已经有了其他的 Python 开发环境，可以跳过这一步。

访问 https://www.jetbrains.com/pycharm/download/ 下载 PyCharm 安装程序。
运行安装程序，根据提示安装 PyCharm。

### 安装浏览器驱动
本程序使用 Chrome 浏览器进行自动化操作，需要下载对应版本的 Chrome 驱动。请根据你的 Chrome 浏览器版本下载对应版本的驱动，并将驱动放在程序根目录下。

打开 Chrome 浏览器，在地址栏中输入 chrome://settings/help，查看自己的 Chrome 版本号。
访问 https://chromedriver.chromium.org/downloads 下载对应版本的 Chrome 驱动。
将下载好的驱动文件解压缩，将 chromedriver.exe（Windows）或 chromedriver（Mac）文件放在程序根目录下。

### 安装依赖
本程序依赖于一些 Python 包，可以通过以下命令安装：

`pip install -r requirements.txt`
  
### 填写配置文件
程序需要读取 config.ini 配置文件中的参数，根据需要修改字段  

## FAQ 持续更新  

* 1.检查chrome版本与下载  
检查自己浏览器版本: chrome://settings/help  
下载地址: https://chromedriver.chromium.org/downloads  

* 2.钉钉机器人创建路径  
电脑版钉钉，创建钉钉群，在钉钉群内 设置-智能群助手-添加机器人-选自定义机器人 添加时的安全设置选择加签  

* 3.多开浏览器  
在Chrome地址栏输入chrome://version/，查看自己的“个人资料路径”  
注意:  
1）路径到User  Data ,不要后面的Default    
2）关闭所有的Chrome进程(必须关闭在运行的浏览器)   
完整复制这个路径到一个新的路径 比如D:\ChromeSelenium  
最后将这个路径填入config.ini的path中  
以上过程比较方便，也可以自己创一个新的空浏览器再添加matamask导入助记词 

* 4.telegram机器人创建  
[BotFather](https://t.me/BotFather)-`/newBot`  
[MCT-Bot](https://t.me/MCT_CLUB_BOT)-`/getchatid` 获取用户id  
机器人创建好后先发一个`/start`激活  

* 5.为什么执行成功可以看到积分但是bid列表为空?  
config.ini 文件中address的地址应为全小写地址  

## 效果  
![log](log.png)  
![alert](alert.png)  

## 免责声明

**使用本软件及服务所存在的风险将完全由用户自行承担，本软件及服务不作任何类型的担保。用户理解和同意，本软件及服务可能会受到干扰、出现延迟或其他不可预见的情况，因使用本软件及服务而遭受的任何损失，本软件及服务不承担任何责任。对于因不可抗力或本软件及服务不能控制的原因造成的网络服务中断或其他缺陷，本软件及服务不承担任何责任。**

**本软件及服务所包含或提供的所有内容、信息、软件、产品及服务，均由第三方（如广告商、用户等）提供或制造，本软件及服务对其合法性概不负责，亦不承担任何法律责任。**

**本软件及服务对任何直接、间接、偶然、特殊及继起的损害不负任何责任，这些损害可能来自于：不当使用本软件及服务、在网上进行交易、非法使用本软件及服务或依赖本软件及服务所产生的损失及利润损失等。**

**本软件及服务会定期更新和升级，因此本软件及服务可能会因此而改变或暂停，用户知晓并同意本软件及服务会变更或暂停的风险。**

**用户在使用本软件及服务时，应遵守所有适用于其所在国家或地区的法律法规，用户理解并承担因违反法律法规所造成的后果。**

**若用户对本免责声明或本软件及服务有任何疑问或意见，请及时联系我们。**

## 开源许可  

```MIT License

Copyright (c) [2023] [luoye.eth]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
