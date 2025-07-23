import shioaji as sj
import pandas as pd

api = sj.Shioaji()  # 建立物件
api.login(
    api_key="7dFgugw4G5merBZBowUWiAg51VRApsoDqCSS6fpKDe4x",
    secret_key="8q7DWfBc31zAjS1B9SriWpvofh18bvS3Z"
)

scanners = api.scanners(
    scanner_type=sj.constant.ScannerType.VolumeRank
    # 不設 count 參數
)

# 轉換成 DataFrame
df = pd.DataFrame(s.__dict__ for s in scanners)
print(df)
