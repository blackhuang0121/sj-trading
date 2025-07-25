import shioaji as sj
import pandas as pd
from .login import get_api
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import datetime

def exDividendAmt():
    api = get_api() 
    # 已實現損益
    # 查詢區間設限為12個月的區間
  
    # 1. 撈明細
    profitloss = api.list_profit_loss(api.stock_account, '2025-01-01', '2025-12-31')
    all_details = []
    for p in profitloss:
        detail_id = p.id
        details = api.list_profit_loss_detail(api.stock_account, detail_id)
        all_details.extend(details)

    df = pd.DataFrame(p.__dict__ for p in all_details)

    # 2. 計算「現金股利」合計
    total_dividend = df['ex_dividend_amt'].sum()

    # 3. 直接查 summary「含股利」損益
    summary = api.list_profit_loss_summary(api.stock_account, '2025-01-01', '2025-12-31')
    total_profit = summary.total.pnl  # 這就是含股利

    # 4. 計算「不含除息」損益
    pure_trade_profit = total_profit - total_dividend

    print("總損益（含股利）:", total_profit)
    print("現金股利合計:", total_dividend)
    print("純買賣損益（不含除息）:", pure_trade_profit)
