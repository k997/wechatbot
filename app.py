"""
demo 将机器人收到所有消息发送到 memos 存储。
并通过 webhook 方便其他应用发送到消息到企业微信。

https://github.com/usememos/memos

"""
from flask import Flask, jsonify, request
from flask_executor import Executor

from config import *
from msg_service import Memos
from wecom import Message

app = Flask(__name__)
exectutor = Executor(app)


wecom_msg = Message(CorpID, AgentID, AgentSecret,
                    AgentToken, AgentEncodingAESKey)
memos = Memos(memos_uri, memos_openid)


@app.route("/D4286C47-6E28-9CF2-36CB-8996D28BA24C", methods=['POST'])
def rss_hook():
    """
    设置 webhook, 方便转发第三方消息至微信机器人
    """
    data = request.get_json().get("content")
    return wecom_msg.send_to_wecom(data, touid=wecom_default_user)


@app.route('/alive')
def alive():
    return jsonify({'msg': 'Service is alive.'})


@app.route('/', methods=['GET'])
def verifyURL_handler():
    try:
        msg_signature = request.args.get('msg_signature', "")
        timestamp = request.args.get('timestamp', "")
        nonce = request.args.get('nonce', "")
        echo_str = request.args.get('echostr', "")

        ret, echo_str = wecom_msg.VerifyURL(
            msg_signature, timestamp, nonce, echo_str)
        print(ret, echo_str)
        if ret != 0:
            print("ERR: VerifyURL ret: " + str(ret))
            return "ERR: VerifyURL ret: " + str(ret)
        return echo_str
    except ValueError as e:
        print("ValueError", e)
        return "NULL"


# 接收所有消息
@app.route('/', methods=['POST'])
def receiver():
    """receiver 负责接收所有发送给机器人的消息

    """
    encrypted_xml = request.data
    msg_signature = request.args.get('msg_signature')
    nonce = request.args.get('nonce')
    timestamp = request.args.get('timestamp')

    ret, msg = wecom_msg.dump(encrypted_xml, msg_signature,
                              timestamp, nonce)
    if ret != 0:
        # 此时 msg 为错误消息
        return ret, msg
    # 企业微信必须在 5s 内回复收到的消息，为避免超时
    # 所有收到的消息均由 msg_handler 进行处理，
    # 并对用户返回空字符串，后续主动向用户发起回复
    msg_handler.submit(msg)
    reply_msg_content = ""

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


@exectutor.job
def msg_handler(msg: dict):
    """消息处理函数

    Args:
        msg (dict): 接收到的消息
    """
    # 获取文本消息正文，并将所有收到的消息发送到 memos
    content = msg['Content']
    memos.post(content)

if __name__ == '__main__':
    app.run(debug=FlaskDebug, host=FlaskAddr, port=FlaskPort)
