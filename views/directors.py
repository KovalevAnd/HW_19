from flask import jsonify, request
from flask_restx import Resource, Namespace

from models import Director, DirectorSchema
from setup_db import db
from decorators import auth_required, admin_required

director_ns = Namespace('directors')


@director_ns.route('/')
class DirectorsView(Resource):
    @auth_required
    def get(self):
        rs = db.session.query(Director).all()
        return jsonify(DirectorSchema(many=True).dump(rs))

    @admin_required
    def post(self):
        req_json = request.json
        ent = Director(**req_json)

        db.session.add(ent)
        db.session.commit()
        return "", 201, {"location": f"/directors/{ent.id}"}

@director_ns.route('/<int:rid>')
class DirectorView(Resource):
    @auth_required
    def get(self, rid):
        r = db.session.query(Director).get(rid)
        return jsonify(DirectorSchema().dump(r))

    @admin_required
    def put(self, bid):
        director = db.session.query(Director).get(bid)
        req_json = request.json
        director.name = req_json.get("name")
        db.session.add(director)
        db.session.commit()
        return "", 204

    @admin_required
    def delete(self, bid):
        director = db.session.query(Director).get(bid)

        db.session.delete(director)
        db.session.commit()
        return "", 204