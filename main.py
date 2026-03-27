from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from sqlalchemy import func
import os
import logging
logging.basicConfig(level=logging.INFO)
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "DATABASE_URL",
    "sqlite:///cafes.db"
)
db = SQLAlchemy(model_class=Base)
db.init_app(app)
print("DB URI:", app.config['SQLALCHEMY_DATABASE_URI'])

# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
import random

@app.route("/random", methods=["GET"])
def random1():
    logging.info("Fetching random cafe")
    stmt = db.select(Cafe).order_by(func.random()).limit(1)
    random_cafe = db.session.execute(stmt).scalar()
    if not random_cafe:
        return jsonify(error="No cafes found in database"), 404

    # Return JSON
    return jsonify(
        id=random_cafe.id,
        name=random_cafe.name,
        map_url=random_cafe.map_url,
        img_url=random_cafe.img_url,
        location=random_cafe.location,
        seats=random_cafe.seats,
        has_toilet=random_cafe.has_toilet,
        has_wifi=random_cafe.has_wifi,
        has_sockets=random_cafe.has_sockets,
        can_take_calls=random_cafe.can_take_calls,
        coffee_price=random_cafe.coffee_price
    )


# HTTP POST - Create Record
@app.route("/all", methods=["GET"])
def get_all_cafes():
    # Use .execute + .select
    logging.info("getting all cafes")
    result = db.session.execute(db.select(Cafe)).scalars().all()
    # Convert each row to dict
    cafes = [cafe.to_dict() for cafe in result]
    # Return JSON
    return jsonify(cafes=cafes)

@app.route("/search/<loc>", methods=["GET"])
def searching(loc):
    logging.info("searching for cafe")
    stmt = db.select(Cafe).where(Cafe.location == loc)
    result = db.session.execute(stmt).scalars().all()

    if result:  # if we found cafes
        cafes = [cafe.to_dict() for cafe in result]
        return jsonify(cafes=cafes)
    else:  # no cafes found
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


@app.route("/add", methods=["POST"])
def post_new_cafe():
    if not request.form.get("name"):
        logging.info("name is empty")
        return jsonify(error="Name is required"), 400
    logging.info("adding new cafe")
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})
# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:id>", methods=["PATCH"])
def pricing(id):
    # Find the cafe by ID
    cafe = db.session.get(Cafe, id)

    if cafe:
        # Get new price from query parameter (?new_price=...)
        logging.info("getting newprice from query parameter")
        new_price = request.args.get("new_price")

        if new_price:
            logging.info("updating to new price")
            cafe.coffee_price = new_price
            db.session.commit()
            return jsonify(success={"Updated": f"Price updated to {new_price}"})
        else:
            logging.info("missing new_price info")
            return jsonify(error={"Missing": "Please provide a new_price query parameter."}), 400
    else:
        logging.info("No cafe found")
        return jsonify(error={"Not Found": "Cafe with that ID does not exist."}), 404


# HTTP DELETE - Delete Record


API_KEY = os.getenv("API_KEY", "defaultkey")

@app.route("/report-closed/<int:id>", methods=["DELETE"])
def deleting(id):
    # Check API key from query parameter (?api_key=...)
    logging.info("checking apikey in query parameter for deleting")
    client_key = request.args.get("api_key")
    if client_key != API_KEY:
        logging.info("invalid key entered ")
        return jsonify(error="Invalid API key"), 403

    # Find the cafe by ID
    cafe = db.session.get(Cafe, id)
    if cafe:
        db.session.delete(cafe)
        db.session.commit()
        logging.info("cafe deleted")
        return jsonify(success="Cafe deleted"), 200
    else:
        logging.info("cafe not found for deleting")
        return jsonify(error="Cafe not found"), 404





if __name__ == '__main__':
    app.run(debug=True)
