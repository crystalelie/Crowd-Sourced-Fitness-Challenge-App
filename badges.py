from flask import Blueprint, request, make_response
from google.cloud import datastore
import constants

# These we might need, so I'll just add them as comments.
# They are for json and the others are for authorizing tokens from the user
# import json
# from google.oauth2 import id_token
# from google.auth.transport import requests

client = datastore.Client()

bp = Blueprint('badges', __name__, url_prefix='/badges')


@bp.route('', methods=['POST', 'GET'])
def name_of_func():
    pass