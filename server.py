from flask import Flask, request
from database import db, User

from utils import encode, decode

import os


app = Flask(__name__)

DB_USER = os.environ.get("AUTH_DB_USER")
DB_PASSWORD = os.environ.get("AUTH_DB_PASS")
DB_HOST = os.environ.get("AUTH_DB_HOST")
DB_PORT = os.environ.get("AUTH_DB_PORT")
DB_NAME = os.environ.get("AUTH_DB_NAME")
SECRET_KEY = os.environ.get("AUTH_SECRET_KEY")
JWT_ALGORITHM = "HS256"

connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print("CONNECTION STRING: ", connection_string)
app.config['SQLALCHEMY_DATABASE_URI'] = connection_string

print('Attemping to connect to Postgres DB')


db.init_app(app)

with app.app_context():
    db.create_all()


print('Connected to Database')


@app.get('/')
def health_check():
    return {'status': 'ok'}


@app.post('/create')
def create_user():
    email, password = request.json['email'], request.json['password']

    if not email or not password:
        return "No Credentials", 400

    user_exists = User.query.filter_by(email=email).first()
    if user_exists:
        return "User Already Exists", 400
    user = User(
        email=email,
        password=password
    )
    db.session.add(user)
    db.session.commit()

    return "Success", 201


@app.post('/login')
def login():
    auth = request.authorization
    if not auth:
        return "Not Authorized", 401

    user = User.query.filter_by(email=auth.username).first()
    if not user or user.password != auth.password:
        return "Invalid Credentials", 401

    jwt_token = encode(user.email, SECRET_KEY,
                       is_admin=True, algorithm=JWT_ALGORITHM)

    return jwt_token, 200


@app.post('/validate')
def validate():
    auth = request.headers['Authorization']
    print(auth)
    if not auth:
        return "Invalid Credenitals", 400

    auth_type, token = auth.split(" ")
    print(auth_type, token)
    if auth_type != "Bearer":
        return "Bad Request", 400
    decoded = decode(token, SECRET_KEY, algorithm=JWT_ALGORITHM)
    if not decoded:
        return "Not Authorized", 401
    return decoded, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
