from flask import request
from flask_restx import Resource, Namespace

from models import User, UserSchema
from setup_db import db

users_ns = Namespace('users')


@users_ns.route('/')
class UsersView(Resource):
    def get(self):
        all_users = db.session.query(User).all()
        res = UserSchema(many=True).dump(all_users)
        return res, 200

    def post(self):
        req_json = request.json
        ent = User(**req_json)
        ent.password = User.get_hash(req_json.get("password"))
        db.session.add(ent)
        db.session.commit()
        return "", 201, {"location": f"/users/{ent.id}"}


@users_ns.route('/<int:bid>')
class UsersView(Resource):
    def get(self, bid):
        b = db.session.query(User).get(bid)
        sm_d = UserSchema().dump(b)
        return sm_d, 200

    def put(self, bid):
        user = db.session.query(User).get(bid)
        req_json = request.json
        user.username = req_json.get("username")
        user.password = User.get_hash(req_json.get("password"))
        user.role = req_json.get("role")
        db.session.add(user)
        db.session.commit()
        return "", 204

    def delete(self, bid):
        user = db.session.query(User).get(bid)

        db.session.delete(user)
        db.session.commit()
        return "", 204
