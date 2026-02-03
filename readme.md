# 天语阁
天语阁是一个基于PyQt6开发的桌面应用，允许用户使用大模型来进行对话、趣味写作，还有交互小说互动。

目前支持的LLM有：DeepSeek，豆包1.8，Gemini 3 Flash，Gemini 2.5 Flash，Gemini 2.5 Flash-Lite，Mistral Large 3，GLM-4.7-Flash。

所有信息，包括API，都只是在客户端本地存储。（我可没这钱来租服务器或云数据库存这个玩意儿……）总之这对于用户是安全的，看代码也看得出来，设置文件就在本地保存为当前目录下的data文件夹中。

## 功能

| 功能 | 功能说明 |
|-|-|
| 对话💬 | 直接和LLM对话 |
| 趣味写作✍️ | 用AI写点抽象东西 |
| 小游戏🎮 | 一点点小游戏（目前只有成语接龙） |
| 交互小说 | 这叠饺子的醋 |

另外，还有角色系统作为辅助。目前仅有交互小说会用到角色，但未来可能拓展。

## 运行
请在python环境中（最好弄个专门的虚拟环境吧），根据 `requirements.txt` 安装那些依赖的包（可能还有一些包，总之安装到能跑起来就行了）。
然后，在终端输入 `python main.py` 即可运行。
如果在Windos环境中，可以使用 `build.spec` 来打包出.exe文件，这样打包出的文件建议放在一个专门的文件夹里。
如果都不太会，也可以通过社交网络联系我（Iking），我直接发给你.exe文件。

## API 获取方法与费用简介

#### DeepSeek
DeepSeek API获取方法非常简单，在DeepSeek官方开放平台的API keys页面（https://platform.deepseek.com/api_keys）弄一个就好了。

它需要氪金，不过很便宜。

另外，好像也可以去字节跳动的火山引擎平台获取DeepSeek API，那个好像是有免费额度的，应该也可以在我们这个天语阁应用里使用。不过我没去弄。

#### 豆包
对于豆包大模型，需要我们在火山方舟管理控制台的API Key管理页面（https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey）去获取。

获取了之后，我们还要去开通管理页面（https://console.volcengine.com/ark/region:ark+cn-beijing/openManagement），点选开通几款需要的豆包大模型。目前，天语阁仅支持Doubao-Seed-1.8这款最新版的豆包。

豆包API也是会花钱的。不过，火山引擎会提供免费额度，具体地说，它每个模型赠送免费50万tokens的使用额度。另外豆包API是阶梯式计价，tokens少的任务很便宜。

### GLM和其他大模型
GLM-4.7-Flash是个免费模型，调用API免费。可以去它官网获取API Key。
其他大模型都可以去官网获取API密钥。

#### Tavily
Tavily倒不是一款大模型，tavily是一个为大型语言模型（LLMs）和检索增强生成（RAG）优化的搜索引擎，旨在提供高效、快速且持久的搜索结果。

Tavily的API可以在它官网（https://app.tavily.com/home）获取。这个搜索引擎API是很好的，它每个月提供1000次调用的免费额度，对于我们个人来用绰绰有余了。

## TODO
- [ ] 美化UI
- [ ] 其他功能……