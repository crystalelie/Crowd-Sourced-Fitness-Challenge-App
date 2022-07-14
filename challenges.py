from flask import Blueprint, request, make_response, render_template, url_for, flash
from google.cloud import datastore
import constants
from check_jwt import check_jwt

client = datastore.Client()

bp = Blueprint('challenges', __name__, url_prefix='/challenges')


@bp.route('', methods=['POST', 'GET'])
def challenges_post_get():
    # Checks if JWT was provided in Authorization header
    sub = check_jwt(request.headers)

    if request.method == 'POST':
        if not isinstance(sub, str):
            return sub

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
        if set(content["name"]).difference(ascii_letters + digits + whitespace) or \
                set(content["type"]).difference(ascii_letters + digits + whitespace) \
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
                "description"], "owner": sub})

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

    elif request.method == 'GET':

        if ('*/*' or 'application/json') not in request.accept_mimetypes:
            # Checks if client accepts json, if not return 406
            err = json.dumps({"Error 406": "The request header ‘Accept' is not application/json"})
            res = make_response(json2html.convert(json=err))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 406
            return res

        # Get query of challenges by owner and set the limit and offset for the query
        query = client.query(kind=constants.challenges)
        # query.add_filter("owner", "=", sub)
        total_challenges = list(query.fetch(query.keys_only()))

        # Reset the query to show the objects
        query = client.query(kind=constants.challenges)
        query.add_filter("owner", "=", sub)
        q_limit = int(request.args.get('limit', '10'))
        q_offset = int(request.args.get('offset', '0'))

        # Get result of query and make into a list
        challenges_iterator = query.fetch(limit=q_limit, offset=q_offset)
        pages = challenges_iterator.pages
        # print(type(pages))
        # results = list(next(pages))
        #
        # # Create a "next" url page using
        # if challenges_iterator.next_page_token:
        #     next_offset = q_offset + q_limit
        #     next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
        # else:
        #     next_url = None
        #
        # # Adds id key and value to each json slip; add next url
        # for challenges in results:
        #     challenges["id"] = challenges.key.id
        #     challenges["self"] = request.base_url + "/" + str(challenges.key.id)
        # output = {"challenges": results}
        #
        # if next_url:
        #     output["next"] = next_url
        #
        # output["total_challenges"] = len(total_challenges)

        res = make_response(render_template('participate.html'))
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
