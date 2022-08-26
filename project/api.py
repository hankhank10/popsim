from flask import Flask, jsonify, request, Blueprint
from flask_sqlalchemy import SQLAlchemy

from . import db
from . import app
from datetime import datetime, timedelta

from .models import Place, Pop, Trait, Belief

from .models import humanize_string, dehumanize_string

import secrets
import random

api = Blueprint('api_blueprint', __name__)

acceptable_trait_list = [
    'parent',
    'gun_owner',
    'military_veteran',
    'married',
    'immigrant',
    'car_owner',
    'cyclist',
    'outdoorsy',
    'alcohol_drinker',
    'smoker',
    'drug_taker',
]

acceptable_belief_list = [
    'law_and_order',
    'strong_military',
    'strong_leadership',
    'environment',
    'balanced_budget',
    'economic_growth',
    'social_equality',
    'universal_health_care',
    'equal_rights',
    'equal_opportunity',
    'individual_liberty',
    'freedom_of_speech',
    'freedom_of_press',
    'individual_freedoms',
]

acceptable_job_industry_list = [
    'unemployed',
    'administrative',
    'architecture',
    'engineering',
    'operations',
    'cleaning_and_maintenance',
    'social services',
    'government',
    'technology',
    'education',
    'farming',
    'healthcare',
    'legal',
    'academia',
    'management',
    'construction',
    'military',
    'police',
    'science',
    'retired'
]

wealth_categories = {
    0: "destitute",
    1: "working poor",
    2: "struggling middle class",
    3: "comfortable professionals",
    4: "wealthy",
    5: "rich",
}


##########
# PLACES #
##########

# List all places
@api.get('/places/')
def places_list():
    places = Place.query.all()
    return jsonify(places)


# Create a place
@api.post('/places/')
def places_create():
    content = request.json

    id = content.get('id')
    name = content.get('name')
    two_letter_code = content.get('two_letter_code')

    if id and name:
        return jsonify({'message': 'Must only specify id or name'}), 400

    if not id and not name:
        return jsonify({"message": "Missing data for place."}), 400

    if id:
        place = Place.query.filter_by(id=id).first()
        if place:
            return jsonify({"message": "Place already exists."}), 400
        id = dehumanize_string(id)

    if name:
        place = Place.query.filter_by(name=name).first()
        if place:
            return jsonify({"message": "Place already exists."}), 400
        id = dehumanize_string(name)

    new_place = Place(
        id=id,
        two_letter_code=two_letter_code,
    )
    try:
        db.session.add(new_place)
        db.session.commit()
    except:
        return jsonify({"message": "Database error."}), 500

    return jsonify({
        "message": "Place created.",
        "id": new_place.id
    }), 201


# Get details of a place
@api.get("/places/<id>/")
def places_get(id):
    place = Place.query.filter_by(id=id).first()
    if not place:
        return jsonify({"message": "Place not found."}), 404

    return jsonify(place)


##########
# POPS   #
##########

# List pops
@api.get("/pops/")
def pops_list():
    if 'place_id' in request.args:
        place_id = request.args.get('place_id')
        pops = Pop.query.filter_by(place_id=place_id).all()

        pop_list = []
        for pop in pops:
            pop_list.append(pop.id)
        return (jsonify(pop_list))

    pops = Pop.query.all()

    pop_list = []
    for pop in pops:
        pop_dict = {
            "id": pop.id,
            "place_id": pop.place_id,
        }
        pop_list.append(pop_dict)

    return jsonify(pop_list)


