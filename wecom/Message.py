import time
import xml.etree.ElementTree as ET

from .WXBizMsgCrypt import WXBizMsgCrypt
from .WecomChan import Wecomchan


class Message(WXBizMsgCrypt, Wecomchan):
    # python dict 转换成特定格式的xml,下面是一些模板
    """
        text_response = {
            'to_user':'',
            'from_user':'',
            'timestamp':'',
            'type':'text',
            'content':'',
        }
        voice_response= {
            'to_user':'',
            'from_user':'',
            'timestamp':'',
            'type':'voice',
            'media_id':''
        }
        image_response= {
            'to_user':'',
            'from_user':'',
            'timestamp':'',
            'type':'image',
            'data':[
                {'media_id':''}
            ]
        }
        video_response= {
            'to_user':'',
            'from_user':'',
            'timestamp':'',
            'type':'video',
            'media_id':'',
            'title':'',
            'description':'',
        }
        article_response= {
            'to_user':'',
            'from_user':'',
            'timestamp':'',
            'type':'news',
            'data':[
                {'title':'',
                 'description':'',
                 'pic_url':'',
                 'url':'',
                }
            ]
        }

    """
    BASIC_RESPONSE_FIELDS = '<ToUserName><![CDATA[%(to_user)s]]></ToUserName>' +\
        '<FromUserName><![CDATA[%(from_user)s]]></FromUserName>' +\
        '<CreateTime>%(timestamp)s</CreateTime>' +\
        '<MsgType><![CDATA[%(type)s]]></MsgType>'

    TEXT_RESPONSE_FIELD = "<Content><![CDATA[%(content)s]]></Content>"
    VOICE_RESPONSE_FIELD = "<Voice><![CDATA[%(media_id)s]]></Voice>"
    IMAGE_RESPONSE_FIELD = "<MediaId><![CDATA[%(media_id)s]]></MediaId>"
    VIDEO_RESPONSE_FIELD = '<Video>' +\
        '<MediaId><![CDATA[%(media_id)s]]></MediaId>' +\
        '<Title><![CDATA[%(title)s]]></Title>' +\
        '<Description><![CDATA[%(description)s]]></Description>' +\
        '</Video>'
    ARTICLE_RESPONSE_FIELD = '<items>' +\
        '<Title><![CDATA[%(title)s]]></Title>' +\
        '<Description><![CDATA[%(description)s]]></Description>' +\
        '<PicUrl><![CDATA[%(pic_url)s]]></PicUrl>' +\
        '<Url><![CDATA[%(url)s]]></Url>' +\
        '</items>'

    REQUEST_MESSAGE_TYPE_FIELDS = {
        "text": ["ToUserName", "FromUserName", "CreateTime", "MsgType", "Content", "MsgId", "AgentID"],
        "image": ["ToUserName", "FromUserName", "CreateTime", "MsgType", "PicUrl", "MediaId", "MsgId", "AgentID"],
        "voice": ["ToUserName", "FromUserName", "CreateTime", "MsgType", "Format", "MediaId", "MsgId", "AgentID"],
        "video": ["ToUserName", "FromUserName", "CreateTime", "MsgType", "ThumbMediaId", "MediaId", "MsgId", "AgentID"],
        "location": ["ToUserName", "FromUserName", "CreateTime", "MsgType", "Location_X", "Location_Y", "Scale", "Label", "MsgId", "AgentID"],
        "link": ["ToUserName", "FromUserName", "CreateTime", "MsgType", "Title", "Description", "PicUrl", "MsgId", "AgentID"],
    }

    def __init__(self, corp_id, agent_id, agent_secret, agent_token, agent_encoding_aes_key):
        WXBizMsgCrypt.__init__(
            self, sToken=agent_token, sEncodingAESKey=agent_encoding_aes_key, sCorpId=corp_id)
        Wecomchan.__init__(self, corpID=corp_id,
                           agentID=agent_id, agentSecret=agent_secret)

    def load(self, reply_msg: dict, nonce: str = None, timestamp=None):
        """dict 转加密消息
        @param reply_msg: 需要回复的消息
        @param nonce: 随机串,可以使用接收到的 nonce, 也可以自己生成，WXBizMsgCrypt 实现了 generateNonce() 函数
        @param timestamp: 时间戳
        @return: 成功0,失败返回对应的错误码
        """
        xml_message = self._dict2xml(reply_msg)
        if xml_message is None:
            return -1, ""
        ret, return_msg = self.EncryptMsg(
            xml_message, nonce, timestamp)
        return ret, return_msg

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

    def _xml2dict(self, xml_content):
        """
        xml 明文转 dict
        """
        xml_tree = ET.fromstring(xml_content)
        type_name = xml_tree.find("MsgType").text
        # 不处理事件消息
        if type_name == "event":
            return -1, "don't support event message!"
        msg = {}
        for nodename in self.REQUEST_MESSAGE_TYPE_FIELDS[type_name]:
            msg[nodename] = xml_tree.find(nodename).text
        return 0, msg

    def _dict2xml(self, data: dict):
        """
        dict 转 xml 明文消息
        """
        if 'timestamp' not in data:
            data['timestamp'] = str(int(time.time()))
        basic = self.BASIC_RESPONSE_FIELDS % data
        # text message
        if data['type'] == 'text':
            return '<xml>' + basic + self.TEXT_RESPONSE_FIELD % data + '</xml>'
        # image message
        elif data['type'] == 'image':
            tmp = ''
            for d in data['data']:
                tmp = tmp + self.IMAGE_RESPONSE_FIELD % d
            return '<xml>' + basic + '<Image>' + tmp + '</Image></xml>'
        # voice message
        elif data['type'] == 'voice':
            return '<xml>' + basic + self.VOICE_RESPONSE_FIELD % data + '</xml>'
        # video message
        elif data['type'] == 'video':
            return '<xml>' + basic + self.VIDEO_RESPONSE_FIELD % data + '</xml>'
        # news message
        elif data['type'] == 'news':
            tmp = ''
            for d in data['data']:
                tmp = tmp + self.ARTICLE_RESPONSE_FIELD % d
            count = "<ArticleCount>" + \
                str(len(data['data']))+"</ArticleCount>"
            return '<xml>' + basic + count + '<Articles>' + tmp + '</Articles></xml>'
        else:
            return None
