from flask import Flask, jsonify, request, Blueprint
from flask_sqlalchemy import SQLAlchemy

from . import db
from . import app
from datetime import datetime, timedelta

from .models import Place, Pop, Trait, Belief

from .models import humanize_string, dehumanize_string

from .models import Place

import requests

import secrets
import random

from . import site_url

from .api import acceptable_job_industry_list, acceptable_trait_list, acceptable_belief_list

simulator = Blueprint('simulator_blueprint', __name__)


@simulator.get('/simulate/create_pop/<place_id>')
def create_random_pop(place_id):

    # Create a random pop in the database

    # Generate random values for the pop
    gender = random.choice(['male', 'female'])
    age = random.randint(18,70)
    wealth = random.randint(0,5)

    # Work out the pop's likely job
    if wealth == 0:
        job = 'unemployed'
    elif age > 70:
        job = 'retired'
    else:
        job = random.choice(acceptable_job_industry_list)

    # Send the pop create request
    url = f"{site_url}/pops"

    pop_create_request = requests.post(
        url,
        json=
            {
                'place_id': place_id,
                'gender': gender,
                'age': age,
                'wealth': wealth,
                'job': job
            }
    )

    if pop_create_request.status_code != 200:
        return pop_create_request.json()

    # Assuming the pop is successfully created get the new pop details
    new_pop = pop_create_request.json()['pop']

    # Add some traits to the pop ensuring that none are duplicates
    new_pop_traits = []
    for i in range(0, random.randint(2,5)):
        trait = random.choice(acceptable_trait_list)
        if trait not in new_pop_traits:
            new_pop_traits.append(trait)

    # Send the request to add those traits
    url = f"{site_url}/pops/{new_pop['id']}/traits/"
    for trait in new_pop_traits:
        add_trait_request = requests.post(
            url,
            json={'trait_name': trait}
        )
        if add_trait_request.status_code != 200:
            # log an error
            pass

    return pop_create_request.json()


@simulator.get('/simulate/create_lots_of_pops/<place_id>/<how_many>')
def create_lots_of_pops(place_id, how_many):

    if place_id != 'everywhere':

        for i in range(0, int(how_many)):
            create_random_pop(place_id)

    if place_id == 'everywhere':
        all_places = Place.query.all()

        for place in all_places:
            print ("Creating " + str(how_many) + " pops in " + place.name)
            for i in range(0, int(how_many)):
                create_random_pop(place.id)

    return "Done"
