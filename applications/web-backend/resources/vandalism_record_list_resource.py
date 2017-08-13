from flask_restful import Resource, Api


class VandalismRecordListResource(Resource):
    def get(self):
        return {'hello': 'world'}
