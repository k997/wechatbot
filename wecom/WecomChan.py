import base64
import datetime
import json
import logging

import requests


class AccessTokenException(Exception):

    def __str__(self) -> str:
        return "access token 获取失败"


class Wecomchan():

    def __init__(self, corpID, agentID, agentSecret) -> None:
        self.corpID = corpID
        self.agentID = agentID
        self.agent_secret = agentSecret
        self.access_token_expires_in = datetime.datetime.min
        self._access_token = None

    @property
    def access_token(self):
        # token 未过期直接返回
        if datetime.datetime.now() < self.access_token_expires_in:
            return self._access_token

        get_token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corpID}&corpsecret={self.agent_secret}"
        response = requests.get(get_token_url)

        self._access_token = response.json().get('access_token')

        if self._access_token and len(self._access_token) > 0:
            expires_in = response.json().get("expires_in")
            self.access_token_expires_in = datetime.datetime.now(
            )+datetime.timedelta(seconds=expires_in)
            return self._access_token
        return None

    def send_to_wecom(self, text, touid='@all'):
        send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token}'
        data = {
            "touser": touid,
            "agentid": self.agentID,
            "msgtype": "text",
            "text": {
                "content": text
            },
            "duplicate_check_interval": 600
        }

        response = requests.post(send_msg_url, data=json.dumps(data)).content
        return response

    def send_to_wecom_markdown(self, text, touid='@all'):

        send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token}'
        data = {
            "touser": touid,
            "agentid": self.agentID,
            "msgtype": "markdown",
            "markdown": {
                "content": text
            },
            "duplicate_check_interval": 600
        }
        response = requests.post(send_msg_url, data=json.dumps(data)).content
        return response

    def send_to_wecom_pic(self, base64_content, touid='@all'):

        upload_url = f'https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={self.access_token}&type=image'
        upload_response = requests.post(upload_url, files={
            "picture": base64.b64decode(base64_content)
        }).json()

        logging.info('upload response: ' + str(upload_response))

        media_id = upload_response['media_id']

        send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token}'
        data = {
            "touser": touid,
            "agentid": self.agentID,
            "msgtype": "image",
            "image": {
                "media_id": media_id
            },
            "duplicate_check_interval": 600
        }
        response = requests.post(send_msg_url, data=json.dumps(data)).content
        return response

    def send_to_wecom_file(self, base64_content, file_name, touid='@all'):

        upload_url = f'https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={self.access_token}&type=file&debug=1'
        upload_response = requests.post(upload_url, files={
            "media": (file_name, base64.b64decode(base64_content))
        }).json()

        logging.info('upload response: ' + str(upload_response))

        media_id = upload_response['media_id']

        send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token}'
        data = {
            "touser": touid,
            "agentid": self.agentID,
            "msgtype": "file",
            "file": {
                "media_id": media_id
            },
            "duplicate_check_interval": 600
        }
        response = requests.post(send_msg_url, data=json.dumps(data)).content
        return response
