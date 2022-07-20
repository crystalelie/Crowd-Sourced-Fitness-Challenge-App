from flask import Blueprint, request, make_response, render_template  # , url_for, flash, redirect
from string import ascii_letters, digits
from google.cloud import datastore
import constants
import json
from json2html import *
from check_jwt import check_jwt

client = datastore.Client()

bp = Blueprint('challenges', __name__, url_prefix='/challenges')


@bp.route('', methods=['GET'])
def challenges_get():
    # Checks if JWT was provided in Authorization header
    # sub = check_jwt(request.headers)

    if request.method == 'GET':

        # if "create" in request.args:
        #     return render_template("create.html")

        if ('*/*' or 'application/json') not in request.accept_mimetypes:
            # Checks if client accepts json, if not return 406
            err = json.dumps({"Error 406": "The request header ‘Accept' is not application/json"})
            res = make_response(json2html.convert(json=err))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 406
            return res

        # Reset the query to show the objects
        query = client.query(kind=constants.challenges)
        # query.add_filter("name", "=", sub)
        q_limit = int(request.args.get('limit', '10'))
        q_offset = int(request.args.get('offset', '0'))

        # Get result of query and make into a list
        challenges_iterator = query.fetch(limit=q_limit, offset=q_offset)
        pages = challenges_iterator.pages
        total_challenges = list(next(pages))

        # Create a "next" url page using
        if challenges_iterator.next_page_token:
            next_offset = q_offset + q_limit
            next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
        else:
            next_url = None

        # Adds id key and value to each json slip; add next url
        for challenges in total_challenges:
            challenges["id"] = challenges.key.id
            challenges["self"] = request.base_url + "/" + str(challenges.key.id)
        output = {"challenges": total_challenges}

        if next_url:
            output["next"] = next_url

        output["total_challenges"] = len(total_challenges)

        res = make_response(render_template("participate.html", content=output))
        res.headers.set('Content-Type', 'text/html')
        res.status_code = 200
        return res

    else:
        # Status code 405
        res = make_response()
        res.headers.set('Allow', 'GET, POST')
        res.headers.set('Content-Type', 'text/html')
        res.status_code = 405
        return res


## Change to tags. Should we create new tag entity?  Should we search by something else? Drop down menu instead of
# search box?
@bp.route('/search', methods=['GET'])
def challenge_search():

    if request.method == 'GET':

        if ('*/*' or 'application/json') not in request.accept_mimetypes:
            # Checks if client accepts json, if not return 406
            err = json.dumps({"Error 406": "The request header ‘Accept' is not application/json"})
            res = make_response(json2html.convert(json=err))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 406
            return res

        # Get the query to show the objects
        query = client.query(kind=constants.challenges)
        query.add_filter("tag", "=", request.args)
        q_limit = int(request.args.get('limit', '10'))
        q_offset = int(request.args.get('offset', '0'))

        # Get result of query and make into a list
        challenges_iterator = query.fetch(limit=q_limit, offset=q_offset)
        pages = challenges_iterator.pages
        total_challenges = list(next(pages))

        # Create a "next" url page using
        if challenges_iterator.next_page_token:
            next_offset = q_offset + q_limit
            next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
        else:
            next_url = None

        # Adds id key and value to each json slip; add next url
        for challenges in total_challenges:
            challenges["id"] = challenges.key.id
            challenges["self"] = request.base_url + "/" + str(challenges.key.id)
        output = {"challenges": total_challenges}

        if next_url:
            output["next"] = next_url

        output["total_challenges"] = len(total_challenges)

        res = make_response(render_template("participate.html", content=output))
        res.headers.set('Content-Type', 'text/html')
        res.status_code = 200
        return res

    else:
        # Status code 405
        res = make_response()
        res.headers.set('Allow', 'GET, POST')
        res.headers.set('Content-Type', 'text/html')
        res.status_code = 405
        return res


