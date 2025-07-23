import shioaji as sj
import pandas as pd
from .login import get_api
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import datetime

# 查詢單一商品
def get_stock_contract(stock_code="2890"):
    api = get_api()
    return api.Contracts.Stocks[stock_code]
    # or api.Contracts.Stocks.TSE.TSE2890

# 查詢多檔商品快照
def get_snapshots(stock_codes=["2330", "2357"]):
    api = get_api()
    contracts = [api.Contracts.Stocks[stock_code] for stock_code in stock_codes]
    snapshots = api.snapshots(contracts)
    return snapshots

    df = pd.DataFrame(s.__dict__ for s in snapshots)
    df.ts = pd.to_datetime(df.ts)
    df

# 例：測試用
if __name__ == "__main__":
    contract = get_stock_contract("2890")
    print(contract)

    snapshot_list = get_snapshots(["2330", "2357"])
    print(snapshot_list)

#
def get_snapshots_df(stock_codes=["2330", "2357", "2890", "9999"]):
    api = get_api()
    contracts = []
    for stock_code in stock_codes:
        contract = api.Contracts.Stocks.get(stock_code)
        if contract is not None:
            contracts.append(contract)
        else:
            print(f"警告：找不到商品檔 {stock_code}，請檢查商品代碼或登入時機！")
    
    if not contracts:
        print("沒有有效商品，無法查詢快照")
        return None

    # 查詢快照
    snapshots = api.snapshots(contracts)

    # 轉成 DataFrame
    df = pd.DataFrame(s.__dict__ for s in snapshots)
    if not df.empty and 'ts' in df.columns:
        df.ts = pd.to_datetime(df.ts)
    print(df)
    return df

# # 排行：成交量
def get_top_volume_stocks(count=10):
    api = get_api()  # 這裡只會在第一次真的登入，後續都重用
    scanners = api.scanners(
        scanner_type=sj.constant.ScannerType.ChangePercentRank,
        count=count,
    )
    print("scanners 回傳：", scanners)
    df = pd.DataFrame(s.__dict__ for s in scanners)
    if not df.empty and 'ts' in df.columns:
        df.ts = pd.to_datetime(df.ts)
    return df

if __name__ == "__main__":
    df = get_top_volume_stocks(10)
    print(df)

# 歷史行情：單一個股
def get_stock_kbars(stock_code="2890", start="2025-01-01", end="2025-06-27"):
    api = get_api()
    contract = api.Contracts.Stocks[stock_code]
    kbars = api.kbars(
        contract=contract,
        start=start,
        end=end,
    )
    # kbars 會是一個 dict，每個 key 一個 list
    df = pd.DataFrame({**kbars})
    if not df.empty and "ts" in df.columns:
        df.ts = pd.to_datetime(df.ts)
    print(df)
    return df

# 歷史行情：複數個個股
def get_multi_stock_kbars(stock_codes=["2330", "2357"], start="2025-01-01", end="2025-06-27"):
    api = get_api()
    dfs = []
    for stock_code in stock_codes:
        contract = api.Contracts.Stocks.get(stock_code)
        kbars = api.kbars(
            contract=contract,
            start=start,
            end=end,
        )
        df = pd.DataFrame({**kbars})
        df['stock_code'] = stock_code # 加入股票代碼欄位
        if not df.empty and 'ts' in df.columns:
            df.ts = pd.to_datetime(df.ts)
        dfs.append(df)
    # 合併所有 Dataframe
    all_df = pd.concat(dfs, ignore_index=True)
    print(all_df.head(20))
    return all_df
