from flask import escape
from sqlalchemy import ForeignKey
from . import db
from datetime import datetime, timedelta
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
import arrow

from dataclasses import dataclass


def humanize_string(result):
    result = result.replace('_', ' ')
    result = result.title()
    return result


def dehumanize_string(result):
    result = result.replace(' ', '_')
    result = result.lower()
    return result


@dataclass
class Place(db.Model):
    name: str

    id:str = db.Column(db.String(30), primary_key=True)

    two_letter_code:str = db.Column(db.String(4))

    pops = db.relationship('Pop', backref='place', lazy='dynamic')

    @property
    def name(self):
        return humanize_string(self.id)


@dataclass
class Pop(db.Model):
    id:str = db.Column(db.String(10), primary_key=True)

    place_id:str = db.Column(db.String(30), ForeignKey('place.id'), nullable=False)
    population:int = db.Column(db.Integer, nullable=False)

    gender:str = db.Column(db.String(10))
    age:int = db.Column(db.Integer)

    wealth:int = db.Column(db.Integer)

    beliefs = db.relationship('Belief', backref='pop', lazy=True)
    traits = db.relationship('Trait', backref='pop', lazy=True)

    job:str = db.Column(db.String(50))


# Each pop can have zero to multiple traits, that describe who they are in factual terms
# Traits are binary - they either apply or they don't.
# Generally a trait wouldn't change throughout a pop's life.
#
# Examples:
# - Parent
# - Gun owner

@dataclass
class Trait(db.Model):
    name_formatted: str

    id:int = db.Column(db.Integer, primary_key=True)
    pop_id:str = db.Column(db.String(10), ForeignKey('pop.id'), nullable=False)
    name:str = db.Column(db.String(60), nullable=False)

    @property
    def name_formatted(self):
        return humanize_string(self.name)


# Each pop can have zero to multiple beliefs, which define how they feel about issues.
# Each belief also has a strength associated with it, which is a number between:
# 100 (they feel very strongly positive about something) and
# -100 (they are very strongly opposed to something).
#
# Examples:
# - Gun control (100), very much in favour of gun control
# - Gun control (-100), very much against gun control
# - Gun control (0), neutral on gun control
#
# - Law and order
# - Abortion rights
# - Female rights
# - Male rights
# - LGBT rights
# - Euthanasia
# - Immigration
# - Diversity
# - Universal healthcare
# - Environment
# - Legalized drugs

@dataclass
class Belief(db.Model):
    name_formatted: str

    id:int = db.Column(db.Integer, primary_key=True)
    pop_id:str = db.Column(db.String(10), ForeignKey('pop.id'), nullable=False)
    name:str = db.Column(db.String(60), nullable=False)
    strength:int = db.Column(db.Integer, default=0)

    @hybrid_property
    def pop(self):
        return Pop.query.filter(Pop.id == self.pop_id).first()

    @hybrid_property
    def place_id(self):
        pop = Pop.query.filter(Pop.id == self.pop_id).first()
        return pop.place_id

    @property
    def name_formatted(self):
        return humanize_string(self.name)