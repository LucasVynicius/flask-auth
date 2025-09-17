from flask import Flask, request, jsonify
from models.user import User
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY']= 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@127.0.0.1:3306/flask_auth'

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout bem-sucedido"})


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": "Login bem-sucedido"})

    return jsonify({"message": "Credenciais inválida"}), 400


@app.route("/user", methods=["POST"])
@login_required
def create_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username and password:
        # if User.query.filter_by(username=username).first():
        #     return jsonify({"message": "Usuário já existe"}), 400
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        new_user = User(username=username, password=hashed_password, role='user')
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Usuário criado com sucesso"}), 201

    return jsonify({"message": "Dados inválidos"}), 400

@app.route("/user/<int:user_id>", methods=["GET"])
@login_required
def read_user(user_id):
    user = User.query.get(user_id)

    if user:
        return jsonify({"id": user.id, "username": user.username}), 200
    
    return jsonify({"message": "Usuário não encontrado"}), 404

@app.route("/users", methods=["GET"])
@login_required
def read_users():
    users = User.query.all()
    users_list = [{"id": user.id, "username": user.username} for user in users]
    return jsonify(users_list), 200

@app.route("/user/<int:user_id>", methods=["PUT"])
@login_required
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)

    if user_id != current_user.id and current_user.role == "user":
        return jsonify({"message": "Você não pode atualizar outro usuário"}), 403

    if user and data.get("password"):
        user.password = data.get("password")
        db.session.commit()
        return jsonify({"message": f"Usuário {user_id} atualizado com sucesso"}), 200

    return jsonify({"message": "Dados inválidos ou usuário não encontrado"}), 400

@app.route("/user/<int:user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)

    if current_user.role != "admin":
        return jsonify({"message": "Apenas administradores podem deletar usuários"}), 403

    if user_id == current_user.id:
        return jsonify({"message": "Você não pode deletar seu próprio usuário"}), 403

    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"Usuário {user_id} deletado com sucesso"}), 200

    return jsonify({"message": "Usuário não encontrado"}), 404

if __name__ == "__main__":
    app.run(debug=True)