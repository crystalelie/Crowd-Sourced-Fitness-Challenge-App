from flask import Blueprint, request, make_response, render_template
from google.cloud import datastore
import constants

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
    images = []
    print(badges)
    for badge in badges:
        names.append(badge["name"])
        images.append(badge["image"])
    return render_template("badges.html", names=names, images=images)
