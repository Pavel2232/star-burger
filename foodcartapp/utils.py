import requests
from geopy.distance import distance
from star_burger.settings import env
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'star_burger.settings')

import django

django.setup()

from geolocation.models import Location


def fetch_coordinates(address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    try:
        response = requests.get(base_url, params={
            "geocode": address,
            "apikey": env('YANDEX_GEO_API_KEY'),
            "format": "json",
        })
        response.raise_for_status()
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']

        if not found_places:
            return None

        most_relevant = found_places[0]
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
        return lon, lat
    except Exception as err:
        print(err)


def get_distance_by_restaurants(orders):
    for order in orders:
        ore = []
        for restaurants in order.get_restaurants:
            or_lon_lat = ()
            res_lon_lat = ()
            if not Location.objects.filter(address_name__exact=order.address):
                order_addres = fetch_coordinates(order.address)
                order_location = Location.objects.get_or_create(
                    address_name=order.address,
                    long=order_addres[0],
                    lat=order_addres[1])
                or_lon_lat = order_location.my_coordinates
            if not Location.objects.filter(address_name__exact=restaurants.address):
                restaurants_address = fetch_coordinates(restaurants.address)
                restaurants_location = Location.objects.get_or_create(
                    address_name=restaurants.address,
                    long=restaurants_address[0],
                    lat=restaurants_address[1])
                res_lon_lat = restaurants_location.my_coordinates

            order_loc = Location.objects.get(address_name__exact=order.address)
            rest_loc = Location.objects.get(address_name__exact=restaurants.address)
            space = distance(rest_loc.my_coordinates, order_loc.my_coordinates).km
            ore.append((restaurants, round(space, 2)))

        order.get_restaurants = sorted(ore, key=lambda space: space[1])

    return orders
