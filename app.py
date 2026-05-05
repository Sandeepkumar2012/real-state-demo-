import os
from decimal import Decimal, InvalidOperation

from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from models import Amenity, Property, db


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-real-estate-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "realestate.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    db.init_app(app)

    with app.app_context():
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        db.create_all()
        seed_properties()

    register_routes(app)
    return app


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_price(value):
    if not value:
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None


def seed_properties():
    if Property.query.count() > 0:
        return

    properties = [
        {
            "title": "Skyline Residences",
            "price": Decimal("825000"),
            "city": "Mumbai",
            "location": "Worli, Mumbai",
            "property_type": "Apartment",
            "description": "A high-floor apartment with sea-facing views, refined finishes, and quick access to business districts.",
            "image_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
            "featured": True,
            "amenities": ["Sea view", "Gym", "Covered parking", "Security"],
        },
        {
            "title": "Palm Court Villa",
            "price": Decimal("1280000"),
            "city": "Bengaluru",
            "location": "Whitefield, Bengaluru",
            "property_type": "Villa",
            "description": "A spacious villa with private garden space, generous bedrooms, and a quiet gated community setting.",
            "image_url": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1200&q=80",
            "featured": True,
            "amenities": ["Private garden", "Clubhouse", "Pool", "Smart locks"],
        },
        {
            "title": "Urban Nest Studio",
            "price": Decimal("245000"),
            "city": "Pune",
            "location": "Koregaon Park, Pune",
            "property_type": "Studio",
            "description": "A compact, move-in-ready studio designed for professionals who want a central location and low upkeep.",
            "image_url": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1200&q=80",
            "featured": True,
            "amenities": ["Furnished", "Lift", "Power backup", "Pet friendly"],
        },
        {
            "title": "Green Meadows Plot",
            "price": Decimal("410000"),
            "city": "Hyderabad",
            "location": "Kokapet, Hyderabad",
            "property_type": "Plot",
            "description": "A well-connected residential plot in a fast-growing neighborhood with wide roads and utilities nearby.",
            "image_url": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1200&q=80",
            "featured": False,
            "amenities": ["Clear title", "Gated layout", "Water access", "Wide roads"],
        },
        {
            "title": "Lakeview Heights",
            "price": Decimal("690000"),
            "city": "Chennai",
            "location": "OMR, Chennai",
            "property_type": "Apartment",
            "description": "A modern three-bedroom apartment with balcony views, quality amenities, and excellent road connectivity.",
            "image_url": "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1200&q=80",
            "featured": False,
            "amenities": ["Balcony", "Children's play area", "Gym", "EV charging"],
        },
        {
            "title": "Heritage Row House",
            "price": Decimal("535000"),
            "city": "Delhi",
            "location": "Greater Kailash, Delhi",
            "property_type": "House",
            "description": "A renovated row house with warm interiors, flexible living areas, and access to premium city conveniences.",
            "image_url": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=1200&q=80",
            "featured": False,
            "amenities": ["Terrace", "Modular kitchen", "Storage", "Near metro"],
        },
    ]

    for item in properties:
        amenities = item.pop("amenities")
        prop = Property(**item)
        prop.amenities = [Amenity(name=name) for name in amenities]
        db.session.add(prop)
    db.session.commit()


def register_routes(app):
    @app.route("/")
    def index():
        featured_properties = Property.query.filter_by(featured=True).limit(6).all()
        return render_template("index.html", featured_properties=featured_properties)

    @app.route("/listings")
    def listings():
        page = request.args.get("page", 1, type=int)
        min_price = parse_price(request.args.get("min_price"))
        max_price = parse_price(request.args.get("max_price"))
        property_type = request.args.get("property_type", "").strip()
        city = request.args.get("city", "").strip()

        query = Property.query.order_by(Property.created_at.desc())
        if min_price is not None:
            query = query.filter(Property.price >= min_price)
        if max_price is not None:
            query = query.filter(Property.price <= max_price)
        if property_type:
            query = query.filter(Property.property_type == property_type)
        if city:
            query = query.filter(Property.city == city)

        pagination = query.paginate(page=page, per_page=6, error_out=False)
        types = [row[0] for row in db.session.query(Property.property_type).distinct().order_by(Property.property_type)]
        cities = [row[0] for row in db.session.query(Property.city).distinct().order_by(Property.city)]

        return render_template(
            "listings.html",
            pagination=pagination,
            properties=pagination.items,
            types=types,
            cities=cities,
            filters={
                "min_price": request.args.get("min_price", ""),
                "max_price": request.args.get("max_price", ""),
                "property_type": property_type,
                "city": city,
            },
        )

    @app.route("/property/<int:property_id>", methods=["GET", "POST"])
    def detail(property_id):
        prop = Property.query.get_or_404(property_id)
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            message = request.form.get("message", "").strip()
            if not name or not email or not message:
                flash("Please complete all contact fields.", "warning")
            else:
                flash("Thanks. Your message has been sent to the listing team.", "success")
                return redirect(url_for("detail", property_id=prop.id))
        return render_template("detail.html", property=prop)

    @app.route("/add", methods=["GET", "POST"])
    def add_property():
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            price = parse_price(request.form.get("price", ""))
            city = request.form.get("city", "").strip()
            location = request.form.get("location", "").strip()
            property_type = request.form.get("property_type", "").strip()
            description = request.form.get("description", "").strip()
            amenities_text = request.form.get("amenities", "").strip()
            featured = request.form.get("featured") == "on"
            image = request.files.get("image")

            if not all([title, price, city, location, property_type, description]):
                flash("Please fill in all required fields.", "warning")
                return render_template("add.html")

            image_url = "https://images.unsplash.com/photo-1560185007-cde436f6a4d0?auto=format&fit=crop&w=1200&q=80"
            if image and image.filename:
                if not allowed_file(image.filename):
                    flash("Upload a PNG, JPG, JPEG, WEBP, or GIF image.", "warning")
                    return render_template("add.html")
                filename = secure_filename(image.filename)
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                image.save(save_path)
                image_url = url_for("static", filename=f"uploads/{filename}")

            prop = Property(
                title=title,
                price=price,
                city=city,
                location=location,
                property_type=property_type,
                description=description,
                image_url=image_url,
                featured=featured,
            )
            prop.amenities = [
                Amenity(name=item.strip())
                for item in amenities_text.split(",")
                if item.strip()
            ]
            db.session.add(prop)
            db.session.commit()
            flash("Property added successfully.", "success")
            return redirect(url_for("detail", property_id=prop.id))

        return render_template("add.html")


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
