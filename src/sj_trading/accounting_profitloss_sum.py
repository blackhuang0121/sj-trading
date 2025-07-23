import shioaji as sj
import pandas as pd
from .login import get_api

def profitloss_sum():
    api = get_api() 
    # 已實現損益
    # 查詢區間設限為12個月的區間
    
    profitloss_sum = api.list_profit_loss_summary(api.stock_account,'2025-01-01','2025-06-30')
    # print(profitloss_sum)
    df = pd.DataFrame(pnl.__dict__ for pnl in profitloss_sum.profitloss_summary)
    total_dict = profitloss_sum.total.__dict__
    df_total = pd.DataFrame([total_dict])

    # # df 明細
    # df = pd.DataFrame(pnl.__dict__ for pnl in profitloss_sum.profitloss_summary)
    # print(df)

    # # df_total 總計
    # total_dict = profitloss_sum.total.__dict__
    # df_total = pd.DataFrame([total_dict])
    # print(df_total)

    print(df)
    print(df_total)
    return api
