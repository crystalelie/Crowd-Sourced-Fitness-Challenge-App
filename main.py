from flask import Flask, redirect, render_template, request, url_for
from google.cloud import datastore
import badges
import users
import challenges
import constants
import create

app = Flask(__name__)

client = datastore.Client()

app = Flask(__name__)
app.register_blueprint(challenges.bp)
app.register_blueprint(users.bp)
app.register_blueprint(badges.bp)
app.register_blueprint(create.bp)

# We may need these for authorizing and creating users
# app.register_blueprint(login.bp)
# app.register_blueprint(oauth.bp)


@app.route('/')
def index():

    signup = request.args.get('signup')
    login = request.args.get('login')
    if signup == "Sign up":
        # if submitting new account register new info 
        fname = request.args.get('fname')   
        lname = request.args.get('lname')    
        email = request.args.get('email')
        password = request.args.get('password')
        print(f"new user with info {fname}, {lname}, {email}, {password}")    
        new_user= datastore.entity.Entity(key=client.key(constants.users))
        new_user.update({"first_name": fname, "last_name": lname, "password": password, "email": email})
        client.put(new_user)

    elif login == "Login":
        login_email = request.args.get('email')
        login_password = request.args.get('password')
        print(f"login attempt with info {login_email}, {login_password}")
        query = client.query(kind=constants.users)
        users = list(query.fetch())
        for user in users:
            if login_email == user["email"]:
                if login_password == user["password"]:
                    curr_id = user.id
                    return redirect(url_for('users.home', id=curr_id))


    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
