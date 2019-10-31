#!/bin/bash

# Home Depot ATL-area Store Route processing
# Chris Joakim, Microsoft, 2019/10/31

area_code=770

# Just generate the maps
echo '==='
echo 'sequential calculate_route and parse_route ...'
python main.py calculate_and_map_route $area_code --invoke

echo '==='
echo 'optimal calculate_route and parse_route ...'
python main.py calculate_and_map_route $area_code --invoke --best_order
