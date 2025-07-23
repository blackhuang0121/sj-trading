import shioaji as sj
import pandas as pd
from .login import get_api
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import datetime

def list_profitloss():
    api = get_api() 
    # 已實現損益，包含稅費的所有明細
    # 查詢區間設限為12個月的區間
    # 第一步：查所有已實現損益
    profitloss = api.list_profit_loss(api.stock_account, "2025-01-01", "2025-07-22")
    print("已實現損益查詢結果：")
    for i, p in enumerate(profitloss):
        print(i, p.id, p)
        
    # 假設你要查第0筆明細
    if len(profitloss) > 0:
        detail_id = profitloss[0].id
        profitloss_detail = api.list_profit_loss_detail(api.stock_account, detail_id)
        df = pd.DataFrame(pnl.__dict__ for pnl in profitloss_detail)
        print(df)
    else:
        print("查無已實現損益，無法查明細")

    # 4. 設定 Google Sheets API 認證
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/e0121n/Documents/sj-trading/secrets/auto_gsheet_bot_account_key.json', scope)
    client = gspread.authorize(creds)

    # 5. 連線到你的 Google Sheet（用網址 key）
    spreadsheet = client.open_by_key('1VENNdDiBglXuO1bTlGp3Fl-G1Z9c_GRLgRGdEAWo6D8')  # 取網址 d/ 與 /edit 之間那串
    sheet = spreadsheet.worksheet('api_list_profitloss')  # 分頁名稱

    # 6. 讀取舊資料並合併
    try:
        old_data = sheet.get_all_records()
        old_df = pd.DataFrame(old_data)
    except Exception:
        old_df = pd.DataFrame()
        df_all = df  # 第一次執行無資料

    # 7. 合併與去重（唯一值為委托單號 dseq）
    df_all = pd.concat([old_df, df], ignore_index=True)
    df_all = df_all.drop_duplicates(subset=["dseq"], keep="last")  # 依據你資料唯一性選擇欄位
    df_all = df_all.sort_values(by=["date", "dseq"], ascending=[True, True])      # 新資料在最下面

    # 8. 寫入資料到 Sheet
    sheet.clear()
    sheet.update([df_all.columns.values.tolist()] + df_all.values.tolist())

    print('已更新已實現損益')
    return api
