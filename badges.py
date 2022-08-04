from flask import Blueprint, request, make_response, render_template
from google.cloud import datastore
import constants

client = datastore.Client()

bp = Blueprint('badges', __name__, url_prefix='/badges')

@bp.route('/<uid>', methods=['GET'])
def get_badges(uid):

    query = client.query(kind=constants.users)
    users = list(query.fetch())
    query2 = client.query(kind=constants.user_account)
    user_accounts = list(query2.fetch())

    badge_dict = {}
    for user in users:
        user_name = str(user["first_name"] + " " + user["last_name"])
        badge_dict[user_name] = 0
        for accounts in user_accounts:
            if accounts["user"].id == user.id and accounts["Completed"] == True:
                badge_dict[user_name] += 1

    for account in badge_dict.items():
        if account[1] > 0:
            print(account[0])

    return render_template("badges.html", badge_dict = badge_dict, uid=uid)
