import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app import schemas
from app.decorators import validate_schema
from datetime import datetime

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

class EventLog(db.Model):
    __tablename__ = "event_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    param = db.Column(db.String(64), index=True)
    value = db.Column(db.Text())

    user = db.relationship("User", back_populates="event_logs")
    user_query = db.relationship(
        "User",
        back_populates="event_logs_query",
        uselist=True,
        viewonly=True,
    )

    @staticmethod
    def log(user_id, param, value=None):
        if isinstance(value, dict):
            value = json.dumps(value)
        if isinstance(user_id, list):
            for u_id in user_id:
                log = EventLog(user_id=u_id, param=param, value=value)
                db.session.add(log)
        else:
            log = EventLog(user_id=user_id, param=param, value=value)
            db.session.add(log)
        db.session.commit()


@app.route("/", methods=["POST"])
@validate_schema
def check(booking_form: schemas.BookAppointment):
    print(booking_form)
    pg = PaymentGuarantee.query.filter_by(email=booking_form.email).all()
    print(pg)
    return jsonify({"existing_payment_guarantees": len(pg)})
