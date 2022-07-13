from flask import Flask, render_template, request
import badges
import users
import challenges

app = Flask(__name__)

app = Flask(__name__)
app.register_blueprint(challenges.bp)
app.register_blueprint(users.bp)
app.register_blueprint(badges.bp)

# We may need these for authorizing and creating users
# app.register_blueprint(login.bp)
# app.register_blueprint(oauth.bp)


@app.route('/')
def index():
    return render_template('index.html')


##########This might go in the users.py file.######

# TO DO:
# Add connection to get user's name from the database
@app.route('/home', methods=['GET'])
def home():
    user="John Doe" # Will be a search to find the current user's name 

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

    if not request.args.get('search'):
        #Query for all challenges -- Active, Favorite and Completed   
        pass  

    return render_template('userhome.html', user=user)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
