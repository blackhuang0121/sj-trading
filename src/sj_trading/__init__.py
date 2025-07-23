import shioaji as sj
from .login import get_api

def hello():
    get_shioaji_client()


def get_shioaji_client() -> sj.Shioaji:
    api =  sj.Shioaji()
    print("Shioaji API created")
    return api

def show_version() -> str:
    print(f"Shioaji Version: {sj.__version__}")
    return sj.__version__

def account():
    api = sj.Shioaji()
    accounts = api.list_accounts()
    print(accounts)
    
def usage():
    api = get_api()  # 這裡只會在第一次真的登入，後續都重用
    usage = api.usage()
    print(usage)
