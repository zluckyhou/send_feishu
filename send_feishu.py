import os
import requests
# from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
# 加载环境变量
# load_dotenv()

def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": app_id, "app_secret": app_secret}
    resp = requests.post(url, json=payload)
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"获取 token 失败: {data}")
    return data["tenant_access_token"]

def upload_image(image_path: str, tenant_access_token: str) -> str:
    url = "https://open.feishu.cn/open-apis/im/v1/images"
    headers = {"Authorization": f"Bearer {tenant_access_token}"}
    with open(image_path, 'rb') as f:
        files = {
            "image_type": (None, "message"),
            "image": (image_path, f, "image/png")
        }
        response = requests.post(url, headers=headers, files=files)
        data = response.json()
        if data.get("code", 0) != 0:
            raise Exception(f"上传图片失败: {data}")
        return data["data"]["image_key"]
def send_feishu_message(webhook_url: str, text: str, image_key: str = None):
    if image_key:
        # 图文消息
        payload = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "定时提醒",
                        "content": [
                            [
                                {"tag": "text", "text": text + " "},
                                {"tag": "at", "user_id": "all"}
                            ],
                            [
                                {"tag": "img", "image_key": image_key}
                            ]
                        ]
                    }
                }
            }
        }
    else:
        # 纯文本消息
        payload = {
            "msg_type": "text",
            "content": {
                "text": text + " @所有人"
            }
        }

    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, headers=headers, json=payload)
    print(f"发送状态: {response.status_code}, 返回内容: {response.text}")


def main():
    app_id = os.environ["FEISHU_APP_ID"]
    app_secret = os.environ["FEISHU_APP_SECRET"]
    webhook_url = os.environ["FEISHU_WEBHOOK_URL"]

    # 获取当前北京时间（UTC+8）
    beijing_now = datetime.now(timezone.utc) + timedelta(hours=8)
    current_hour = beijing_now.hour

    if current_hour == 11:
        image_path = "noon.jpeg"
        text = "午饭时间到！"
    elif current_hour == 17:
        image_path = "dinner.png"
        text = "该吃晚饭了！"
    elif current_hour == 19:
        # image_path = "night.png"
        text = "下班啦！"
    else:
        print(f"当前小时 {current_hour} 不是发送时间，跳过")
        return

    token = get_tenant_access_token(app_id, app_secret)

    # 尝试上传图片，失败时发纯文本
    image_key = None
    try:
        image_key = upload_image(image_path, token)
    except Exception as e:
        print(f"上传图片失败，发送纯文本消息。错误: {e}")

    send_feishu_message(webhook_url, text, image_key)


if __name__ == "__main__":
    main()
