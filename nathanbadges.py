from flask import Blueprint, request, make_response, render_template
from google.cloud import datastore
import constants

# These we might need, so I'll just add them as comments.
# They are for json and the others are for authorizing tokens from the user
# import json
# from google.oauth2 import id_token
# from google.auth.transport import requests

client = datastore.Client()

bp = Blueprint('badges', __name__, url_prefix='/badges')


@bp.route('', methods=['GET'])
def name_of_func():

    # test code from sean to create a new badge 
    # new_badge= datastore.entity.Entity(key=client.key(constants.badges))
    # new_badge.update({"name": "Testing", "type": "Running"})
    # client.put(new_badge)

    query = client.query(kind=constants.badges)
    badges = list(query.fetch())
    names = []
    for badge in badges:
        names.append(badge["name"])
    return render_template("badges.html", names=names)
