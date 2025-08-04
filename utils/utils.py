from parking_space.models import OffStreetCP, OffStreetPSA
import math
from geopy.geocoders import Nominatim

def normalize_city_name(input_str):
    city_name_map = {
        "台北": "Taipei", "臺北": "Taipei", "台中": "Taichung", "臺中": "Taichung",
        "台東": "Taitung", "臺東": "Taitung", "台南": "Tainan", "臺南": "Tainan",
        "高雄": "Kaohsiung", "新北": "NewTaipei", "基隆": "Keelung", "桃園": "Taoyuan",
        "新竹": "Hsinchu", "嘉義": "Chiayi", "宜蘭": "YilanCounty", "彰化": "ChanghuaCounty",
        "雲林": "YunlinCounty", "屏東": "PingtungCounty", "花蓮": "HualienCounty", "金門": "KinmenCounty"
    }
    for keyword, eng_name in city_name_map.items():
        if keyword in input_str:
            return eng_name
    return None

def get_city_by_coordinates(lat, lon):
    geolocator = Nominatim(user_agent="parking_sys")
    location = geolocator.reverse((lat, lon), language='zh-TW')

    if location and location.raw.get('address'):
        address = location.raw['address']
        city = address.get('city') or address.get('county') or address.get('state')
        return normalize_city_name(city)
    return None

#獲取整合過後的資料
def get_merged_data_by_city(city):
    cp_data = OffStreetCP.objects.filter(city=city)
    psa_data = OffStreetPSA.objects.filter(city=city)

    psa_dict = {
        (p.car_park_id, p.city): {
            'total_spaces': p.total_spaces,
            'available_spaces': p.available_spaces
        }
        for p in psa_data
    }

    merged_data = []
    for cp in cp_data:
        key = (cp.car_park_id, cp.city)
        psa_info = psa_dict.get(key, {})
        merged_data.append({
            'car_park_id': cp.car_park_id,
            'name': cp.name,
            'description': cp.description,
            'faredescription': cp.faredescription,
            'address': cp.address,
            'lat': cp.position_lat,
            'lon': cp.position_lon,
            'emergency_phone': cp.emergency_phone,
            'total_spaces': psa_info.get('total_spaces'),
            'available_spaces': psa_info.get('available_spaces'),
            
        })
    return merged_data

# 計算兩點距離 (哈夫辛公式)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # 地球半徑，單位為公里
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # 回傳距離（公里）