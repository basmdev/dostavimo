from decimal import Decimal

from yandex_geocoder import Client

from config import REGION, YANDEX_API_KEY

client = Client(YANDEX_API_KEY)


# Получить ссылку с маршрутом
def get_coordinates(start_address: str, end_address: str):
    start_coordinates = client.coordinates(REGION + start_address)
    end_coordinates = client.coordinates(REGION + end_address)
    yandex_url = f"https://yandex.ru/maps/?rtext={start_coordinates[1]},{start_coordinates[0]}~{end_coordinates[1]},{end_coordinates[0]}&rtt=auto"
    return yandex_url


# Получить координаты одного адреса
def get_coordinates_for_one_address(address: str):
    coordinates = client.coordinates(REGION + address)
    coordinates = f"{coordinates[0]},{coordinates[1]}"
    return coordinates


# Получить изображение карты с метками
def get_static_map_url(start_coordinates: str, end_coordinates: str):
    center_latitude = (
        Decimal(start_coordinates.split(",")[0])
        + Decimal(end_coordinates.split(",")[0])
    ) / 2
    center_longitude = (
        Decimal(start_coordinates.split(",")[1])
        + Decimal(end_coordinates.split(",")[1])
    ) / 2
    static_map_url = f"https://static-maps.yandex.ru/1.x/?ll={center_latitude},{center_longitude}&size=600,400&z=13&l=map&pt={start_coordinates},pm2al~{end_coordinates},pm2bl"
    return static_map_url
