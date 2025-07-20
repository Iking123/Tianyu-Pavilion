# 天语阁
天语阁是一个基于PyQt开发的桌面应用，允许用户输入大模型API密钥（目前仅支持DeepSeek和豆包），实现与AI的实时对话和娱乐互动。

所有信息，包括API，都只是在客户端本地存储。（我可没这钱来租服务器或云数据库存这个玩意儿……）总之这对于用户是安全的，看代码也看得出来，设置文件就在本地保存为config.enc，还有一些别的.enc文件类似。

## 功能

![image-20250720221910238](screenshots/home_page.png)如图，目前仅有对话、小游戏、交互小说、趣味写作这四大功能。

另外，还有角色系统作为辅助。目前仅有交互小说会用到角色，但未来可能拓展。



## 安装

不需要安装，下载即可用。下载 `dist/天语阁.exe` 这一个文件即可。

不过，如果你想要在自己的本机上直接跑代码，还是需要 `pip install pyqt5` 的，也可能还要安装一些别的依赖。



## API 获取方法与费用简介

#### DeepSeek

DeepSeek API获取方法非常简单，在DeepSeek官方开放平台的API keys页面（https://platform.deepseek.com/api_keys）弄一个就好了。

它需要氪金，不过很便宜。DeepSeek API是在凌晨（根据官方文档，**北京时间 00:30-08:30**）用会打2.5折。

另外，好像也可以去字节跳动的火山引擎平台获取DeepSeek API，那个好像是有免费额度的，应该也可以在我们这个天语阁应用里使用。不过我没去弄。

#### 豆包

对于豆包大模型，需要我们在火山方舟管理控制台的API Key管理页面（https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey）去获取。

获取了之后，我们还要去开通管理页面（https://console.volcengine.com/ark/region:ark+cn-beijing/openManagement），点选开通几款需要的豆包大模型。目前，天语阁仅支持Doubao-Seed-1.6和Doubao-Seed-1.6-thinking这两款最新版的豆包。

豆包API也是会花钱的。不过，火山引擎会提供免费额度，具体地说，它每个模型赠送免费50万tokens的使用额度。另外豆包API是阶梯式计价，tokens少的任务很便宜，如果不是在凌晨用，好像豆包的均价比DeepSeek更便宜。

#### Tavily

Tavily倒不是一款大模型，tavily是一个为大型语言模型（LLMs）和检索增强生成（RAG）优化的搜索引擎，旨在提供高效、快速且持久的搜索结果。

Tavily的API可以在它官网（https://app.tavily.com/home）获取。这个搜索引擎API是很好的，它每个月提供1000次调用的免费额度，对于我们个人来用绰绰有余了。



## TODO

- [ ] 优化启动速度（话说为什么，打包出来的这个天语阁.exe启动这么慢啊o(╥﹏╥)o）

- [ ] 优化交互小说的选项显示
- [ ] 添加对Gemini模型的支持

- [ ] 美化整个UI
- [ ] 其他功能……