import os
import flask_login
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app import schemas
from app.decorators import validate_schema
from datetime import datetime
import logging

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"].replace(
    "://", "ql://", 1
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    api_key = db.Column(db.String(124))

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


@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Bearer ', '', 1)
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    return None


def is_authenticated():
    logging.info("Check whether user is authenticated.")
    try:
        if flask_login.current_user.is_authenticated is False:
            logging.info("The user is not authenticated, proceeding with AnonymousUser.")
            return False

    # If the user is authenticated, then it is not an AnonymousUser and therefore
    # it does not have the `is_authenticated` attribute.
    except AttributeError:
        logging.info("The user authenticated, ID : %s.", flask_login.current_user.id)


@app.route("/", methods=["POST"])
@validate_schema
def check(booking_form: schemas.BookAppointment):
    print(booking_form)
    pg = PaymentGuarantee.query.filter_by(email=booking_form.email).all()
    print(pg)
    return jsonify({"existing_payment_guarantees": len(pg)})


@app.route("/booking", methods=["GET"])
def get_bookings():
    logging.info("Received GET request against endpoint '/booking'.")
    
    if is_authenticated() is False:
        return jsonify({"message": "unauthorized"}), 401

    args = request.args
    pg_id = args.get("pg_id")
    booking_time = args.get("booking_time")

    logging.info("Attributes provided, pg_id: %s, booking_time: %s.", pg_id, booking_time)

    query = Bookings.query
    if pg_id is not None:
        query = query.filter_by(pg_id=pg_id)
    if booking_time is not None:
        booking_time = datetime.fromisoformat(booking_time)
        query = query.filter_by(booking_time=booking_time)

    filtered_bookings = query.all()

    user_bookings = []
    for booking in filtered_bookings:
        pg = PaymentGuarantee.query.filter_by(id=booking.pg_id).first()
        if pg.user_id == flask_login.current_user.id:
            user_bookings.append(booking)

    resp = {
        "bookings": [
            {
                "id": booking.id,
                "pg_id": booking.pg_id,
                "booking_time": booking.booking_time,
                "creation_time": booking.creation_time
            } for booking in user_bookings
        ]
    }
    
    logging.info("Response for user %s: %s.", pg.user_id, resp)

    return jsonify(resp), 200


@app.route("/booking", methods=["POST"])
@validate_schema
def create_booking(booking_form: schemas.Booking):
    logging.info("Received POST request against endpoint '/booking'.")

    if is_authenticated() is False:
        return jsonify({"message": "unauthorized"}), 401

    id = booking_form.id
    pg_id = booking_form.pg_id
    booking_time = datetime.fromisoformat(booking_form.booking_time)
    creation_time = datetime.utcnow()

    logging.info("Received following form for booking creation, id: %s, pg_id: %s, booking_time: %s",id, pg_id, booking_time)

    pg = PaymentGuarantee.query.filter_by(id=pg_id).first()
    user = User.query.filter_by(id=pg.user_id).first()

    if flask_login.current_user != user:
        logging.info("User: %s cannot book the booking covered by PG: %s", flask_login.current_user.id, pg.id)
        return jsonify({"message": "forbidden"}, 403)

    new_booking = Bookings(id=id, pg_id=pg_id, booking_time=booking_time, creation_time=creation_time)
    db.session.add(new_booking)
    db.session.commit()

    logging.info("User: %s created booking: %s using the PG: %s", user.id, new_booking.id, pg.id)

    return jsonify({"message": "booking created successfully"}), 201