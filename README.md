<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://raw.githubusercontent.com/nonebot/nonebot2/master/docs/.vuepress/public/logo.png" width="200" height="200" alt="nonebot"></a>
</p>

<div align="center">

# nonebot-plugin-docs

_✨ NoneBot2 图片搜索插件 ✨_

</div>

<p align="center">
  <a href="https://raw.githubusercontent.com/nonebot/nonebot2/master/LICENSE">
    <img src="https://img.shields.io/github/license/nonebot/nonebot2.svg" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-imgsearch">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-imgsearch.svg" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="python">
</p>

## 快速启动

* ### 1. 通过pip安装
  ```
  pip install nonebot-plugin-imgsearch
  ```


* ### 2. 申请 SAUCENAO API KEY
  [点此申请](https://saucenao.com/user.php?page=search-api)  
  `SauceNAO API KEY` 用于直接向saucenao请求搜索，无需模拟抓包，更快，更方便。  
  一个 `API KEY` 每30s可请求5次，每24h可请求200次。

* ### 3. 配置`.env`文件
  在你的`.env.*`文件中添加如下内容：
  ```
  search_proxy: <your_proxy>
  # 代理选项，可留空，如果你的bot位于国内，请填一个代理，
  # 通常它长这样 -> search_proxy="http://127.0.0.1:7890"
  
  saucenao_api_key: <your_saucenao_api_key>
  # 填你申请到的 SauceNAO API KEY, 是必选项。
  ```



## 使用教程

  在群组或私聊中发送 `/search [图片]` 即可进行搜索，支持多张  
  更多权限设置请修改`source code`
