# wecom message

企业微信机器人消息接口的封装。

## 使用方法

### 初始化

关于以下参数介绍请参考[企业微信基本概念介绍](https://developer.work.weixin.qq.com/document/path/90665)。

```python
from wecom import Message

# 企业微信企业id
CorpID = ''
# 企业微信应用 id
AgentID = ''
# 企业微信应用密码
AgentSecret = ''
# 企业微信应用 token
AgentToken = ''
# 企业微信应用消息加密密钥
AgentEncodingAESKey = ''

wecom_msg = Message(CorpID, AgentID, AgentSecret,
                    AgentToken, AgentEncodingAESKey)
```

### 验证 URL 有效性

```python
class Message():
    ...
    def VerifyURL(self, sMsgSignature, sTimeStamp, sNonce, sEchoStr):
        """验证URL
        @param sMsgSignature: 签名串,对应URL参数的msg_signature
        @param sTimeStamp: 时间戳,对应URL参数的timestamp
        @param sNonce: 随机串,对应URL参数的nonce
        @param sEchoStr: 随机串,对应URL参数的echostr
        @param sReplyEchoStr: 解密之后的echostr,当return返回0时有效
        @return: 成功0,失败返回对应的错误码
        """
```

### 接收用户消息/被动回复用户消息

1. 接收用户消息

```python
class Message():
    ...
    def dump(self, post_data, msg_signature, timestamp, nonce):
        """加密消息转 dict
        @param post_data: 加密消息，post 的 entity-body
        @param msg_signature: 签名串,对应URL参数的msg_signature
        @param timestamp: 时间戳,对应URL参数的timestamp
        @param nonce: 随机串,对应URL参数的nonce
        @return: 成功0,失败返回对应的错误码
        """
        ret, xml_content = self.DecryptMsg(
            post_data, msg_signature, timestamp, nonce)
        if ret != 0:
            return ret, "ERR: DecryptMsg ret: " + str(ret)
        return self._xml2dict(xml_content)
```

2. 回复用户消息

```python
class Message():
    ...
    def load(self, reply_msg: dict, nonce: str = None, timestamp=None):
		"""dict 转加密消息
        @param reply_msg: 需要回复的消息
        @param nonce: 随机串,可以使用接收到的 nonce, 也可以自己生成，WXBizMsgCrypt 实现了 generateNonce() 函数
        @param timestamp: 时间戳
        @return: 成功0,失败返回对应的错误码
        """
```

3. demo

```python

# 接收用户消息
encrypted_xml = request.data
msg_signature = request.args.get('msg_signature')
nonce = request.args.get('nonce')
timestamp = request.args.get('timestamp')

ret, msg = wecom_msg.dump(encrypted_xml, msg_signature,
                              timestamp, nonce)
if ret != 0:
    # 返回错误消息
    return msg

# 构造返回消息
reply_msg_content = "<要回复的消息>"

reply_dict = {
    'to_user': msg['FromUserName'],
    'from_user': msg['ToUserName'],
    'type': 'text',
    'content': reply_msg_content,
}

ret, reply_msg = wecom_msg.load(reply_dict)

if ret != 0:
    print("ERR: VerifyURL ret: " + str(ret))
    return "ERR: VerifyURL ret: " + str(ret)
return reply_msg
```

### 主动发送消息

企业微信要求企业在 5 秒内对消息进行被动回复，如果无法保证在 5 秒内处理并回复，或者不想回复任何内容，可以直接返回200（即以空串为返回包），后续主动发消息接口进行异步回复。

```python
class Message():
    ...
    def send_to_wecom(self, text, touid='@all'):
    """主动发送文本消息
    """
    def send_to_wecom_markdown(self, text, touid='@all'):
    """主动发送 markdown 文本消息
    """
    
    def send_to_wecom_pic(self, base64_content, touid='@all'):
    """主动发送图片消息
    """
    
    def send_to_wecom_file(self, base64_content, file_name, touid='@all'):
    """主动发送文件
    """
```

### 异步处理消息

`Flask`可采用 `flask_executor` 对消息进行异步处理，通过主动发送消息对用户发起回复。

## 参考项目

[Programer_Log/2020/3-16-企业微信 at master · makelove/Programer_Log (github.com)](https://github.com/makelove/Programer_Log/tree/master/2020/3-16-企业微信)

[sbzhu/weworkapi_python: official lib of wework api https://work.weixin.qq.com/api/doc (github.com)](https://github.com/sbzhu/weworkapi_python)

[easychen/wecomchan: 通过企业微信向微信推送消息的配置文档、直推函数和可自行搭建的在线服务代码。可以看成Server酱的开源替代方案之一。 (github.com)](https://github.com/easychen/wecomchan)