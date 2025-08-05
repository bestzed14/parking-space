import requests
import json
import time
import os
from pprint import pprint
from django.utils import timezone
from datetime import datetime, timedelta
from parking_space.models import OffStreetCP,OffStreetPSA,DBUpdateTime
#City:[ Taipei Taoyuan Taichung Tainan Kaohsiung Keelung ChanghuaCounty YunlinCounty
#       PingtungCounty YilanCounty HualienCounty KinmenCounty]
app_id = 'rationalitypls-4a83a54a-6c43-4e4a'
app_key = '571782fb-86e7-4f92-b394-0052e197a0fe'
auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
base_url="https://tdx.transportdata.tw/api/basic/"
format_url="?%24format=JSON"
#完整API請求由 base_url+ FunctionURL +City + format_url 組成
###  以下為FunctionURL
API_URL_MAP = {
    "OffStreetCP": "v1/Parking/OffStreet/CarPark/City/",
    "OffStreetPSA": "v1/Parking/OffStreet/ParkingAvailability/City/"
}
#非路邊停車場車位
# OffStreetPSA="v1/Parking/OffStreet/ParkingAvailability/City/"
# #非路邊停車場基本資料
# OffStreetCP="v1/Parking/OffStreet/CarPark/City/"
#路邊停車場車位
OnStreetPSA="v1/Parking/OnStreet/ParkingSegmentAvailability/City/"

token_file = 'token.json'
token_valid_seconds = 86400  # 1 天的秒數

# ✅ 取得新 token 並寫入 token.json
def get_new_token():
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials',
        'client_id': app_id,
        'client_secret': app_key
    }

    response = requests.post(auth_url, headers=headers, data=data)
    response.raise_for_status()
    access_token = response.json().get('access_token')

    # 寫入 token.json
    with open(token_file, 'w') as f:
        json.dump({
            'access_token': access_token,
            'timestamp': int(time.time())
        }, f)

    print("✅ 取得新 token 並儲存。")
    return access_token


# ✅ 讀取 token，如果過期就重新取得
def get_token():
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        saved_time = token_data.get('timestamp', 0)
        now = int(time.time())
        if now - saved_time < token_valid_seconds:
            print("✅ 使用已儲存的 token")
            return token_data['access_token']
        else:
            print("⚠️ Token 過期，重新申請...")
            return get_new_token()
    else:
        print("⚠️ 尚未有 token，首次申請...")
        return get_new_token()


def save_to_db(data, function_type,City):
    if function_type == "OffStreetCP":
        for item in data.get("CarParks", []):
            OffStreetCP.objects.update_or_create(
                car_park_id=item.get("CarParkID"),
                city=item.get("City"),
                defaults={
                    "name": item.get("CarParkName", {}).get("Zh_tw"),
                    "description": item.get("Description"),
                    "faredescription": item.get("FareDescription"),
                    "address": item.get("Address"),
                    "emergency_phone": item.get("EmergencyPhone"),
                    "position_lat": item.get("CarParkPosition", {}).get("PositionLat"),
                    "position_lon": item.get("CarParkPosition", {}).get("PositionLon"),
                }
            )
    elif function_type == "OffStreetPSA":
        for item in data.get("ParkingAvailabilities", []):
            OffStreetPSA.objects.update_or_create(
                car_park_id=item.get("CarParkID"),
                # city=data.get("AuthorityCode"),  # or pass city separately
                city=City,  # or pass city separately
                defaults={
                    "total_spaces": item.get("TotalSpaces"),
                    "available_spaces": item.get("AvailableSpaces")
                }
            )


# ✅ 使用 token 存取指定功能/地區資料
def fetch_data(token,function_key,City):
    # 檢查或建立 db_updatetime 記錄
    db_updatetime, created = DBUpdateTime.objects.get_or_create(
        db=function_key,
        city=City,
        defaults={'updatetime': None}  # 若無記錄則建立，updatetime 預設為 None
    )

    # 判斷是否需跳過執行
    if db_updatetime.updatetime is not None:  # 僅當有更新記錄時才檢查時間差
        current_time = timezone.now()
        time_diff = current_time - db_updatetime.updatetime

        if function_key == "OffStreetPSA" and time_diff < timedelta(seconds=30):
            print(f"⏳ OffStreetPSA 資料在 30 秒內已更新，跳過執行（最後更新於 {db_updatetime.updatetime}）")
            return None
        elif function_key == "OffStreetCP" and time_diff < timedelta(days=10):
            print(f"⏳ OffStreetCP 資料在 10 天內已更新，跳過執行（最後更新於 {db_updatetime.updatetime}）")
            return None

    FunctionURL = API_URL_MAP.get(function_key)
    if not FunctionURL:
        raise ValueError(f"❌ 未支援的功能類型: {function_key}")

    data_url=base_url+FunctionURL+City+format_url
    print(data_url)
    headers = {
        'authorization': 'Bearer ' + token,
        'Accept-Encoding': 'gzip'
    }
    response = requests.get(data_url, headers=headers)
    response.raise_for_status()
    data = response.json()
    # with open(f"{function_key}_{City}.json", 'w', encoding='utf-8') as f:
    #     json.dump(data, f, ensure_ascii=False, indent=4)
    # print(f"✅ 成功儲存為 {function_key}_{City}.json")

    save_to_db(data, function_key,City)
    # 更新或建立 db_updatetime 記錄
    # 更新資料庫與時間記錄
    db_updatetime.updatetime = timezone.now()  # 更新為當前時間
    db_updatetime.save()
    return data

# 要查詢可用OffStreetCP.objects.get(car_park_id="001", city="Taipei")
if __name__ == '__main__':
    try:
        token = get_token()
        data = fetch_data(token,OffStreetCP,"Taipei")

    except Exception as e:
        print("❌ 發生錯誤：", e)
