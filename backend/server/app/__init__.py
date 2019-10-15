import os
from flask import Flask, request
from flask_cors import CORS
from werkzeug.utils import import_string

import config

def getConfig():
    if os.environ['ENVIRON'] == 'DEVELOPMENT':
        return import_string('config.DevelopmentConfig')()
    elif os.environ['ENVIRON'] == 'PRODUCTION':
        return import_string('config.ProductionConfig')()


app = Flask(__name__)
CORS(app)
app.config.from_object(getConfig())

from app import routes

app.register_blueprint(routes.routes)
app.run(host="0.0.0.0")



