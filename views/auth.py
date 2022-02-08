from flask import request, abort
from flask_restx import Resource, Namespace

from config import Config
from models import User
from setup_db import db
import jwt
import datetime
import calendar

auth_ns = Namespace('auth')


@auth_ns.route('/')
class AuthView(Resource):

    def post(self):
        req_json = request.json
        ent = User(**req_json)
        ent.password = User.get_hash(req_json.get("password"))
        with db.session.begin():
            user = db.session.query(User).filter(User.username == ent.username, User.password ==
                                                 ent.password).scalar()
        if user is not None:
            data = {
                'username': user.username,
                'role': user.role
            }
            result_token = {
                'access_token': self.generate_access_token(data, Config.SECRET, Config.ALGO),
                'refresh_token': self.generate_refresh_token(data, Config.SECRET, Config.ALGO)
            }
            return result_token, 201
        else:
            return abort(401)

    def generate_access_token(self, data, secret, algo):
        min30 = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        data["exp"] = calendar.timegm(min30.timetuple())
        return jwt.encode(data, secret, algorithm=algo)

    def generate_refresh_token(self, data, secret, algo):
        days130 = datetime.datetime.utcnow() + datetime.timedelta(days=130)
        data["exp"] = calendar.timegm(days130.timetuple())
        return jwt.encode(data, secret, algorithm=algo)

    def put(self):
        req_json = request.json
        if self.check_token(req_json['refresh_token'], Config.SECRET, Config.ALGO):
            pld = jwt.decode(req_json['refresh_token'], Config.SECRET, Config.ALGO)
            data = {
                'username': pld['username'],
                'role': pld['role']
            }
            result_token = {
                'access_token': self.generate_access_token(data, Config.SECRET, Config.ALGO),
                'refresh_token': self.generate_refresh_token(data, Config.SECRET, Config.ALGO)
            }
            return result_token, 201
        else:
            return abort(401)

    def check_token(self, token, secret, algo):
        try:
            jwt.decode(token, secret, algorithms=algo)
            return True
        except Exception as e:
            return False
