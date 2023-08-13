import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app import schemas
from app.decorators import validate_schema

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"].replace(
    "://", "ql://", 1
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return "<User %r>" % self.username


class PaymentGuarantee(db.Model):
    __tablename__ = "payment_guarantees"
    id = db.Column(db.Integer, primary_key=True)
    ref_id = db.Column(db.String(124), unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)

    first_name = db.Column(db.String(124))
    last_name = db.Column(db.String(124))
    cell_phone_number = db.Column(db.String(124))
    email = db.Column(db.String(124))


class Bookings(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    pg_id = db.Column(db.Integer, db.ForeignKey("payment_guarantees.id"), index=True)
    booking_time = db.Column(db.DateTime)
    creation_time = db.Column(db.DateTime)


@app.route("/", methods=["POST"])
@validate_schema
def check(booking_form: schemas.BookAppointment):
    print(booking_form)
    pg = PaymentGuarantee.query.filter_by(email=booking_form.email).all()
    print(pg)
    return jsonify({"existing_payment_guarantees": len(pg)})


@app.route("/booking", methods=["GET"])
def get_bookings():
    
    return None


@app.route("/booking", methods=["POST"])
@validate_schema
def create_booking():

    return None