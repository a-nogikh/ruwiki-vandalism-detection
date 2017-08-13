from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask_restful import Resource, Api
from resources.vandalism_record_resource import VandalismRecordResource
from resources.vandalism_record_list_resource import VandalismRecordListResource
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dependencies import db
import os

load_dotenv(find_dotenv())

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

api = Api(app)
db.init_app(app)
migrate = Migrate(app, db)

api.add_resource(VandalismRecordListResource, '/record')
api.add_resource(VandalismRecordResource, '/record/<record_id>')

if __name__ == '__main__':
    app.run(debug=True)