from yandex_geocoder import Client

from config import REGION, YANDEX_API_KEY

client = Client(YANDEX_API_KEY)


# Выдает координаты адреса
async def get_coordinates(address: str):
    coordinates = client.coordinates(REGION + address)
    return coordinates
