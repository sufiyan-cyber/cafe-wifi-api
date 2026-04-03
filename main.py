from flask import Flask, jsonify, request,render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, Float
from sqlalchemy import func
import os
import logging
logging.basicConfig(level=logging.INFO)
from dotenv import load_dotenv
load_dotenv()
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# ── Base ────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── DB Connection ────────────────────────────────────────────
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "DATABASE_URL"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(model_class=Base)
db.init_app(app)

logging.info("DB URI loaded from environment")


# ── Model ────────────────────────────────────────────────────
class Cafe(db.Model):
    __tablename__ = 'cafe'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    online_order: Mapped[bool] = mapped_column(Boolean, nullable=True)
    book_table: Mapped[bool] = mapped_column(Boolean, nullable=True)
    rate: Mapped[float] = mapped_column(Float, nullable=True, index=True)
    votes: Mapped[int] = mapped_column(Integer, nullable=True)
    location: Mapped[str] = mapped_column(String(250), nullable=True, index=True)
    rest_type: Mapped[str] = mapped_column(String(500), nullable=True)
    dish_liked: Mapped[str] = mapped_column(String(1000), nullable=True)
    cuisines: Mapped[str] = mapped_column(String(500), nullable=True)
    approx_cost: Mapped[int] = mapped_column(Integer, nullable=True)
    listed_in_type: Mapped[str] = mapped_column(String(250), nullable=True)
    listed_in_city: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'location': self.location,
            'rate': self.rate,
            'votes': self.votes,
            'online_order': self.online_order,
            'book_table': self.book_table,
            'approx_cost': self.approx_cost,
            # comma-separated strings → proper lists in JSON
            'rest_type': [r.strip() for r in self.rest_type.split(',')] if self.rest_type else [],
            'cuisines': [c.strip() for c in self.cuisines.split(',')] if self.cuisines else [],
            'dish_liked': [d.strip() for d in self.dish_liked.split(',')] if self.dish_liked else [],
            'listed_in_type': self.listed_in_type,
            'listed_in_city': self.listed_in_city,
        }

'''
this here is not needed once u switch to cloud This block runs at startup and tries to connect to DB before workers are ready, causing the timeout
with app.app_context():
    db.create_all()
'''

# ── API Key ──────────────────────────────────────────────────
API_KEY = os.getenv("API_KEY", "defaultkey")

def check_api_key():
    """Helper — reads key from Authorization header: Bearer <key>"""
    auth = request.headers.get("Authorization", "")
    token = auth.replace("Bearer ", "").strip()
    return token == API_KEY


# ════════════════════════════════════════════════════════════
#  ROUTES
# ════════════════════════════════════════════════════════════

@app.route("/")
def home():
    return render_template("index.html")


# ── GET /random ──────────────────────────────────────────────
@app.route("/random", methods=["GET"])
def random_cafe():
    logging.info("Fetching random cafe")
    cafe = db.session.execute(
        db.select(Cafe).order_by(func.random()).limit(1)
    ).scalar()
    if not cafe:
        return jsonify(error="No cafes found"), 404
    return jsonify(cafe=cafe.to_dict()), 200


# ── GET /all?page=1&per_page=20 ──────────────────────────────
@app.route("/all", methods=["GET"])
def get_all_cafes():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    logging.info(f"Getting all cafes — page {page}, per_page {per_page}")

    paginated = db.paginate(
        db.select(Cafe).order_by(
            func.random()
        ),
        page=page,
        per_page=per_page,
        error_out=False
    )
    return jsonify({
        'cafes': [c.to_dict() for c in paginated.items],
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': per_page
    }), 200


# ── GET /search?location=Koramangala&min_rate=4.2&max_cost=800&online_order=true ──
@app.route("/search", methods=["GET"])
def search():
    location = request.args.get('location', '').strip()
    min_rate = request.args.get('min_rate', type=float)
    max_cost = request.args.get('max_cost', type=int)
    online = request.args.get('online_order', '').strip().lower()

    logging.info(f"Search — location={location} min_rate={min_rate} max_cost={max_cost} online={online}")

    stmt = db.select(Cafe)

    if location:
        stmt = stmt.where(Cafe.location.ilike(f"%{location}%"))
    if min_rate is not None:
        stmt = stmt.where(Cafe.rate >= min_rate)
    if max_cost is not None:
        stmt = stmt.where(Cafe.approx_cost <= max_cost)
    if online in ('true', 'false'):
        stmt = stmt.where(Cafe.online_order == (online == 'true'))

    stmt = stmt.order_by(Cafe.name, Cafe.location, Cafe.rate.desc())
    stmt = stmt.distinct(Cafe.name, Cafe.location)
    result = db.session.execute(stmt).scalars().all()

    if not result:
        return jsonify(error="No cafes found matching your filters"), 404

    return jsonify(cafes=[c.to_dict() for c in result]), 200


# ── GET /locations — unique location list for frontend dropdowns ──
@app.route("/locations", methods=["GET"])
def get_locations():
    logging.info("Fetching all unique locations")
    rows = db.session.execute(
        db.select(Cafe.location).distinct().order_by(Cafe.location)
    ).scalars().all()
    return jsonify(locations=[r for r in rows if r]), 200


# ── POST /add ────────────────────────────────────────────────
@app.route("/add", methods=["POST"])
def add_cafe():
    if not check_api_key():
        return jsonify(error="Unauthorised"), 403

    data = request.get_json() or request.form

    if not data.get("name") or not data.get("location"):
        return jsonify(error="name and location are required"), 400

    logging.info(f"Adding new cafe: {data.get('name')}")

    new_cafe = Cafe(
        name=data.get("name"),
        address=data.get("address"),
        location=data.get("location"),
        online_order=str(data.get("online_order", "false")).lower() == "true",
        book_table=str(data.get("book_table", "false")).lower() == "true",
        rate=data.get("rate"),
        votes=data.get("votes", 0),
        rest_type=data.get("rest_type"),
        dish_liked=data.get("dish_liked"),
        cuisines=data.get("cuisines"),
        approx_cost=data.get("approx_cost"),
        listed_in_type=data.get("listed_in_type"),
        listed_in_city=data.get("listed_in_city"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(success="Cafe added successfully", cafe=new_cafe.to_dict()), 201


# ── PATCH /update-price/<id> ─────────────────────────────────
@app.route("/update-price/<int:id>", methods=["PATCH"])
def update_price(id):
    if not check_api_key():
        return jsonify(error="Unauthorised"), 403

    cafe = db.session.get(Cafe, id)
    if not cafe:
        return jsonify(error="Cafe not found"), 404

    new_cost = request.args.get("new_cost", type=int)
    if new_cost is None:
        return jsonify(error="Provide ?new_cost=<int> as query param"), 400

    logging.info(f"Updating approx_cost for cafe {id} to {new_cost}")
    cafe.approx_cost = new_cost
    db.session.commit()
    return jsonify(success=f"Cost updated to {new_cost}"), 200


# ── DELETE /report-closed/<id> ───────────────────────────────
@app.route("/report-closed/<int:id>", methods=["DELETE"])
def delete_cafe(id):
    if not check_api_key():
        logging.warning("Unauthorised delete attempt")
        return jsonify(error="Invalid or missing API key"), 403

    cafe = db.session.get(Cafe, id)
    if not cafe:
        return jsonify(error="Cafe not found"), 404

    db.session.delete(cafe)
    db.session.commit()
    logging.info(f"Cafe {id} deleted")
    return jsonify(success="Cafe deleted"), 200


# ════════════════════════════════════════════════════════════
if __name__ == '__main__':
    app.run(debug=True)