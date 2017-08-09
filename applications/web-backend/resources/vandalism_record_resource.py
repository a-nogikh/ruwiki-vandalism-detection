from flask_restful import Resource, Api


class VandalismRecord(Resource):
    def get(self):
        return {'hello': 'world'}
