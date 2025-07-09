import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

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

def send_feishu_message(webhook_url: str, text: str, image_key: str):
    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": "干饭时间到！",
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
    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, headers=headers, json=payload)
    print(f"发送状态: {response.status_code}, 返回内容: {response.text}")

def main():
    app_id = os.environ["FEISHU_APP_ID"]
    app_secret = os.environ["FEISHU_APP_SECRET"]
    webhook_url = os.environ["FEISHU_WEBHOOK_URL"]

    token = get_tenant_access_token(app_id, app_secret)
    image_key = upload_image("ganfan.png", token)  # 请确保 image 文件存在
    send_feishu_message(webhook_url, "干饭了！", image_key)

if __name__ == "__main__":
    main()
