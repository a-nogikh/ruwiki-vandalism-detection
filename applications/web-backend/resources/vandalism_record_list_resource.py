from flask_restful import Resource, Api


class VandalismRecordList(Resource):
    def get(self):
        return {'hello': 'world'}
