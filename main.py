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

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
