#!/bin/bash

# Start a simple Python web server for serving HTML Animations
# Chris Joakim, Microsoft, 2019/10/31

echo 'Starting simple web server...'
echo 'Visit this URL with your web browser: http://localhost:3000/web/route_sequential.html'
echo ''

source bin/activate  # activate the python virtual environment

python -m http.server 3000
