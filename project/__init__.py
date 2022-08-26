from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import os

from sqlalchemy.sql.expression import false, true

from flask_cors import CORS, cross_origin


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

#def create_app():
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://usr7chco5ywlmt4b:QZAAPpVkUDeozyLm77ic@b8g3qoflozcqrafourgp-mysql.services.clever-cloud.com:3306/b8g3qoflozcqrafourgp'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JSON_SORT_KEYS"] = False


if os.environ.get("LOCATION_RUNNING") == "heroku":
    site_url = "https://popworld.herokuapp.com"
else:
    site_url = "http://localhost:6688"


CORS(app)

# db init
from .models import Place, Pop, Trait, Belief
db.init_app(app)
migrate = Migrate(app, db)

# blueprints

from .api import api as api_blueprint
app.register_blueprint(api_blueprint)

from .main import main as main_blueprint
app.register_blueprint(main_blueprint)

from .simulator import simulator as simulator_blueprint
app.register_blueprint(simulator_blueprint)