##  Shioaji Trading 
1. This project is the repository remade from [永豐金證券 API: the Shioaji official documentation](https://sinotrade.github.io/zh_TW/).
2. 支援行情（報價）、下單、帳務（損益）三大功能。

## 1. 專案介紹
- **報價、行情（（Quate Market Data））**
    1. 相關股票表現
    2. 持股狀況（要看什麼）
    3. 排行（叫不出資料）
    （支援即時個股快照、歷史K棒查詢、自選股排行）
- **下單（Order）**
    1. 支援 API 下單
- **帳務（Accounting）**
    1. 未實現損益（持股）
    2. 已實現損益
   （尚無法直接查詢配發的股利）

<!-- Shioaji 目前沒有查詢「個人持股實際領到的股利」API。
如果想要「真實總收益」＝ 買賣損益 + 股利，必須手動合併券商對帳單或資金明細的配息紀錄。 -->

## 2. 架構
```
sj-trading
├── README.md # 專案總覽
├── pyproject.toml #專案主設定檔，管理 dependencies、指定 build backend、定義 scripts 作為 cli 指令使用
├── .env # 環境參數
├── .gitignore
└── src
    └── sj_trading
        └── __init__.py
        ├── login.py                   # API 登入流程
        ├── market_data.py             # 報價、行情查詢
        ├── order.py                   # 下單
        ├── accounting_profitloss.py   # 帳務查詢：如未實現損益、已實現損益等
        └── ...
├── .venv
├── .python-version
├── shioaji.log
├── uv.lock
```

## 3. 環境設定
1. 安裝套件：`pip install shioaji` / `uv add shioaji`
2. 設定虛擬環境：`pip install -e .`
3. 創建一個名為 sj-trading 的專案：
```py
- uv init sj-trading --package --app --vcs git
cd sj-trading
```
4. 加入 shioaji 套件到專案中：`uv add shioaji`

## 4. 執行
1. 執行 Python 檔案：`python src/sj_trading/accounting_profitloss.py`
2. 執行指令（scripts）：`profitloss = "sj_trading.accounting_profitloss:profitloss"`：`uv run profitloss`
