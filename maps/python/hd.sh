#!/bin/bash

# Home Depot ATL-area Store Route processing
# Chris Joakim, Microsoft, 2019/10/31

echo '==='
echo 'parse_stores_txt ...'
python main.py parse_stores_txt

echo '==='
echo 'get_store_geos ...'
python main.py get_store_geos --invoke

echo '==='
echo 'merge_store_geos ...'
python main.py merge_store_geos

area_code=770

echo '==='
echo 'sequential calculate_route and parse_route ...'
python main.py calculate_and_map_route $area_code --invoke

echo '==='
echo 'optimal calculate_route and parse_route ...'
python main.py calculate_and_map_route $area_code --invoke --best_order