@bp.route('/<cid>', methods=['PATCH', 'PUT', 'DELETE'])
def challenges_get_put_delete(cid):
    # Checks if JWT was provided in Authorization header
    # sub = check_jwt(request.headers)

    # if not isinstance(sub, str):
    #     return sub

    if request.method == 'PATCH':

        if not request.is_json:
            # Checks if sent data is json, if not return 415
            err = {"Error": "The request header 'content_type' is not application/json "
                            "and/or the sent request body does not contain json"}
            res = make_response(err)
            res.headers.set('Content-Type', 'application/json')
            res.status_code = 415
            return res

        elif 'application/json' not in request.accept_mimetypes:
            # Checks if client accepts json, if not return 406
            err = {"Error": "The request header ‘Accept' is not application/json"}
            res = make_response(err)
            res.headers.set('Content-Type', 'application/json')
            res.status_code = 406
            return res

        # Checks if sent data is json, if not return 415
        try:
            content = request.get_json()
        except:
            # Checks if sent data is json, if not return 415
            err = {"Error": "The request header 'content_type' is not application/json "
                            "and/or the sent request body does not contain json"}
            res = make_response(err)
            res.headers.set('Content-Type', 'application/json')
            res.status_code = 415
            return res

        challenge_key = client.key(constants.challenges, int(cid))
        challenge = client.get(key=challenge_key)

        # Checks if challenge with challenge_id exists
        if not challenge:
            err = {"Error": "No challenge with this challenge_id exists"}
            res = make_response(err)
            res.headers.set('Content-Type', 'application/json')
            res.status_code = 404
            return res

        elif challenge["owner"] != cid:
            err = {"Error": "The challenge is owned by another user"}
            res = make_response(err)
            res.headers.set('Content-Type', 'application/json')
            res.status_code = 401
            return res

        # If any or all of the 3 attributes are provided, they are updated.
        if "name" in content and content["name"]:
            # Check value of contents to make sure they are not null or have valid characters.
            if set(content["name"]).difference(ascii_letters + digits + " "):
                err = {"Error": "The request object has at least one invalid value assigned to an attribute"}
                res = make_response(err)
                res.headers.set('Content-Type', 'application/json')
                res.status_code = 400
                return res

            # Name of challenge must be unique
            query = client.query(kind=constants.challenges)
            challenge_list = list(query.fetch())

            # Search all challenge objects and compare the names to make sure they are unique
            for curr_challenge in challenge_list:
                if curr_challenge["name"] == content["name"]:
                    err = {"Error": "There is already a challenge with that name"}
                    res = make_response(err)
                    res.headers.set('Content-Type', 'application/json')
                    res.status_code = 403
                    return res

            # Checks if user is on a challenge, updates all user names
            if challenge["users"]:
                for user_item in challenge["users"]:
                    user_key = client.key(constants.users, int(user_item["id"]))
                    user = client.get(key=user_key)
                    user["carrier"]["name"] = content["name"]
                    user.update(user)
                    client.put(user)

            # challenge name is unique and updated
            challenge.update({"name": content["name"]})

        if "type" in content and content["type"]:
            # Check value of contents to make sure they are not null or have valid characters.
            if set(content["type"]).difference(ascii_letters + digits + " "):
                err = {"Error": "The request object has at least one invalid value assigned to an attribute"}
                res = make_response(err)
                res.headers.set('Content-Type', 'application/json')
                res.status_code = 400
                return res

            challenge.update({"type": content["type"]})

        if "length" in content and content["length"]:
            # Check value of contents to make sure they are not null or have valid characters.
            if not isinstance(content["length"], int):
                err = {"Error": "The request object has at least one invalid value assigned to an attribute"}
                res = make_response(err)
                res.headers.set('Content-Type', 'application/json')
                res.status_code = 400
                return res

            challenge.update({"length": content["length"]})

        client.put(challenge)

        res = make_response(json.dumps(challenge))
        res.mimetype = 'application/json'
        res.status_code = 200
        return res

    elif request.method == 'PUT':

        if not request.is_json:
            # Checks if sent data is json, if not return 415
            err = {"Error": "The request header 'content_type' is not application/json "
                            "and/or the sent request body does not contain json"}
            res = make_response(err)
            res.headers.set('Content-Type', 'application/json')
            res.status_code = 415
            return res

        elif 'application/json' not in request.accept_mimetypes:
            # Checks if client accepts json, if not return 406
            err = {"Error": "The request header ‘Accept' is not application/json"}
            res = make_response(err)
            res.headers.set('Content-Type', 'application/json')
            res.status_code = 406
            return res

        # Checks if sent data is json, if not return 415
        try:
            content = request.get_json()
        except:
            err = {"Error": "The request header 'content_type' is not application/json "
                            "and/or the sent request body does not contain json"}
            res = make_response(err)
            res.headers.set('Content-Type', 'application/json')
            res.status_code = 415
            return res

        challenge_key = client.key(constants.challenges, int(cid))
        challenge = client.get(key=challenge_key)

        # Checks if challenge with challenge_id exists
        if not challenge:
            err = {"Error": "No challenge with this challenge_id exists"}
            res = make_response(err)
            res.headers.set('Content-Type', 'application/json')
            res.status_code = 404
            return res

        elif challenge["owner"] != cid:
            err = {"Error": "The challenge is owned by another user"}
            res = make_response(err)
            res.headers.set('Content-Type', 'application/json')
            res.status_code = 401
            return res

        # Check contents of the json file to make sure keys have values, and it is not empty.
        # Only supported attributes will be used. Any additional ones will be ignored.
        if not content or "name" not in content or "type" not in content or "length" not in content:
            err = {"Error": "The request object is missing at least one of the required attributes"}
            res = make_response(err)
            res.headers.set('Content-Type', 'application/json')
            res.status_code = 400
            return res

        # Check value of contents to make sure they are not null or have valid characters.
        if set(content["name"]).difference(ascii_letters + digits + " ") or \
                set(content["type"]).difference(ascii_letters + digits + " ") \
                or not isinstance(content["length"], int):
            err = {"Error": "The request object has at least one invalid value assigned to an attribute"}
            res = make_response(err)
            res.headers.set('Content-Type', 'application/json')
            res.status_code = 400
            return res

        # Name of challenge must be unique
        query = client.query(kind=constants.challenges)
        challenge_list = list(query.fetch())

        # Search all challenge objects and compare the names to make sure they are unique
        for curr_challenge in challenge_list:
            if curr_challenge["name"] == content["name"]:
                err = {"Error": "There is already a challenge with that name"}
                res = make_response(err)
                res.headers.set('Content-Type', 'application/json')
                res.status_code = 403
                return res

        # Checks if user is on the challenge, updates all user names
        if challenge["users"]:
            for user_item in challenge["users"]:
                user_key = client.key(constants.users, int(user_item["id"]))
                user = client.get(key=user_key)
                user["carrier"]["name"] = content["name"]
                user.update(user)
                client.put(user)

        # Edits all the attributes, except the id
        challenge.update({"name": content["name"], "type": content["type"], "length": content["length"]})
        client.put(challenge)

        res = make_response(json.dumps(challenge))
        res.mimetype = 'application/json'
        res.status_code = 200
        return res

    elif request.method == 'DELETE':
        challenge_key = client.key(constants.challenges, int(cid))
        challenge = client.get(key=challenge_key)

        # Checks if challenge with challenge_id exists
        if not challenge:
            err = {"Error": "No challenge with this challenge_id exists"}
            res = make_response(err)
            res.headers.set('Content-Type', 'application/json')
            res.status_code = 404
            return res

        elif challenge["owner"] != cid:
            err = {"Error": "The challenge is owned by another user"}
            res = make_response(err)
            res.headers.set('Content-Type', 'application/json')
            res.status_code = 401
            return res

        # Check to see if user(s) is/are on the challenge; remove user(s) (carrier==None)
        query = client.query(kind=constants.users)
        users_list = list(query.fetch())

        for curr_user in users_list:
            if curr_user["carrier"] and curr_user["carrier"]['id'] == cid:
                curr_user.update({"carrier": None})
                client.put(curr_user)

        client.delete(challenge_key)

        res = make_response()
        res.status_code = 204
        return res

    elif request.method == 'GET':

        if ('*/*' or 'application/json') not in request.accept_mimetypes:
            # Checks if client accepts json, if not return 406
            err = {"Error": "The request header 'Accept' is not application/json"}
            res = make_response(err)
            res.headers.set('Content-Type', 'application/json')
            res.status_code = 406
            return res

        challenge_key = client.key(constants.challenges, int(cid))
        challenge = client.get(key=challenge_key)

        # Check if challenge exists
        if not challenge:
            return {"Error": "No challenge with this challenge_id exists"}, 404

        challenge["id"] = challenge.key.id
        challenge["self"] = request.base_url

        # Sends json response
        res = make_response(json.dumps(challenge))
        res.headers.set('Content-Type', 'application/json')
        res.status_code = 200
        return res

    else:
        # Status code 405
        res = make_response()
        res.headers.set('Allow', 'GET, DELETE, PATCH, PUT')
        res.headers.set('Content-Type', 'text/html')
        res.status_code = 405
        return res


