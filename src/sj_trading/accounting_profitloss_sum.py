import shioaji as sj
import pandas as pd
from .login import get_api
from oauth2client.service_account import ServiceAccountCredentials
import gspread

def profitloss_sum(year=2025):
    api = get_api() 
    # 1. 取得 已實現損益總計
    profitloss_sum = api.list_profit_loss_summary(api.stock_account, f'{year}-01-01', f'{year}-12-31')
    total_dict = profitloss_sum.total.__dict__
    df_total = pd.DataFrame([total_dict])

    df_total['year'] = year  # 加上年度欄位

    # 2. 取得已實現損益中的現金股利
    profitloss = api.list_profit_loss(api.stock_account, f'{year}-01-01', f'{year}-12-31')
    all_details = []
    for p in profitloss:
        detail_id = p.id
        details = api.list_profit_loss_detail(api.stock_account, detail_id)
        all_details.extend(details)
    df_detail = pd.DataFrame(p.__dict__ for p in all_details)
    total_dividend = df_detail['ex_dividend_amt'].sum() if not df_detail.empty else 0

    df_total['ex_dividend_amt'] = total_dividend   # 新增到同一 row

    # 3. 計算不含息報酬率
    # 純資本利得 = pnl（總損益）- total_dividend
    # 報酬率 = 純資本利得 / buy_cost
    pure_trade_profit = df_total['pnl'][0] - total_dividend
    pr_ratio_pure = pure_trade_profit / df_total['buy_cost'][0] * 100 if df_total['buy_cost'][0] != 0 else 0  # 百分比
    df_total['pr_ratio_pure'] = round(pr_ratio_pure, 2)

      # 4. 新增三個欄位
    df_total['year'] = year
    df_total['ex_dividend_amt'] = total_dividend
    df_total['pr_ratio_pure'] = round(pr_ratio_pure, 2)

    
    # 5. 欄位順序
    # 省略 entry_amount、cover_amount
    final_cols = [
        'year', 'quantity', 'buy_cost', 'sell_cost', 'pnl', 'ex_dividend_amt', 'pr_ratio', 'pr_ratio_pure'
    ]
    # 若欄位不足自動補齊0
    for col in final_cols:
        if col not in df_total.columns:
            df_total[col] = 0
    df_total = df_total[final_cols]


    # 再重新命名
    col_map = {
        'year': '年度',
        'quantity': '成交數量',
        'buy_cost': '買進金額',
        'sell_cost': '賣出金額',
        'pnl': '損益',
        'ex_dividend_amt': '已實現股利',
        'pr_ratio': '含息報酬率',
        'pr_ratio_pure': '不含息報酬率'
    }
    df_total = df_total.rename(columns=col_map)

    # print(df_total)

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
