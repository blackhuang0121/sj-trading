import shioaji as sj
import pandas as pd
from .login import get_api
from oauth2client.service_account import ServiceAccountCredentials
import gspread

def profitloss_detail(target_code="2357"):
    api = get_api()
    # 查所有已實現損益
    profitloss = api.list_profit_loss(api.stock_account, "2025-01-01", "2025-07-22")
    print("所有已實現損益紀錄：")
    # 1. print 出所有含該股票代碼的 id，呈現手續費、稅，沒有直接的已實現損益
    found = False
    for i, p in enumerate(profitloss):
        if hasattr(p, "code") and p.code == target_code:
            print(f"[{i}] id={p.id} code={p.code} qty={p.quantity} price={p.price} date={p.date}")
            found = True
    if not found:
        print(f"查無指定股票 {target_code} 的損益紀錄")
        return

    # 2. 批次查詢所有該股票的損益明細
    ids = [p.id for p in profitloss if hasattr(p, "code") and p.code == target_code]
    details_list = []
    for detail_id in ids:
        details = api.list_profit_loss_detail(api.stock_account, detail_id)
        for d in details:
            details_list.append(d.__dict__)
    if not details_list:
        print(f"查無 {target_code} 明細紀錄")
        return
    df = pd.DataFrame(details_list)

    # 3. Google Sheets API 認證
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/e0121n/Documents/sj-trading/secrets/auto_gsheet_bot_account_key.json', scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key('1VENNdDiBglXuO1bTlGp3Fl-G1Z9c_GRLgRGdEAWo6D8')
    sheet = spreadsheet.worksheet('api_list_profitloss')  # 覆蓋用

    # 4. 覆蓋寫入
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    print(f'已覆蓋更新 Google Sheet，{target_code} 所有已實現損益明細')
    return df
