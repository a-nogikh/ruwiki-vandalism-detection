from dependencies import db


class VandalismRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)