# Create a pop
@api.post("/pops/")
def pops_create():
    content = request.json

    id = secrets.token_hex(4)
    place_id = content.get('place_id')
    population = content.get('population', 1000)
    gender = content.get('gender', 'male')
    age = content.get('age', random.randint(18, 60))
    wealth = content.get('wealth', 1)
    job = content.get('job', 'unemployed')

    if not place_id:
        return jsonify({'message': 'place_id required'})

    place = Place.query.filter_by(id=place_id).first()
    if not place:
        return jsonify({'message': 'place_id not found'})

    if job not in acceptable_job_industry_list:
        return jsonify({'message': 'job not in accepted list'})

    new_pop = Pop(
        id=id,
        place_id=place_id,
        population=population,
        gender=gender,
        age=age,
        wealth=wealth,
        job=job
    )
    db.session.add(new_pop)
    db.session.commit()

    return jsonify({
        'message': 'success',
        'pop': new_pop,
    }), 200


# Pop detail
@api.get("/pops/<id>/")
def pops_get(id):
    pop = Pop.query.filter_by(id=id).first()
    if not pop:
        return jsonify({"message": "Pop not found."}), 404

    traits = Trait.query.filter_by(pop_id=id).all()
    traits_list = []
    for trait in traits:
        traits_list.append(trait.name)

    beliefs = Belief.query.filter_by(pop_id=id).all()
    beliefs_list = []
    for belief in beliefs:
        beliefs_list.append({
            'belief': belief.name,
            'strength': belief.strength
        })

    wealth_name = 'destitute'
    if int(pop.wealth) == 1: wealth_name = 'working_poor'
    if int(pop.wealth) == 2: wealth_name = 'struggling_middle_class'
    if int(pop.wealth) == 3: wealth_name = 'comfortable_professionals'
    if int(pop.wealth) == 4: wealth_name = 'wealthy'
    if int(pop.wealth) == 5: wealth_name = 'rich'

    pop_dict = {
        "id": pop.id,
        "place_id": pop.place_id,
        "population": pop.population,
        "gender": pop.gender,
        "age": pop.age,
        "wealth": pop.wealth,
        "wealth_name": wealth_name,
        "job": pop.job,
        "traits": traits_list,
        "beliefs": beliefs_list
    }

    return jsonify(pop_dict)


# Delete a pop
@api.delete("/pops/<id>/")
def pops_delete(id):
    # Delete associated traits
    traits = Trait.query.filter_by(pop_id=id).all()
    for trait in traits:
        db.session.delete(trait)

    # Delete associated beliefs
    beliefs = Belief.query.filter_by(pop_id=id).all()
    for belief in beliefs:
        db.session.delete(belief)

    db.session.commit()

    # Delete pop
    pop = Pop.query.filter_by(id=id).first()
    if not pop:
        return jsonify({"message": "Pop not found."}), 404

    db.session.delete(pop)
    db.session.commit()

    return jsonify({"message": "Pop deleted."}), 200


# TRAITS

# Pop trait add
@api.post("/pops/<pop_id>/traits/")
def pops_trait_add(pop_id):
    pop_id = pop_id.lower()
    trait_name = request.json.get('trait_name')

    pop = Pop.query.filter_by(id=pop_id).first()
    if not pop:
        return jsonify({"message": "Pop not found."}), 404

    if not trait_name:
        return jsonify({"message": "Trait name must be included"}), 404

    if trait_name not in acceptable_trait_list:
        return jsonify({"message": f"Trait {trait_name} is not valid."}), 400

    # Check if trait already exists
    existing_trait = Trait.query.filter_by(pop_id=pop_id, name=trait_name).first()
    if existing_trait:
        return jsonify({'message': f'Trait {trait_name} already added to that pop'}), 400

    new_trait = Trait(
        pop_id=pop_id,
        name=trait_name.lower()
    )
    try:
        db.session.add(new_trait)
        db.session.commit()
    except:
        return jsonify({'message': 'Database error'}), 400

    return jsonify({'message': 'Trait added'}), 200


# Pop delete trait
@api.delete("/pops/<pop_id>/traits/<trait_name>/")
def pops_trait_delete(pop_id, trait_name):
    pop_id = pop_id.lower()
    trait_name = trait_name.lower()

    trait = Trait.query.filter_by(pop_id=pop_id, name=trait_name).first()
    if not trait:
        return jsonify({"message": f"Trait {trait_name} not found."}), 404

    try:
        db.session.delete(trait)
        db.session.commit()
    except:
        return jsonify({'message': 'Database error'}), 500

    return jsonify({'message': 'Trait deleted'}), 200


