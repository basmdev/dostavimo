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
    coordinates = f"{coordinates[1]},{coordinates[0]}"
    return coordinates
