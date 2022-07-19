from flask import Blueprint, request, make_response, render_template
from google.cloud import datastore
import constants

client = datastore.Client()

bp = Blueprint('create', __name__, url_prefix='/create')

@bp.route('', methods=['GET'])
def func():
    return render_template("create.html")