# Check if pop has trait
@api.get("/pops/<pop_id>/traits/<trait_name>/")
def pops_trait_check(pop_id, trait_name):
    pop_id = pop_id.lower()
    trait_name = trait_name.lower()

    pop = Pop.query.filter_by(id=pop_id).first()
    if not pop:
        return jsonify({"message": "Pop not found."}), 404

    if pop.has_trait(trait_name):
        return ({
            'result': True,
            'trait': trait_name,
            'pop_id': pop_id
        }), 200
    else:
        return ({
            'result': False,
            'trait': trait_name,
            'pop_id': pop_id
        })


# BELIEFS

# Add belief
@api.post("/pops/<pop_id>/beliefs/<belief_name>/")
def pops_belief_add(pop_id, belief_name):
    strength = request.json.get('strength', 50)

    belief_name = dehumanize_string(belief_name)

    pop = Pop.query.filter_by(id=pop_id).first()
    if not pop:
        return jsonify({"message": "Pop not found."}), 404

    if not belief_name:
        return jsonify({"message": "Belief name must be included"}), 404

    if belief_name not in acceptable_belief_list:
        return jsonify({"message": f"Belief {belief_name} is not valid."}), 400

    # Check if trait already exists
    existing_trait = Trait.query.filter_by(pop_id=pop_id, name=belief_name).first()
    if existing_trait:
        return jsonify({'message': f'Belief {belief_name} already added to that pop'}), 400

    new_belief = Belief(
        pop_id=pop_id,
        name=belief_name,
        strength=strength
    )
    try:
        db.session.add(new_belief)
        db.session.commit()
    except:
        return jsonify({'message': 'Database error'}), 400

    return jsonify({'message': 'Belief added'}), 200


# Delete belief
@api.delete("/pops/<pop_id>/beliefs/<belief_name>/")
def pops_belief_delete(pop_id, belief_name):
    belief_name = dehumanize_string(belief_name)
    belief = Belief.query.filter_by(pop_id=pop_id, name=belief_name).first()
    if not belief:
        return jsonify({"message": f"Belief {belief_name} not found."}), 404

    try:
        db.session.delete(belief)
        db.session.commit()
    except:
        return jsonify({'message': 'Database error'}), 500

    return jsonify({'message': 'Belief deleted'}), 200


# Check if pop has belief
@api.get("/pops/<pop_id>/beliefs/<belief_name>/")
def pops_belief_check(pop_id, belief_name):
    pop_id = pop_id.lower()
    belief_name = dehumanize_string(belief_name)

    belief = Belief.query.filter_by(pop_id=pop_id, name=belief_name).first()
    if belief:
        return ({
            'result': True,
            'belief': belief_name,
            'description': humanize_string(belief_name),
            'pop_id': pop_id,
            'place_id': belief.place_id,
        }), 200
    else:
        return ({
            'result': False,
            'belief': belief_name,
            'description': humanize_string(belief_name),
            'pop_id': pop_id
        })


# Change belief
@api.put("/pops/<pop_id>/beliefs/<belief_name>/")
def pops_belief_change(pop_id, belief_name):
    strength = request.json.get('strength', 50)

    belief_name = dehumanize_string(belief_name)

    belief = Belief.query.filter_by(pop_id=pop_id, name=belief_name).first()
    if not belief:
        return jsonify({"message": f"Belief {belief_name} not found."}), 404

    belief.strength = strength
    try:
        db.session.commit()
    except:
        return jsonify({'message': 'Database error'}), 500

    return jsonify({'message': 'Belief changed'}), 200


######################
# TRAITS AND BELIEFS #
######################

@api.get("/traits/")
def traits_list():
    return jsonify(acceptable_trait_list)


