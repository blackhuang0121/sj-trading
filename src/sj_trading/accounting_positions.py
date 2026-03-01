import datetime
import pandas as pd
import shioaji as sj
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from .login import get_api

def positions():
    """
    一鍵完成：以「股」為單位取得所有部位（含整股與零股），計算未實現損益並同步至 Google Sheets
    """
    print("🚀 開始執行未實現損益更新流程...")
    
    api = get_api()

    # 1. 取得部位資料
    # 直接使用 Unit.Share (以股為單位)，這會回傳帳戶內所有持股的「總股數」
    # 這樣就不會發生整股與零股重複計算的問題
    positions_all = api.list_positions(api.stock_account, unit=sj.constant.Unit.Share)

    if not positions_all:
        print("ℹ️ 目前帳戶內沒有任何持股部位。")
        return pd.DataFrame()

    records = []
    for p in positions_all:
        # 根據代號查找股票名稱
        try:
            stock_name = api.Contracts.Stocks[p.code].name
        except Exception:
            stock_name = p.code

        # 直接讀取 API 回傳數值 (Unit.Share 模式下 quantity 單位就是「股」)
        quantity = p.quantity
        pnl_val = p.pnl if p.pnl else 0
        avg_price = p.price
        last_price = p.last_price
        
        # 計算成本與市值
        cost = avg_price * quantity
        market_value = last_price * quantity
        pnl_ratio = (pnl_val / cost * 100) if cost > 0 else 0
        
        records.append({
            "股票代號": p.code,
            "股票名稱": stock_name,
            "持有股數": int(quantity),
            "平均成本": round(avg_price, 2),
            "現價": last_price,
            "未實現損益": int(pnl_val),
            "報酬率(%)": round(float(pnl_ratio), 2),
            "總成本": int(cost),
            "市值": int(market_value)
        })

    df = pd.DataFrame(records)

    # 3️⃣ 計算合計行
    total_pnl = df["未實現損益"].sum()
    total_cost = df["總成本"].sum()
    total_market_value = df["市值"].sum()
    total_ratio = round((total_pnl / total_cost * 100), 2) if total_cost != 0 else 0

    total_row = pd.DataFrame([{
        "股票代號": "TOTAL",
        "股票名稱": "合計",
        "持有股數": int(df["持有股數"].sum()),
        "平均成本": None,
        "現價": None,
        "未實現損益": total_pnl,
        "報酬率(%)": total_ratio,
        "總成本": total_cost,
        "市值": total_market_value
    }])
    
    # 排序：按損益由高到低
    df = df.sort_values(by="未實現損益", ascending=False)
    df = pd.concat([df, total_row], ignore_index=True)

    # 4️⃣ 同步至 Google Sheets
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        key_path = '/Users/e0121n/Documents/sj-trading/secrets/auto_gsheet_bot_account_key.json'
        sheet_id = '1VENNdDiBglXuO1bTlGp3Fl-G1Z9c_GRLgRGdEAWo6D8'
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(sheet_id)
        sheet = spreadsheet.worksheet('api_positions')

        # 整理寫入資料格式
        header = df.columns.tolist()
        values = []
        for _, row in df.iterrows():
            processed_row = [str(val) if pd.notnull(val) and val is not None else "" for val in row]
            values.append(processed_row)

        # 執行清空與更新
        sheet.clear()
        sheet.update('A1', [header] + values)
        
        update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"✅ 所有持股部位（含整零整合）已於 {update_time} 成功更新至 Google Sheet")

    except Exception as e:
        print(f"❌ 同步至 Google Sheets 失敗: {e}")

    return df

if __name__ == "__main__":
    positions()
