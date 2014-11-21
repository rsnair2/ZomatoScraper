#
#   Zomato Web Bot
#   description: scrapes information about restaurants from http://zomato.com and
#   saves information in JSON format to a file
#
__author__ = 'rsnair2'


import requests
from parse import *
import json
import time


def construct_URL(city, area, page):
    return "https://www.zomato.com/%s/restaurants?q=%s&page=%s" % (city, area, str(page))


def find_restaurants(city, area, max_page):
    """
        finds all the restaurants listed by Zomato for the given city, area and we keep looking for listings
        up to max_page - 1.
    """
    restaurants = set()
    for i in range(1, int(max_page)):
        parser = ZomatoFindRestaurantsParser()
        parser.restaurants = set()

        URL = construct_URL(city=city, area=area, page=i)
        response = requests.get(URL).text

        parser.feed(response)
        restaurants = restaurants.union(parser.restaurants)

    return restaurants


def zomato_restaurant_data(URL):
    """
        given the URL of a restaurant's info page on Zomato, we find out information about it. Included are the
        following keys:

        title - title of restaurant
        phone_no
        address
        locality
        ratings
        features
        cuisine
        price
        timings
        accepted - cards accepted?
        menu - list of urls to the menu images
    """
    zomato_page = requests.get(URL).text

    parser = ZomatoRestaurantsDataParser()
    parser.feed(zomato_page)

    d = parser.info

    if d.get('menu') and len(d['menu']) == 1:
        menu_parser = ZomatoMenuParser("num_pages")
        menu_URL = d['menu'].pop()
        menu_page = requests.get(menu_URL).text
        menu_parser.feed(menu_page)
        num_pages = int(menu_parser.page)
        menu_URL = menu_URL.replace("#tabtop", "?page=")
        menu_images = set()

        for i in range(1, num_pages + 1):
            menu_parser = ZomatoMenuParser()
            page = requests.get(menu_URL + str(i)).text
            menu_parser.feed(page)
            menu_images.add(str(menu_parser.menu_image))

        d['menu'] = list(menu_images)

    else:
        d['menu'] = list()
        print "Error: I am being lazy! I don't anticipate this situation, " \
              "but if it does happen, the menu URLs will not be loaded."

    return d


def save_json(restaurant_info, file_name):
    """
        saves specified restaurant info to filename in compliance with json spec
        each restaurant info entry is a dictionary and is added to a list and saved
    """
    try:
        f = open(file_name, "r+")
        data = json.load(f)
        f.close()
    except (IOError, ValueError):
        data = list()

    data.append(restaurant_info)
    f = open(file_name, "w+")
    json.dump(data, f)
    f.close()


def main():
    # just add the city, area, max_page sets here to expand your queries
    queries = [
        ("mumbai", "powai", 2),
        ("mumbai", "bandra", 2),
    ]

    average = 0
    restaurants = list()

    for query in queries:
        restaurants += find_restaurants(query[0], query[1], query[2])

    print "Number of restaurants: %s" % str(len(restaurants))

    for restaurant in restaurants:
        start = time.time()
        info = zomato_restaurant_data(restaurant)
        save_json(info, "zomato-db.json")
        average = (time.time() - start + average) / 2
        print "%.2f" % average + " seconds\t" + "%.2f" % (len(restaurants) * average) + " seconds remaining\t" + \
              restaurant
              

if __name__ == "__main__":
    main()