import shioaji as sj
import os
from dotenv import load_dotenv

load_dotenv()

def get_api():
    # 建立 shioaji 物件
    api = sj.Shioaji()
    # 登入
    api.login(
        api_key=os.environ["API_KEY"],
        secret_key=os.environ["SECRET_KEY"],
        contracts_timeout=10000,  # 下載商品檔等 10 秒
    )
    # 啟用憑證
    api.activate_ca(
        ca_path=os.environ["CA_CERT_PATH"],
        ca_passwd=os.environ["CA_PASSWORD"],
        person_id=os.environ["PERSON_ID"],
    )
    return api
