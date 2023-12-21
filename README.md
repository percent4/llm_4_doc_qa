本项目用于文档问答，使用向量嵌入 + ES 做召回，使用Rerank模型作为精排，再使用LLM做文档问答，Web框架使用Flask。

项目的整体架构如图：

![文档问答流程图](https://percent4.github.io/img/nlp60_5.jpeg)

本项目对应的博客文章：

- [NLP（六十一）使用Baichuan-13B-Chat模型构建智能文档](https://mp.weixin.qq.com/s?__biz=MzU2NTYyMDk5MQ==&mid=2247485425&idx=1&sn=bd85ddfce82d77ceec5a66cb96835400&chksm=fcb9be61cbce37773109f9703c2b6c4256d5037c8bf4497dfb9ad0f296ce0ee4065255954c1c&token=28280910&lang=zh_CN#rd)
- [NLP（六十九）智能文档助手升级](https://mp.weixin.qq.com/s?__biz=MzU2NTYyMDk5MQ==&mid=2247485609&idx=1&sn=f8337b4822b1cdf95a586af6097ef288&chksm=fcb9b139cbce382f735e4c119ade8084067cde0482910c72767f36a29e7291385cbe6dfbd6a9&payreadticket=HJFJOt_DfmG3B-dmlm1HgcVHJP-S_fXfPwCpOqO05uqaij4NU-vn7HEWnzwgujoFA7BiQh8#rd)

### 启动方式

1. 安装ElasticSearch（版本7.17.0），建议使用Docker搭建环境，参考文件：docs/docker-compose-es.yml， 具体配置方法参考：[https://github.com/percent4/ES_Learning](https://github.com/percent4/ES_Learning)
2. 安装Milvus（版本2.2.1），建议使用Docker搭建环境，参考文件：docs/docker-compose-milvus.yml
3. 安装Python第三方模块，参考`requirements.txt`
4. 启动web服务: `python3 server.py`
5. 可视化web页面启动: server_gradio.py`

### HTTP请求

1. 文档问答接口

```bash
curl --location 'localhost:5000/api/doc_qa' \
--header 'Content-Type: application/json' \
--data '{
    "question": "戚发轫的头衔是什么？",
    "model_name": "gpt-3.5-turbo-1106"
}'
```

2. 文档上传

在浏览器中输入 http://localhost:5000//api/uploads 即可。

![文档上传页面](https://s2.loli.net/2023/12/21/3f5p7hWwRtogsyL.png)

3. 可视化问答页面

启动`server_gradio.py`脚本即可，采用Gradio工具开发。

### 支持模型

Embedding模型:

- [x] Baichuan-13B-Chat
- [x] text-embedding-ada-002

大模型（LLM）:

- [x] Baichuan-13B-Chat
- [x] LLAMA-2-Chinese-13b-Chat
- [x] internlm-chat-7b
- [x] ChatGPT model: GPT-3.5, GPT-4

### 功能特性

- [x] 支持文件格式
    - [x] txt文件
    - [x] pdf文件
    - [x] url链接（并非所有页面）
    - [x] word文件
- [x] 配置文件
- [x] 日志记录
- [x] 初筛阈值设置
- [ ] 高并发调用
- [x] 问答可追溯（加入文本高亮，属于答案归因研究课题）
- [x] 问答可视化页面
- [x] 多/单模型调用
- [x] 模型效果对比，类似Compass
- [ ] 多轮对话
- [x] 加入Rerank模型
- [x] 使用GPT-4进行模型评估（指标：CORRECTNESS）
- [x] 数据分析可视化

### 数据分析可视化

文件类型，共五种：

- txt: txt文件
- docx: docx文件
- pdf: pdf文件
- url: 用户输入的网址
- string: 用户自定义输入

在Kibana中使用可视化功能进行数据分析，首先统计每种文件类型的chunk（对文本内容进行划分，每个单位记为一个chunk）数据表格及柱状图、饼图：

![每种文件类型的chunk数据表格](https://s2.loli.net/2023/12/21/gSIFsClVfYJjch6.png)

![每种文件类型的chunk柱状图](https://s2.loli.net/2023/12/21/cXIglSrNWubDQwn.png)

![每种文件类型的chunk饼图](https://s2.loli.net/2023/12/21/kTY2mP6vcr5DKax.png)

每个文件类型的文件数量（使用source.keyword字段进行统计）：

![每个文件类型的文件数量](https://s2.loli.net/2023/12/21/fyQgkeG52AIx4W9.png)

文件插入时间与chunk数量的折线图（可用于记录不同时间段，插入的chunk数量统计）：

![文件插入时间与chunk数量的折线图](https://s2.loli.net/2023/12/21/d9IJatvEYi7P38W.png)

### 效果测试

- txt文件：

> 今年上半年的GDP增长率是多少？
> 
> 根据文档知识，2021年上半年的GDP增长率为5.5%。

> 你知道格里芬的职务吗？
> 
> 格里芬的职务是美国宇航局局长。

> 格里芬发表演说时讲了什么？
> 
> 根据文档知识，格里芬发表演说时讲了如下内容：他认为如果中国人愿意，2020年他们可以实现载人登月工程。此外，叶培建院士也曾发表自己的观点，认为2025年比较合适。然而，根据中国科学院编制的50年长远规划，中国要实现载人登月工程是2030年。

> 日本的国土面积多大？
> 
> \n根据文档知识：日本的国土面积为377,915平方千米。根据外部知识：日本是世界上国土面积第64大的国家，排名在它前面的有俄罗斯、加拿大、美国、中国和澳大利亚等国家。

> 一个地区如果回流生数量多会有什么影响？
> 
> 根据文档知识，一个地区如果回流生数量多可能会对常年在本地上学的学生造成一定的影响，导致学位紧张。但同时，也存在一些家长和学生通过投机行为，试图利用回流生的机会获得更好的教育资源。为了防止这种情况，需要采取措施震慑不法分子。同时，回流生的存在可能对本地学生产生一定的竞争压力，但主要还是要看学生的个人学习表现。

> 今年暑期档电影有哪些？
> 
> 今年暑期档电影市场活跃度持续升温，已有多部电影陆续上映。根据灯塔专业版统计，今年暑期档共有119部新片上映，涵盖了动画、冒险、剧情、儿童、纪录片、惊悚、科幻等多种题材。截至7月22日，暑期档总票房已突破100亿元，预计今年暑期档总票房将在160亿元以上。业内人士预测，今年暑期档有望成为“史上最强暑期档”。

> 封神第一部什么时候上映的？
> 
> 根据文档知识，《封神第一部》于2023年7月20日上映。


- pdf文件

> OPPO最新款折叠屏手机叫什么？
> 
> OPPO最新款折叠屏手机是OPPO Find N3 Flip。
> 
> 腾讯有发布自研的大模型吗，什么时候发布的？
> 
> 是的，腾讯已经发布了自研的大语言模型，名为 “ 混元大模型 ” 。它在 2023 年腾讯全球数字生态大会上正式对外亮相。具体时间为 9 月 7 日。

- word文件

> 海菜花对生长环境有什么要求？
> 
> 海菜花对生长环境要求极高，只能在水体洁净、透明度较高的水体中生长，被誉为水质的“试金石”。

- url链接

示例网址: [https://gaokao.xdf.cn/202303/12967078.html](https://gaokao.xdf.cn/202303/12967078.html)

> 电子科技大学2022年招生多少人？
> 
> 电子科技大学2022年招生总计划是5030人，其中“电子科技大学”将面向全国招生3300余人，“电子科技大学(沙河校区)”将面向部分省份招生1700余人。
> 
> 电子科技大学的官网？
> 
> 电子科技大学的官网是：http://www.zs.uestc.edu.cn/

示例网址: [https://www.hntv.tv/50rd/article/1/1700396378818207745?v=1.0](https://www.hntv.tv/50rd/article/1/1700396378818207745?v=1.0)

> PPT发明者是谁，他什么时候去世？
> 
> PPT发明者是丹尼斯·奥斯汀，他于2023年9月1日在美国加利福尼亚州洛斯阿尔托斯的家中去世，享年76岁。


### 可视化问答

- 单轮问答

> oppo 新款折叠屏手机叫什么，价格多少
> 
> oppo 新款折叠屏手机叫 OPPO Find N3 Flip，价格为6799元起(12GB+256GB版本)和7799元起(12GB+512GB版本)。
> 
> 混元大模型什么时候发布的？
> 
> 混元大模型是在2023年9月7日的腾讯全球数字生态大会上发布的。

![](https://s2.loli.net/2023/09/09/bGpvOTNHraePX1E.png)

![](https://s2.loli.net/2023/09/09/1IREmDQJqvsK9NG.png)

![](https://s2.loli.net/2023/09/09/CF8dx4wgEakt6Lz.png)

![答案归因](https://s2.loli.net/2023/09/09/zMeEg5nwmPZschj.png)