@api.get("/beliefs/")
def beliefs_list():
    return jsonify(acceptable_belief_list)


@api.get("/industries/")
def industries_list():
    return jsonify(acceptable_job_industry_list)


#########
# POLLS #
#########

@api.get("/places/<place_id>/polls/traits/<trait_name>/")
def calculate_percentage_have_trait(place_id, trait_name):
    trait_name = dehumanize_string(trait_name)

    place = Place.query.filter_by(id=place_id).first()
    if not place:
        return jsonify({"message": "Place not found."}), 404

    pops = Pop.query.filter_by(place_id=place_id).all()
    if not pops:
        return jsonify({"message": "No pops found."}), 404

    pops_with_trait = Pop.query.filter(
        Pop.place_id == place_id,
        Pop.traits.any(name=trait_name)
    ).count()

    return round(pops_with_trait / len(pops) * 100, 2)


def check_belief_strength(strength):
    threshold_passionately_support_oppose = 80
    threshold_strongly_support_oppose = 40
    threshold_support_oppose = 10

    if strength > threshold_passionately_support_oppose:
        return "passionately_support"

    if strength < -threshold_passionately_support_oppose:
        return "passionately_oppose"

    if strength > threshold_strongly_support_oppose:
        return "strongly_support"

    if strength < -threshold_strongly_support_oppose:
        return "strongly_oppose"

    if strength > threshold_support_oppose:
        return "support"

    if strength < -threshold_support_oppose:
        return "oppose"

    return "neutral"


@api.get("/places/<place_id>/polls/beliefs/<belief_name>/")
def calculate_percentage_have_belief(place_id, belief_name):
    belief_name = dehumanize_string(belief_name)

    place = Place.query.filter_by(id=place_id).first()
    if not place:
        return jsonify({"message": "Place not found."}), 404

    pops = Pop.query.filter_by(place_id=place_id).all()
    if not pops:
        return jsonify({"message": "No pops found."}), 404

    count_dictionary = {
        'passionately_support': 0,
        'strongly_support': 0,
        'support': 0,
        'neutral': 0,
        'oppose': 0,
        'strongly_oppose': 0,
        'passionately_oppose': 0,
    }

    beliefs = Belief.query.filter(Belief.pop.place_id == place_id).all()
    for belief in beliefs:
        belief_strength_description = check_belief_strength(belief.strength)
        count_dictionary[belief_strength_description] = count_dictionary[belief_strength_description] + 1

    number_of_pops = len(pops)
    number_expressing_belief = sum(count_dictionary.values())

    count_dictionary['neutral'] = count_dictionary['neutral'] + number_of_pops - number_expressing_belief

    for key in count_dictionary:
        count_dictionary[key] = round(count_dictionary[key] / number_of_pops * 100, 2)

    result = {
        'belief_name': belief_name,
        'poll_result': count_dictionary
    }

    if 'belief' in request.path:
        return jsonify(result)

    return result


@api.get("/places/<place_id>/polls/")
def all_polls(place_id):
    place = Place.query.filter_by(id=place_id).first()
    if not place:
        return jsonify({"message": "Place not found."}), 404

    pop_count = Pop.query.filter_by(place_id=place_id).count()

    # Prepare the traits list
    traits_poll_list = []
    for trait in acceptable_trait_list:
        trait_poll = {
            'trait': trait,
            'percentage': calculate_percentage_have_trait(place_id, trait)
        }
        traits_poll_list.append(trait_poll)

    # Prepare the beliefs list
    beliefs_poll_list = []
    # for belief in acceptable_belief_list:
    #    belief_poll = calculate_percentage_have_belief(place_id, belief)
    #    beliefs_poll_list.append(belief_poll)

    return jsonify({
        'place_id': place_id,
        'place_name': place.name,
        'pop_count': pop_count,
        'trait_polls': traits_poll_list,
        'belief_polls': beliefs_poll_list
    })
