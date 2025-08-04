from django.shortcuts import render
from utils import tdx_api
from utils.utils import get_merged_data_by_city,haversine,get_city_by_coordinates
from django.http import JsonResponse,HttpResponse,HttpResponseBadRequest
from .models import OffStreetCP, OffStreetPSA
import re


def homepage(request):
    return render(request, 'homepage.html')

def get_location_info(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')

    if not lat or not lon:
        return JsonResponse({'error': '缺少 lat 或 lon'}, status=400)

    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return JsonResponse({'error': 'lat 與 lon 必須為數字'}, status=400)

    city = get_city_by_coordinates(lat, lon)
    if not city:
        return JsonResponse({'error': '無法取得城市名稱'}, status=404)

    return JsonResponse({
        'lat': lat,
        'lon': lon,
        'city': city
    })

def test_view(request):
    return render(request, 'test_parking.html')

#獲取單一Table
def get_parking_data(request):
    table = request.GET.get('table')
    city = request.GET.get('city')

    if not table or not city:
        return HttpResponseBadRequest("缺少參數：table 或 city")

    if table == "OffStreetCP":
        data = OffStreetCP.objects.filter(city=city).values()
    elif table == "OffStreetPSA":
        data = OffStreetPSA.objects.filter(city=city).values()
    else:
        return HttpResponseBadRequest("不支援的 table 名稱")

    return JsonResponse(list(data), safe=False)
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
        if not city:
            return JsonResponse({'error': '缺少 city 參數'}, status=400)

        merged_data = get_merged_data_by_city(city)

        results = []
        for park in merged_data:
            if (park['lat'] is not None and
                park['lon'] is not None and
                park['available_spaces'] is not None and
                park['available_spaces'] > 0
                ):
                distance = haversine(lat, lon, park['lat'], park['lon'])
                park['distance_km'] = round(distance, 2)
                results.append(park)

        # 依距離排序並取前10
        results.sort(key=lambda x: x['distance_km'])
        return JsonResponse({'data': results[:10]})


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
