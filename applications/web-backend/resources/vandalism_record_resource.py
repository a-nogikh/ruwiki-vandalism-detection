from flask_restful import Resource, Api


class VandalismRecordResource(Resource):
    def get(self):
        return {'hello': 'world'}
