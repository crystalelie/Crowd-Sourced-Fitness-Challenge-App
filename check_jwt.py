import json
from json2html import *
from flask import request, make_response
from google.oauth2 import id_token
from google.auth.transport import requests
import constants 


def check_jwt(headers):
    # Checks if JWT was provided in Authorization header
    if 'Authorization' in headers:
        auth_header = request.headers['Authorization']
        auth_header = auth_header.split(" ")[1]

        # Checks validity of JWT provided
        try:
            sub = id_token.verify_oauth2_token(
                auth_header, requests.Request(), constants.client_id)['sub']
            return sub
        except:
            err = json.dumps({"Error 401": "JWT is invalid"})
            res = make_response(json2html.convert(json=err))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 401
            return res
    else:
        err = json.dumps({"Error 401": "Authorization header is missing JWT"})
        res = make_response(json2html.convert(json=err))
        res.headers.set('Content-Type', 'text/html')
        res.status_code = 401
        return res

        # Sends html response
        # content = json.dumps(boat)
        # res = make_response(json2html.convert(json=content))
        # res.headers.set('Content-Type', 'text/html')
        # res.status_code = 200
        # return res
