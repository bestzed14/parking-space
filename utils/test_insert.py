import os
import django

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkingsys.settings')
django.setup()

# 匯入 fetch_data 函式與 token、FunctionURL
from utils.tdx_api import fetch_data  # 如果你是放在這支檔案裡
from utils.tdx_api import get_token  # 自行調整你的 token 來源
# 測試用常數
#OffStreetCP 基礎資料  OffStreetPSA 停車位資料
#City:[ Taipei Taoyuan Taichung Tainan Kaohsiung Keelung ChanghuaCounty YunlinCounty
#       PingtungCounty YilanCounty HualienCounty KinmenCounty]
# FunctionURL = "OffStreetCP"
FunctionURL = "OffStreetPSA"

City = "Taichung"
token = get_token()

#如要單獨使用此檔案可用  python -m utils.test_insert
# 呼叫 fetch_data 並寫入資料庫
fetch_data(token, FunctionURL, City)

