from flask import Blueprint, request, make_response, jsonify, render_template
from google.cloud import datastore
import constants

# These we might need, so I'll just add them as comments.
# They are for json and the others are for authorizing tokens from the user
# import json
# from google.oauth2 import id_token
# from googgle.auth.transport import requests

client = datastore.Client()

bp = Blueprint('users', __name__, template_folder='templates', static_folder='static', url_prefix='/home')


@bp.route('', methods=['POST', 'GET'])
def home():

    user_id = request.args.get("id")
    query = client.query(kind=constants.users)
    users = list(query.fetch())
    for curr_user in users:
        if int(user_id) == curr_user.id:
            user_name = str(curr_user["first_name"] + " " + curr_user["last_name"])

    if request.method == 'GET':
        # Search for a challenge
        if request.args.get('search'):
            input = request.args['input'].lower()

            if input != '':
                #Query for all challenges that have a certain key word or key words -- Active, Favorite and Completed
                pass
            else:
                #Query for all challenges -- Active, Favorite and Completed
                pass

        res = make_response(render_template('userhome.html', user_name=user_name))
        res.headers.set('Content-Type', 'text/html')
        res.status_code = 200
        return res

    if not request.args.get('search'):
        #Query for all challenges -- Active, Favorite and Completed
        pass

    else:
        # Status code 405
        res = make_response()
        res.headers.set('Allow', 'GET, POST')
        res.headers.set('Content-Type', 'text/html')
        res.status_code = 405
        return res
