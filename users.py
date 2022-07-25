from flask import Blueprint, request, make_response, jsonify, render_template, flash, redirect, url_for
from google.cloud import datastore
from json2html import *
from string import ascii_letters, digits
import json
import constants
import requests
from goal_convert import goal_convert

client = datastore.Client()

bp = Blueprint('users', __name__, template_folder='templates', static_folder='static', url_prefix='/home')


# Change route so that it is passing the id in it

@bp.route('/<uid>', methods=['POST', 'GET'])
def home(uid):
    # user_id = request.args.get("id")

    # Checks if load with user_id exists
    query = client.key(constants.users, int(uid))
    users = client.get(key=query)

    if not users:
        err = json.dumps({"Error": "No user with this user_id exists"})
        res = make_response(json2html.convert(json=err))
        res.headers.set('Content-Type', 'application/json')
        res.status_code = 404
        return res

    user_name = {"id": users.id, "name": str(users["first_name"] + " " + users["last_name"])}

    if request.method == 'GET':
        # Search for a challenge
        if request.args.get('search'):
            input = request.args['input'].lower()

            if input != '':
                # Query for all challenges that have a certain key word or key words -- Active, Favorite and Completed
                pass
            else:
                # Query for all challenges -- Active, Favorite and Completed
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


@bp.route('/<uid>/challenge', methods=['POST', 'GET'])
def create_challenge(uid):
    if request.method == 'POST':

        res_content = request.form.to_dict()
        goal_list = request.form.getlist('goals[]')
        content = goal_convert(res_content, goal_list)

        # Check contents of the json file to make sure keys have values, and it is not empty.
        # Only supported attributes will be used. Any additional ones will be ignored.
        if not content or "name" not in content or "exercise_type" not in content or "duration" not in content \
                or "time_unit" not in content or "goals" not in content or "description" not in \
                content or "tags" not in content:
            err = json.dumps({"Error 400": "The request object is missing at least one of the required attributes"})
            res = make_response(json2html.convert(json=err))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 400
            return res

        # Check value of contents to make sure they are not null or have valid characters.
        if set(content["name"]).difference(ascii_letters + digits + " ") or \
                not isinstance(int(content["duration"]), int):
            err = json.dumps({"Error 400": "Your name of your Challenge has an invalid character"})
            res = make_response(json2html.convert(json=err))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 400
            return res

        exe_flag = False
        query = client.query(kind=constants.exercises)
        exercise_list = list(query.fetch())

        for exercise in exercise_list:
            if exercise["name"] == content["exercise_type"]:
                exe_flag = True

        if not exe_flag:
            url = url_for("exercises.exercises_post_get", _external=True)
            data = {
                "name": content["exercise_type"]
            }
            requests.post(url, json=json.dumps(data))

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

        # Create new challenges entity
        new_challenges = datastore.entity.Entity(key=client.key(constants.challenges))
        new_challenges.update({"name": content["name"], "exercise_type": content["exercise_type"],
                               "duration": int(content["duration"]), "time_unit": content["time_unit"],
                               "goals": content["goals"], "description": content[
                "description"], "tags": content["tags"], "owner": uid})

        client.put(new_challenges)
        flash('Challenge created successfully!')
        url = request.root_url + "/challenges/" + uid

        return redirect(url)

    elif request.method == "GET":

        query = client.key(constants.users, int(uid))
        users = client.get(key=query)
        user_name = {"id": users.id, "name": str(users["first_name"] + " " + users["last_name"])}

        url = url_for("exercises.exercises_post_get", _external=True)
        r = requests.get(url)
        exercises = r.json()

        return render_template("create.html", exercises=exercises, user_name=user_name)
