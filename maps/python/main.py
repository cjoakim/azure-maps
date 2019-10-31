"""
Usage:
    python main.py parse_stores_txt
    python main.py get_store_geos --invoke
    python main.py merge_store_geos
    python main.py calculate_and_map_route 770 --invoke --best_order
    python main.py parse_route data/route-770-best-order.json
Options:
    -h --help     Show this screen.
    --version     Show version.
"""

# Chris Joakim, Microsoft, 2019/10/31

import collections
import csv
import json
import random
import sys
import time
import os
import traceback
import urllib.parse

import arrow
import requests

from docopt import docopt

from jinja2 import Template

from src.joakim import cosmos
from src.joakim import fs

VERSION='2019/10/28'

class Main(object):

    def __init__(self):
        self.point1 = None
        self.point2 = None
        self.cosmosdb_insert_sleep_seconds = 0.1
 
    def print_options(self, msg):
        print(msg)
        arguments = docopt(__doc__, version=VERSION)
        print(arguments)

    def write_text_file(self, outfile, txt):
        return fs.FSUtil().write_text_file(outfile, txt)

    def hd_ga_stores_filename(self, suffix='json'):
        return 'data/hd-ga-stores.{}'.format(suffix.lower())

    def hd_ga_stores_with_geo_filename(self, area_code='all'):
        return 'data/hd-ga-stores-{}-with-geo.json'.format(area_code)

    def map_data_file(self, map_type):
        return 'data/map_data_{}.json'.format(map_type)

    def invoke_search_address_api(self, address):
        try:
            key = os.environ['AZURE_MAPS_KEY']
            template = 'https://atlas.microsoft.com/search/address/json?subscription-key={}&api-version=1.0&query={}'
            url = template.format(key, address)
            print('URL: {}'.format(url))
            if self.invoke():
                r = requests.get(url)
                return r.json()
            else:
                return {}
        except:
            print("EXCEPTION:\n{}\n".format(sys.exc_info()[0]))
            traceback.print_exc(file=sys.stdout)
            return {}

    def invoke_route_directions_api(self, query, curr_traffic, best_order):
        # see https://docs.microsoft.com/en-us/rest/api/maps/route/getroutedirections
        try:
            key = os.environ['AZURE_MAPS_KEY']
            template, url = '', ''

            if best_order:
                template = 'https://atlas.microsoft.com/route/directions/json?subscription-key={}&api-version=1.0&query={}&traffic={}&computeBestOrder=true&routeType=shortest'
                url = template.format(key, query, curr_traffic) 
            else:
                template = 'https://atlas.microsoft.com/route/directions/json?subscription-key={}&api-version=1.0&query={}&traffic={}'
                url = template.format(key, query, curr_traffic)
            print('URL: {}'.format(url))
            
            # https://atlas.microsoft.com/route/directions/{format}?subscription-key={subscription-key}
            # &api-version=1.0
            # &query={query}
            # &maxAlternatives={maxAlternatives}
            # &alternativeType={alternativeType}
            # &minDeviationDistance={minDeviationDistance}
            # &arriveAt={arriveAt}
            # &departAt={departAt}
            # &minDeviationTime={minDeviationTime}
            # &instructionsType={instructionsType}
            # &language={language}
            # &computeBestOrder={computeBestOrder}
            # &routeRepresentation={routeRepresentation}
            # &computeTravelTimeFor={computeTravelTimeFor}
            # &vehicleHeading={vehicleHeading}
            # &report={report}
            # &sectionType={sectionType}
            # &vehicleAxleWeight={vehicleAxleWeight}
            # &vehicleWidth={vehicleWidth}
            # &vehicleHeight={vehicleHeight}
            # &vehicleLength={vehicleLength}
            # &vehicleMaxSpeed={vehicleMaxSpeed}
            # &vehicleWeight={vehicleWeight}
            # &vehicleCommercial={vehicleCommercial}
            # &windingness={windingness}
            # &hilliness={hilliness}
            # &travelMode={travelMode}
            # &avoid={avoid}
            # &traffic={traffic}
            # &routeType={routeType}
            # &vehicleLoadType={vehicleLoadType}
            # &vehicleEngineType={vehicleEngineType}
            # &constantSpeedConsumptionInLitersPerHundredkm={constantSpeedConsumptionInLitersPerHundredkm}
            # &currentFuelInLiters={currentFuelInLiters}
            # &auxiliaryPowerInLitersPerHour={auxiliaryPowerInLitersPerHour}
            # &fuelEnergyDensityInMJoulesPerLiter={fuelEnergyDensityInMJoulesPerLiter}
            # &accelerationEfficiency={accelerationEfficiency}
            # &decelerationEfficiency={decelerationEfficiency}
            # &uphillEfficiency={uphillEfficiency}
            # &downhillEfficiency={downhillEfficiency}
            # &constantSpeedConsumptionInkWhPerHundredkm={constantSpeedConsumptionInkWhPerHundredkm}
            # &currentChargeInkWh={currentChargeInkWh}
            # &maxChargeInkWh={maxChargeInkWh}
            # &auxiliaryPowerInkW={auxiliaryPowerInkW}

            if self.invoke():
                r = requests.get(url)
                return r.json()
            else:
                return {}
        except:
            print("EXCEPTION:\n{}\n".format(sys.exc_info()[0]))
            traceback.print_exc(file=sys.stdout)
            return {}

    def prune_response_fields(self, resp_obj):
        for key in self.unwanted_response_fields():
            if resp_obj[key]:
                del resp_obj[key]
        return resp_obj

    def unwanted_response_fields(self):
        return 'copyright,privacy'.split(',')

    # methods to process the command-line args:

    def cli_flag_arg(self, flag):
        for arg in sys.argv:
            if arg == flag:
                return True
        return False

    def invoke(self):
        return self.cli_flag_arg('--invoke')

    # def cosmos(self):
    #     for arg in sys.argv:
    #         if arg == '--cosmos':
    #             return True
    #     return False

    # def html(self):
    #     for arg in sys.argv:
    #         if arg == '--html':
    #             return True
    #     return False

    # def db_name(self):
    #     for idx, arg in enumerate(sys.argv):
    #         if arg == '--db':
    #             return sys.argv[idx + 1]
    #     return None

    # def coll_name(self):
    #     for idx, arg in enumerate(sys.argv):
    #         if arg == '--coll':
    #             return sys.argv[idx + 1]
    #     return None

    # def persist_to_cosmosdb(self, p1_idx, p2_idx, data):
    #     db = self.db_name()
    #     coll = self.coll_name()
    #     print('db: {} coll: {}'.format(db, coll))
    #     util = cosmos.DocDbUtil()
    #     route = data['maps_data']['routes']
    #     for route_idx, route in enumerate(data['maps_data']['routes']):
    #         for leg_idx, leg in enumerate(route['legs']):
    #             for point_idx, point in enumerate(leg['points']):
    #                 if point_idx < 9999:
    #                     doc = {}
    #                     doc['pk']         = p1_idx
    #                     doc['p1_idx']     = p1_idx
    #                     doc['p2_idx']     = p2_idx
    #                     doc['route_name'] = self.route_name()
    #                     doc['route_idx']  = route_idx
    #                     doc['leg_idx']    = leg_idx
    #                     doc['point_idx']  = point_idx
    #                     doc['location']   = self.point_geo_json(point)
    #                     newdoc = util.insert_document(db, coll, doc)
    #                     print(json.dumps(newdoc, sort_keys=True, indent=2)) 
    #                     time.sleep(self.cosmosdb_insert_sleep_seconds)

    # def route_name(self):
    #     n1 = self.point1[2]
    #     n2 = self.point2[2]
    #     return '{} to {}'.format(n1, n2)

    # def point_geo_json(self, point):
    #     data = {}
    #     data['type'] = 'Point'
    #     data['coordinates'] = [point['longitude'], point['latitude']] 
    #     return data

    def parse_stores_txt(self):
        stores, store, store_num = list(), dict(), 0
        infile = self.hd_ga_stores_filename('txt')
        outfile = self.hd_ga_stores_filename('json')
        lines, seq = fs.FSUtil().read_text_file_lines(infile), 0
        for line in lines:
            if line.strip() == '---':
                store = dict()
                store_num = store_num + 1
                store['store_num'] = store_num
                stores.append(store)
                seq = 1
            else:
                if seq == 1:
                    store['name'] = line.strip()
                    seq = 2
                elif seq == 2:
                    store['street'] = line.strip()
                    seq = 3
                elif seq == 3:
                    store['city_state_zip'] = line.strip()
                    tokens = line.split()
                    if (len(tokens) < 3):
                        store['city_state_zip_invalid'] = true
                    else:
                        store['zip'] = tokens.pop()
                        store['state'] = tokens.pop()
                        store['city'] = (" ".join(tokens)).strip()
                    seq = 4
                elif seq == 4:
                    store['phone'] = line.strip()
                    store['area_code'] = line.strip()[1:4]
                    s  = store['street']
                    c  = store['city']
                    st = store['state']
                    z  = store['zip']
                    store['search_address'] = "{} {} {} {}".format(s,c,st,z)
                    seq = 99
        fs.FSUtil().write_obj_as_json_file(outfile, stores)

    def get_store_geos(self):
        infile = self.hd_ga_stores_filename()
        fsUtil = fs.FSUtil()
        stores = fsUtil.read_json_file(infile)
        address_key = 'search_address'
        for idx, store in enumerate(stores):
            if idx < 999:
                if address_key in store.keys():
                    search_address = store[address_key]
                    quoted_address = urllib.parse.quote_plus(search_address)
                    resp_json = self.invoke_search_address_api(quoted_address)
                    resp_json['search_address'] = search_address
                    json_file = self.search_address_filename_for_store(store)
                    fsUtil.write_obj_as_json_file(json_file, resp_json)
                else:
                    print('{} key missing in store'.format(address_key))
                    print(store)

    def search_address_filename_for_store(self, store):
        store_num = store['store_num']
        store_name = store['name']
        s = 'search-address-{}-{}.json'.format(store_num, store_name)
        return 'data/' + s.replace(',','').replace(' ','-').replace('/','-')

    def merge_store_geos(self):
        infile = self.hd_ga_stores_filename()
        outfile = self.hd_ga_stores_with_geo_filename()
        fsUtil = fs.FSUtil()
        stores = fsUtil.read_json_file(infile)
        area_codes = dict()
        for idx, store in enumerate(stores):
            area_code = store['area_code']
            area_codes[area_code] = area_code
            if idx < 999:
                geo_file = self.search_address_filename_for_store(store)
                geo_data = fsUtil.read_json_file(geo_file)
                results = geo_data['results']
                search_address = geo_data['search_address']
                location = results[0]['position']
                store['location'] = location
                print("{} results in {} -> {} -> {}".format(len(results), geo_file, search_address, location))
        fsUtil.write_obj_as_json_file(outfile, stores)

        print('distinct area codes: {}'.format(sorted(area_codes.keys())))
        # distinct area codes: ['229', '404', '478', '678', '706', '770', '912']

        for area_code in sorted(area_codes.keys()):
            area_code_store_list = list()
            for idx, store in enumerate(stores):
                if area_code == store['area_code']:
                    area_code_store_list.append(store)
            outfile = self.hd_ga_stores_with_geo_filename(area_code)
            fsUtil.write_obj_as_json_file(outfile, area_code_store_list)

    def calculate_and_map_route(self, area_code):
        print('calculate_and_map_route for {}'.format(area_code))
        infile = self.hd_ga_stores_with_geo_filename(area_code)
        fsUtil = fs.FSUtil()
        stores = fsUtil.read_json_file(infile)
        lat_lon_pairs = list()
        for idx, store in enumerate(stores):
            address = store['search_address']
            location = store['location']
            lat_lon = "{},{}".format(location['lat'], location['lon'])
            lat_lon_pairs.append(lat_lon)
            print("{} -> {}".format(address, lat_lon))
        query = ':'.join(lat_lon_pairs)
        print(query)
        curr_traffic = self.cli_flag_arg('--curr_traffic')
        best_order = self.cli_flag_arg('--best_order')
        resp_data = self.invoke_route_directions_api(query, curr_traffic, best_order)

        # calculate the name of the output file based on CLI parameters
        outfile = 'data/route-{}'.format(area_code)
        htmlfile = 'web/route_sequential.html'
        if best_order:
            outfile = outfile + '-best-order'
            htmlfile = 'web/route_optimized.html'
        outfile = outfile + '.json'
        fsUtil.write_obj_as_json_file(outfile, resp_data)

        self.gen_map(area_code, stores, resp_data, best_order, htmlfile)

    def gen_map(self, area_code, stores, resp_data, best_order, htmlfile):
        print('gen_map: {} {}'.format(area_code, best_order))
        fsUtil = fs.FSUtil()
        resp_data_keys = resp_data.keys()  # ['formatVersion', 'optimizedWaypoints', 'routes']
        map_data, map_waypoints, map_points = dict(), list(), list()
        loc_vars = list()
        map_data['waypoints'] = map_waypoints
        map_data['points'] = map_points
        map_type = 'sequential'
        if best_order:
            map_data['title'] = 'Optimized Route'
            map_type = 'optimized'
        else:
            map_data['title'] = 'Sequential Route'
        map_data['map_type'] = map_type

        hours = float(resp_data['routes'][0]['summary']['travelTimeInSeconds']) / 3600.0
        miles = float(resp_data['routes'][0]['summary']['lengthInMeters']) * 0.000621371
        map_data['hours'] = str(hours)[:6]
        map_data['miles'] = str(miles)[:5]
        map_data['stores'] = stores

        for store_idx, store in enumerate(stores):
            store_num = store_idx + 1
            store['store_num'] = store_num
            lat = store['location']['lat']
            lon = store['location']['lon']
            name = store['name']
            addr = store['search_address']
            color = '#F44B09' # home depot = #F44B09
            loc_vars.append('// {} {} {} {} {}'.format(store_idx, name, addr, lat, lon))
            t = "map.markers.add(new atlas.HtmlMarker(<color: '{}', text: '{}', position: [{}, {}]>));"
            loc_vars.append(t.format(color, store_num, lon, lat).replace('<','{').replace('>','}'))

        routes = resp_data['routes']
        route = routes[0]
        legs = route['legs']
        summary = route['summary']
        print('summary: {}'.format(summary))

        print('legs length: {}'.format(len(legs)))
        sum_lat, sum_lon = 0, 0
        for leg_idx, leg in enumerate(legs):
            points = leg['points']
            for leg_point_idx, point in enumerate(points):
                lon, lat = point['longitude'], point['latitude']
                sum_lat = sum_lat + lat
                sum_lon = sum_lon + lon
                point_array = '[{}, {}]'.format(lon,lat)  # [-80.85447, 35.22552]
                map_points.append(point_array)

        avg_lat = sum_lat / float(len(map_points))
        avg_lon = sum_lon / float(len(map_points))

        fsUtil.write_obj_as_json_file(self.map_data_file(map_type), map_data)

        # generate the html with the jinja2 template 
        map_data['zoom_level'] = 9
        template_text = fs.FSUtil().read_text_file('templates/route.html')
        map_data['key'] = os.environ['AZURE_MAPS_KEY']
        map_data['center_point'] = '{}, {}'.format(avg_lon, avg_lat)
        map_data['path_points'] = ",\n            ".join(map_points)
        map_data['loc_vars'] = "\n                ".join(loc_vars)
        t = Template(template_text)
        html = t.render(map_data)
        fs.FSUtil().write_text_file(htmlfile, html)

    def execute(self):
        if len(sys.argv) > 1:
            func = sys.argv[1].lower()

            if func == 'parse_stores_txt':
                self.parse_stores_txt()
            elif func == 'get_store_geos':
                self.get_store_geos()
            elif func == 'merge_store_geos':
                self.merge_store_geos()
            elif func == 'calculate_and_map_route':
                area_code = sys.argv[2]
                self.calculate_and_map_route(area_code)
            else:
                self.print_options('invalid function')
        else:
            self.print_options('no function given on command-line')


if __name__ == "__main__":
    Main().execute()
