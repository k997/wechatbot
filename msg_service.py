import requests

class Memos():
    """
    发送笔记到 memos
    """
    def __init__(self, uri: str, openid: str) -> None:
        self.uri = uri
        self.openid = openid

    def post(self, message: str):
        """
        发起 post 请求 
        """
        resp = requests.post(
            f"{self.uri}/api/memo?openId={self.openid}", json={"content": message})
        if resp.status_code != requests.status_codes.ok:
            return None
        return resp.text