@bp.route('/<cid>/users', methods=['GET'])
def get_reservations(cid):
    if 'application/json' not in request.accept_mimetypes:
        # Checks if client accepts json, if not return 406
        err = {"Error": "The request header ‘Accept' is not application/json"}
        res = make_response(err)
        res.headers.set('Content-Type', 'application/json')
        res.status_code = 406
        return res

    if request.method == 'GET':
        # Checks if JWT was provided in Authorization header
        # sub = check_jwt(request.headers)
        #
        # if not isinstance(sub, str):
        #     return sub

        challenge_key = client.key(constants.challenges, int(cid))
        challenge = client.get(key=challenge_key)
        user_list = {"self": request.root_url + "challenges/" + cid, "users": []}

        # Check if challenge exists
        if not challenge:
            err = {"Error": "No challenge with this challenge_id exists"}
            res = make_response(err)
            res.headers.set('Content-Type', 'application/json')
            res.status_code = 404
            return res

        # Checks ownership of challenge
        elif challenge["owner"] != cid:
            err = {"Error": "The challenge is owned by another user"}
            res = make_response(err)
            res.headers.set('Content-Type', 'application/json')
            res.status_code = 401
            return res

        if challenge['users']:
            for user in challenge['users']:
                user_list['users'].append(user)

            # Sends json response
            res = make_response(json.dumps(user_list))
            res.headers.set('Content-Type', 'application/json')
            res.status_code = 200
            return res

        # challenge has no users
        else:
            # Sends json response
            res = make_response(json.dumps([]))
            res.headers.set('Content-Type', 'application/json')
            res.status_code = 200
            return res

    else:
        # Status code 405
        res = make_response()
        res.headers.set('Allow', 'GET')
        res.headers.set('Content-Type', 'text/html')
        res.status_code = 405
        return res
