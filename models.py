from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(180), nullable=False)
    property_type = db.Column(db.String(60), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    amenities = db.relationship(
        "Amenity",
        backref="property",
        cascade="all, delete-orphan",
        lazy=True,
    )

    @property
    def formatted_price(self):
        return f"${self.price:,.0f}"


class Amenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey("property.id"), nullable=False)
