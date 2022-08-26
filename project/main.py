from flask import Flask, jsonify, request, Blueprint
from flask_sqlalchemy import SQLAlchemy

from . import db
from . import app
from datetime import datetime, timedelta

from .models import Place, Pop, Trait, Belief

from .models import humanize_string, dehumanize_string

import requests

import secrets
import random

from .api import acceptable_job_industry_list

main = Blueprint('main_blueprint', __name__)

running_where = "local"
if running_where == "local":
    site_url = "http://0.0.0.0:6688"
else:
    site_url = "https://popworld.herokuapp.com"


@main.route('/')
def index():
    return 'Welcome to popsim'


@main.route('/setup_places')
def setup_places():

    # Create a new places

    place_list = [
        {'name': 'Alabama', 'code': 'AL'},
        {'name': 'Alaska', 'code': 'AK'},
        {'name': 'Arizona', 'code': 'AZ'},
        {'name': 'Arkansas', 'code': 'AR'},
        {'name': 'California', 'code': 'CA'},
        {'name': 'Colorado', 'code': 'CO'},
        {'name': 'Connecticut', 'code': 'CT'},
        {'name': 'Delaware', 'code': 'DE'},
        {'name': 'Florida', 'code': 'FL'},
        {'name': 'Georgia', 'code': 'GA'},
        {'name': 'Hawaii', 'code': 'HI'},
        {'name': 'Idaho', 'code': 'ID'},
        {'name': 'Illinois', 'code': 'IL'},
        {'name': 'Indiana', 'code': 'IN'},
        {'name': 'Iowa', 'code': 'IA'},
        {'name': 'Kansas', 'code': 'KS'},
        {'name': 'Kentucky', 'code': 'KY'},
        {'name': 'Louisiana', 'code': 'LA'},
        {'name': 'Maine', 'code': 'ME'},
        {'name': 'Maryland', 'code': 'MD'},
        {'name': 'Massachusetts', 'code': 'MA'},
        {'name': 'Michigan', 'code': 'MI'},
        {'name': 'Minnesota', 'code': 'MN'},
        {'name': 'Mississippi', 'code': 'MS'},
        {'name': 'Missouri', 'code': 'MO'},
        {'name': 'Montana', 'code': 'MT'},
        {'name': 'Nebraska', 'code': 'NE'},
        {'name': 'Nevada', 'code': 'NV'},
        {'name': 'New Hampshire', 'code': 'NH'},
        {'name': 'New Jersey', 'code': 'NJ'},
        {'name': 'New Mexico', 'code': 'NM'},
        {'name': 'New York', 'code': 'NY'},
        {'name': 'North Carolina', 'code': 'NC'},
        {'name': 'North Dakota', 'code': 'ND'},
        {'name': 'Ohio', 'code': 'OH'},
        {'name': 'Oklahoma', 'code': 'OK'},
        {'name': 'Oregon', 'code': 'OR'},
        {'name': 'Pennsylvania', 'code': 'PA'},
        {'name': 'Rhode Island', 'code': 'RI'},
        {'name': 'South Carolina', 'code': 'SC'},
        {'name': 'South Dakota', 'code': 'SD'},
        {'name': 'Tennessee', 'code': 'TN'},
        {'name': 'Texas', 'code': 'TX'},
        {'name': 'Utah', 'code': 'UT'},
        {'name': 'Vermont', 'code': 'VT'},
        {'name': 'Virginia', 'code': 'VA'},
        {'name': 'Washington', 'code': 'WA'},
        {'name': 'West Virginia', 'code': 'WV'},
        {'name': 'Wisconsin', 'code': 'WI'},
        {'name': 'Wyoming', 'code': 'WY'},
    ]

    successes = 0
    failures = 0

    for place in place_list:
        r = requests.post(
            site_url + '/places/',
            json={
                'name': place['name'],
                'two_letter_code': place['code'].lower()
            }
        )
        
        if r.status_code == 201:
            successes += 1
        else:
            failures += 1
            
        
    return jsonify({
        'successes': successes,
        'failures': failures
    })

