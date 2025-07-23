import shioaji as sj
import pandas as pd
from .login import get_api
from oauth2client.service_account import ServiceAccountCredentials
import gspread

def profitloss_sum(year=2025):
    api = get_api() 
    # 已實現損益總計
    profitloss_sum = api.list_profit_loss_summary(api.stock_account, f'{year}-01-01', f'{year}-12-31')
    total_dict = profitloss_sum.total.__dict__
    df_total = pd.DataFrame([total_dict])
    df_total['year'] = year  # 加上年度欄位

    print(df_total)

    # 寫入 Google Sheet
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/e0121n/Documents/sj-trading/secrets/auto_gsheet_bot_account_key.json', scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key('1VENNdDiBglXuO1bTlGp3Fl-G1Z9c_GRLgRGdEAWo6D8')
    sheet = spreadsheet.worksheet('api_profitloss_sum')

    # # 先判斷是否已經有標題，沒有則加上
    # records = sheet.get_all_records()
    # if not records:
    #     sheet.append_row(df_total.columns.values.tolist())

    # # append 一行新資料
    # sheet.append_row(df_total.values.tolist()[0])
    # print(f'已新增 {year} 年度已實現損益總計到 Google Sheet')
    # return df_total

# 讀取所有現有資料
    records = sheet.get_all_records()
    header = df_total.columns.values.tolist()

    # 如果沒有資料，補上標題和第一行
    if not records:
        sheet.append_row(header)
        sheet.append_row(df_total.values.tolist()[0])
        print(f'已新增 {year} 年度已實現損益總計到 Google Sheet')
        return df_total

    # 轉成 DataFrame 判斷年度是否已存在
    df_sheet = pd.DataFrame(records)
    if 'year' not in df_sheet.columns:
        # 若原本沒 year 欄位也先加上
        df_sheet['year'] = ''

    # 找有沒有這個年度
    if str(year) in df_sheet['year'].astype(str).values:
        # 已有這年度，覆蓋（找到該行 row）
        row_idx = df_sheet[df_sheet['year'].astype(str) == str(year)].index[0] + 2  # +2 for header
        sheet.update(f'A{row_idx}', df_total.values.tolist())
        print(f'已覆蓋 {year} 年度已實現損益總計')
    else:
        # 沒有就 append
        sheet.append_row(df_total.values.tolist()[0])
        print(f'已新增 {year} 年度已實現損益總計到 Google Sheet')

    return df_total
