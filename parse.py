#
#   parse: HTML parsers for Zomato
#   private implementation
#
__author__ = 'rsnair2'


from HTMLParser import HTMLParser
import re


# helpers
def find_zone(attrs, key, val):
    for attr in attrs:
        if len(attr) >= 2 and attr[0].find(key) != -1 and attr[1].find(val) != -1:
            return True
    return False


def get_val(attrs, key):
    for attr in attrs:
        if len(attr) >= 2 and attr[0].find(key) != -1:
            return attr[1]


# parsers
class ZomatoFindRestaurantsParser(HTMLParser):

    restaurants = set()

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            if find_zone(attrs, "class", "result-title"):
                restaurant = get_val(attrs, "href")
                self.restaurants.add(restaurant)

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        pass


class ZomatoRestaurantsDataParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.info = dict()
        self.controls = dict()
        self.controls['title'] = {'status': 0, 'tag': 'span', 'key': 'itemprop', 'val': 'name', 'data': 1}
        self.controls['phone_no'] = {'status': 0, 'tag': 'span', 'key': 'class', 'val': 'tel', 'data': 2}
        self.controls['address'] = {'status': 0, 'tag': 'h2', 'key': 'class', 'val': 'res-main-address-text', 'data': 1}
        self.controls['locality'] = {'status': 0, 'tag': 'strong', 'key': 'itemprop', 'val': 'addressLocality', 'data': 1}
        self.controls['ratings'] = {'status': 0, 'tag': 'div', 'key': 'itemprop', 'val': 'ratingValue', 'data': 1}
        self.controls['features'] = {'status': 0, 'tag': 'div', 'key': 'class', 'val': 'res-info-feature-text', 'data': 1, 'type': 'list'}
        self.controls['cuisine'] = {'status': 0, 'tag': 'a', 'key': 'itemprop', 'val': 'servesCuisine', 'data': 1}
        self.controls['price'] = {'status': 0, 'tag': 'span', 'key': 'itemprop', 'val': 'priceRange', 'data': 4}
        self.controls['timings'] = {'status': 0, 'tag': 'span', 'key': 'class', 'val': "res-info-timings", 'data': 1}
        self.controls['accepted'] = {'status': 0, 'tag': 'span', 'key': 'itemprop', 'val': 'paymentAccepted', 'data': 1}
        self.controls['menu'] = {'status': 0, 'tag': 'a', 'key': 'class', 'val': 'res-info-thumbs', 'data': 1}
        self.controls['coords'] = {'status': 0, 'tag': 'img', 'key': 'data-original', 'val': 'https://maps.googleapis.com/maps/api/staticmap?', 'data': 1}

    def handle_starttag(self, tag, attrs):
        if self.controls['price']['status'] >= 1:
            self.controls['price']['status'] += 1

        for key in self.controls:
            control = self.controls[key]
            if tag == control['tag'] and find_zone(attrs, control['key'], control['val']):
                control['status'] += 1

        if self.controls['menu']['status'] == 1:
            self.controls['menu']['status'] = 0
            if not self.info.get('menu'):
                self.info['menu'] = set()
            if get_val(attrs, 'href').find('menu') != -1:
                self.info['menu'].add(str(get_val(attrs, 'href')))

        if self.controls['coords']['status'] == 1:
            static_map = get_val(attrs, 'data-original')
            coords = static_map.split('center=')[1].split('&')[0].split(',')
            self.info['coords'] = (coords[0], coords[1])
            self.controls['coords']['status'] = 0


    def handle_endtag(self, tag):
        if tag == "span" and self.controls['price']['status'] == 3:
            self.controls['price']['status'] += 1

    def handle_data(self, data):
        for key in self.controls:
            control = self.controls[key]
            if control['status'] == control['data']:
                control['status'] = 0

                data = data.strip("\n")
                data = data.strip(" ")
                data = str(data)
                if control.get('type') == 'list':
                    if not self.info.get(key):
                        self.info[key] = list()
                    self.info[key].append(data)
                else:
                    self.info[key] = data


class ZomatoMenuParser(HTMLParser):

    def __init__(self, function=None):
        HTMLParser.__init__(self)
        self.function = function
        self.pagination_control = False
        self.max_page = False
        self.page = 0
        self.menu_image = None
        self.menu_div = False

    def handle_starttag(self, tag, attrs):
        if self.function == "num_pages":
            if tag == "ul" and find_zone(attrs, "class", "pagination-control"):
                self.pagination_control = True

            if self.pagination_control and tag == "a":
                self.max_page = True

        else:
            if tag == "div" and find_zone(attrs, "id", "menu-image"):
                self.menu_div = True

            if self.menu_div and tag == "img":
                self.menu_div = False
                self.menu_image = get_val(attrs, "src")

    def handle_endtag(self, tag):
        if self.pagination_control and tag == "ul":
            self.pagination_control = False

    def handle_data(self, data):
        if self.function == "num_pages":
            if self.max_page:
                self.max_page = False
                if re.findall(r'\d+', data):
                    self.page = str(re.findall(r'\d+', data)[0])

