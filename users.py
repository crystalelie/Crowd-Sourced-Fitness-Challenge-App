from flask import Blueprint, request, make_response, jsonify, render_template, flash, redirect, url_for
from google.cloud import datastore
from json2html import *
from string import ascii_letters, digits
import json
import constants
import requests

# These we might need, so I'll just add them as comments.
# They are for json and the others are for authorizing tokens from the user
# import json
# from google.oauth2 import id_token
# from googgle.auth.transport import requests

client = datastore.Client()

bp = Blueprint('users', __name__, template_folder='templates', static_folder='static', url_prefix='/home')


# Change route so that it is passing the id in it
@bp.route('', methods=['POST', 'GET'])
def home():

    user_id = request.args.get("id")
    query = client.query(kind=constants.users)
    users = list(query.fetch())
    for curr_user in users:
        if int(user_id) == curr_user.id:
            user_name = {"id": curr_user.id, "name": str(curr_user["first_name"] + " " + curr_user["last_name"])}

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
        # Query for all challenges -- Active, Favorite and Completed
        pass

    else:
        # Status code 405
        res = make_response()
        res.headers.set('Allow', 'GET, POST')
        res.headers.set('Content-Type', 'text/html')
        res.status_code = 405
        return res


@bp.route('/<cid>/challenge', methods=['POST', 'GET'])
def create_challenge(cid):
    if request.method == 'POST':

        if not request.is_json:
            # Checks if sent data is json, if not return 415
            err = json.dumps({"Error 415": "The request header 'content_type' is not application/json "
                                           "and/or the sent request body does not contain json"})
            res = make_response(json2html.convert(json=err))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 415
            return res

        elif 'application/json' not in request.accept_mimetypes:
            # Checks if client accepts json, if not return 406
            err = json.dumps({"Error 406": "The request header ‘Accept' is not application/json"})
            res = make_response(json2html.convert(json=err))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 406
            return res

        # Checks if header sent data is json, if not return 415
        try:
            content = request.get_json()
        except:
            err = json.dumps({"Error 415": "The request header 'content_type' is not application/json "
                                           "and/or the sent request body does not contain json"})
            res = make_response(json2html.convert(json=err))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 415
            return res

        # Check contents of the json file to make sure keys have values, and it is not empty.
        # Only supported attributes will be used. Any additional ones will be ignored.
        if not content or "name" not in content or "type" not in content or "length" not in content:
            err = json.dumps({"Error 400": "The request object is missing at least one of the required attributes"})
            res = make_response(json2html.convert(json=err))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 400
            return res

        # Check value of contents to make sure they are not null or have valid characters.
        if set(content["name"]).difference(ascii_letters + digits + " ") or \
                set(content["type"]).difference(ascii_letters + digits + " ") \
                or not isinstance(content["length"], int):
            err = json.dumps({"Error 400": "The request object has at least one invalid value assigned to an "
                                           "attribute"})
            res = make_response(json2html.convert(json=err))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 400
            return res

        # Name of challenges must be unique
        query = client.query(kind=constants.challenges)
        challenges_list = list(query.fetch())

        # Search all challenges objects and compare the names to make sure they are unique
        for curr_challenges in challenges_list:
            if curr_challenges["name"] == content["name"]:
                err = json.dumps({"Error 403": "There is already a challenges with that name"})
                res = make_response(json2html.convert(json=err))
                res.headers.set('Content-Type', 'text/html')
                res.status_code = 403
                return res

        # For future bug closure: Query list of users. If sub not in list of users, return a 401

        # Create new challenges entity
        new_challenges = datastore.entity.Entity(key=client.key(constants.challenges))
        ### Make changes to attribute names if necessary
        # Schema:
        # Name : str
        # exercise_type : str or exercise_type_id (will need to pick one)
        # duration : int
        # time_unit : str
        # Source: https://stackoverflow.com/questions/45111538/javascript-how-to-build-a-checkbox-list-that-returns
        # -the-values-which-have-been
        # goals : list/array of strings
        # badges : str or int for badge_ID
        # description : str
        # tags : list/array of strings
        new_challenges.update({"name": content["name"], "exercise_type": content["exercise_type"],
                               "duration": int(content["duration"]), "time_unit": int(content["time_unit"]),
                               "goals": content["goals"], "badges": content["badges"], "description": content[
                "description"], "owner": cid})

        client.put(new_challenges)
        new_challenges["id"] = new_challenges.key.id
        new_challenges["self"] = request.base_url + "/" + str(new_challenges.key.id)

        flash('Challenge created successfully!')
        return redirect(url_for('challenges_post_get'))

        ## IF statement for below if requesting just the json in the header Accept
        # res = make_response(json.dumps(new_challenges))
        # res.mimetype = 'application/json'
        # res.status_code = 201
        # return res

    elif request.method == "GET":
        exercises = requests.get(url_for("exercises_post_get"))
        return render_template("create.html", exercises=exercises)
