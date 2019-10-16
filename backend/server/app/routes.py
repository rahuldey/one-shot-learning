import os
from flask import request, jsonify, Blueprint
from werkzeug.utils import secure_filename, import_string
from app import predict as prediction
import config

routes = Blueprint('api', __name__)


def getConfig():
    return config.DevelopmentConfig()


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'pgm'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@routes.route('/predict', methods=['POST'])
def predict():
    conf = getConfig()
    images = request.files.to_dict()

    if len(images) != 2:
        return jsonify({
            'response': 'Incorrect number of files sent',
            'status': 400,
            'mimetype': 'application/text'
        }), 400

    filenames = []
    for image in images:
        if not (allowed_file(images[image].filename)):
            return jsonify({
                'response': 'File uploaded is not an image',
                'status': 400,
                'mimetype': 'application/text'
            }), 400
        images[image].save(os.path.join(conf.UPLOAD_FOLDER,
                                        secure_filename(images[image].filename)))
        filenames.append(os.path.join(conf.UPLOAD_FOLDER,
                                      secure_filename(images[image].filename)))

    if prediction.verify(filenames) == True:
        res = 'Images match'
    else:
        res = 'Images don\'t match'

    for filename in filenames:
        os.remove(filename)

    return jsonify({
        'response': res,
        'status': 200,
        'mimetype': 'application/text'
    }), 200


@routes.route('/healthcheck', methods=['GET'])
def heartbeat():
    return jsonify({
        'response': 'Server is up',
        'status': 200,
        'mimetype': 'application/text'
    }), 200
