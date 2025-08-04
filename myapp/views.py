from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.core.mail import send_mail

from myapp.models import Users
from myapp.forms import LoginForm
import random
import re

# parking space
from utils import tdx_api
from utils.utils import get_merged_data_by_city,haversine

# google map
import pandas as pd
import requests
from django.http import JsonResponse

def normalize_city_name(input_str):
    city_name_map = {
        "台北": "Taipei",
        "臺北": "Taipei",
        "台中": "Taichung",
        "臺中": "Taichung",
        "台東": "Taitung",
        "臺東": "Taitung",
        "台南": "Tainan",
        "臺南": "Tainan",
        "高雄": "Kaohsiung",
        "新北": "NewTaipei",
        "基隆": "Keelung",
        "桃園": "Taoyuan",
        "新竹": "Hsinchu",
        "嘉義": "Chiayi",
        "宜蘭": "YilanCounty",
        "彰化": "ChanghuaCounty",
        "雲林": "YunlinCounty",
        "屏東": "PingtungCounty",
        "花蓮": "HualienCounty",
        "金門": "KinmenCounty"
    }

    for key, value in city_name_map.items():
        if key in input_str:
            return value
    return None  # 沒找到對應城市


def get_coordinates(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json',
        'limit': 1,
        'addressdetails' : 1
    }
    headers = {
        'User-Agent': 'your-app-name/1.0'
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])

            # 嘗試取得 city，若沒有則依序嘗試 town、village、county
            address_details = data[0].get('address', {})
            city = (
                address_details.get('city') or
                address_details.get('town') or
                address_details.get('village') or
                address_details.get('county') or
                'Unknown'
            )
            #print("========= city =========")
            if city:
                city = normalize_city_name(city)
            #print(city)
            return lat, lon, city
    except:
        return None, None, None

def map(request):
    address = request.GET.get('address')
    result_list = []
    center = None
    rcity = ''

    if address:
        lat, lon, rcity = get_coordinates(address)
        if lat and lon:
            center = {'lat': lat, 'lon': lon}

            # 載入停車 JSON（你可改成 API 或檔案）
            df = pd.read_json('parking.json')
            parking_df = pd.json_normalize(df['ParkingAvailabilities'])

            # 篩選有位置資料且距離輸入地址 < 1 公里
            def haversine(row):
                from math import radians, sin, cos, sqrt, atan2
                R = 6371
                dlat = radians(row['Lat'] - lat)
                dlon = radians(row['Lng'] - lon)
                a = sin(dlat/2)**2 + cos(radians(lat)) * cos(radians(row['Lat'])) * sin(dlon/2)**2
                return R * 2 * atan2(sqrt(a), sqrt(1-a))

            parking_df = parking_df.dropna(subset=['Lat', 'Lng'])
            parking_df['distance_km'] = parking_df.apply(haversine, axis=1)
            nearby = parking_df[parking_df['distance_km'] <= 1.0]  # 1公里內

            result_list = nearby[[
                'CarParkName.Zh_tw', 'TotalSpaces', 'AvailableSpaces', 'Lat', 'Lng'
            ]].rename(columns={
                'CarParkName.Zh_tw': 'name',
                'TotalSpaces': 'total',
                'AvailableSpaces': 'available',
                'Lat': 'lat',
                'Lng': 'lng'
            }).to_dict(orient='records')

    return render(request, 'map.html', {
        'rcity': rcity,
        'address': address,
        'center': center,
        'results': result_list
    })

def geocode_address(request):
    address = request.GET.get('address')
    if not address:
        return JsonResponse({'error': '缺少 address'}, status=400)

    lat, lon, rcity = get_coordinates(address)
    if lat and lon:
        return JsonResponse({'lat': lat, 'lon': lon, 'city': rcity}, content_type="application/json")
    else:
        return JsonResponse({'error': '找不到位置'}, status=404)

def test_view(request):
    return render(request, 'test_parking.html')

#獲得整合 停車場基本資料以及實時停車位的資料(From DB)
def get_merged_parking_data(request):
    city = request.GET.get('city')
    if not city:
        return JsonResponse({'error': '缺少 city 參數'}, status=400)

    merged_data = get_merged_data_by_city(city)
    return JsonResponse({'data': merged_data})

#更新停車場基本資料以及實時停車位
def update_PSA_CP(request):
    token = tdx_api.get_token()
    city = request.GET.get('city')
    tdx_api.fetch_data(token,"OffStreetPSA",city)
    tdx_api.fetch_data(token,"OffStreetCP",city)
    return HttpResponse(status=204)

#查詢距離自己的座標最近的10筆，且剩餘車位大於0
def nearby_parking(request):
    try:
        lat = float(request.GET.get('lat'))
        lon = float(request.GET.get('lon'))
        city = request.GET.get('city')
        print(f'lat:{lat}')
        print(f'lon:{lon}')
        print(f'city:{city}')

        if not city:
            return JsonResponse({'error': '缺少 city 參數'}, status=400)

        merged_data = get_merged_data_by_city(city)
        print(merged_data)

        results = []
        for park in merged_data:
            if (park['lat'] is not None and
                park['lon'] is not None and
                park['available_spaces'] is not None and
                park['available_spaces'] > 0
                ):
                distance = haversine(lat, lon, park['lat'], park['lon'])
                park['distance_km'] = round(distance, 2)
                fare_description = park.get('faredescription', '')
                fee = extract_hourly_fee(fare_description)
                if fee is not None:
                    park['hourly_fee'] = fee
                results.append(park)

        # 依距離排序並取前10
        results.sort(key=lambda x: x['distance_km'])
        return JsonResponse({'data': results[:10]}, content_type="application/json")

    except (TypeError, ValueError):
        return JsonResponse({'error': '請提供正確的經緯度 lat 與 lon'}, status=400)

def extract_hourly_fee(fare_description):
    if not fare_description:
        return None

    # 優先順序 1：??元/時（例如：40元/時、20元/時）
    match = re.search(r'(\d{2})元/時', fare_description)
    if match:
        return int(match.group(1))

    # 優先順序 2：?元（例如：10元、50元）
    match = re.search(r'(\d{2})元', fare_description)
    if match:
        return int(match.group(1))

    # 優先順序 3：第一個出現的數字
    match = re.search(r'(\d+)', fare_description)
    if match:
        return int(match.group(1))

    # 找不到就回傳 0
    return None

def cheapest_nearby_parking(request):
    try:
        lat = float(request.GET.get('lat'))
        lon = float(request.GET.get('lon'))
        city = request.GET.get('city')
        if not city:
            return JsonResponse({'error': '缺少 city 參數'}, status=400)

        merged_data = get_merged_data_by_city(city)

        results = []
        for park in merged_data:
            if (park['lat'] is not None and
                park['lon'] is not None and
                park['available_spaces'] is not None and
                park['available_spaces'] > 0):

                distance = haversine(lat, lon, park['lat'], park['lon'])
                park['distance_km'] = round(distance, 2)

                fare_description = park.get('faredescription', '')
                fee = extract_hourly_fee(fare_description)
                if fee is not None:
                    park['hourly_fee'] = fee
                    results.append(park)

        # 距離排序取前30
        results.sort(key=lambda x: x['distance_km'])
        top30 = results[:30]

        # 再依每小時費用排序取前10
        cheapest10 = sorted(top30, key=lambda x: x['hourly_fee'] if x['hourly_fee'] is not None else float('inf'))[:10]
        return JsonResponse({'data': cheapest10})

    except (TypeError, ValueError):
        return JsonResponse({'error': '請提供正確的經緯度 lat 與 lon'}, status=400)

