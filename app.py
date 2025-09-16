from flask import Flask, request, jsonify
from models.user import User
from database import db
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY']= 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

LoginManager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

# @login_manager.user_loader
# def load_user(user_id):

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username and password:
        pass

    return jsonify({"message": "Credenciais inválida"}), 400

@app.route("/hello-world", methods=["GET"])
def hello_word():
    return "Hello, World!"


if __name__ == "__main__":
    app.run(debug=True)