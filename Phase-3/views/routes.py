from flask import Blueprint, request, jsonify
from db import load_db, save_db
from models.logic import get_open_posts, create_offer, submit_counter_offer, accept_offer

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/posts", methods=["GET"])
def api_get_posts():
    db = load_db()
    return jsonify(get_open_posts(db))


@api_bp.route("/offers", methods=["POST"])
def api_create_offer():
    db = load_db()
    data = request.get_json()

    required = ["post_id", "proposer_id", "offered_item_details"]
    if not data or any(field not in data for field in required):
        return jsonify({"error": "post_id, proposer_id, and offered_item_details are required"}), 400

    offer, error, status = create_offer(
        db,
        post_id=data["post_id"],
        proposer_id=data["proposer_id"],
        offered_item_details=data["offered_item_details"]
    )

    if error:
        return jsonify({"error": error}), status

    save_db(db)
    return jsonify(offer), status


@api_bp.route("/offers/<int:offer_id>/counter", methods=["POST"])
def api_counter_offer(offer_id):
    db = load_db()
    data = request.get_json()

    if not data or "offered_item_details" not in data or "actor_id" not in data:
        return jsonify({"error": "offered_item_details and actor_id are required"}), 400

    offer, error, status = submit_counter_offer(
        db,
        offer_id=offer_id,
        new_terms=data["offered_item_details"],
        actor_id=data["actor_id"]
    )

    if error:
        return jsonify({"error": error}), status

    save_db(db)
    return jsonify(offer), status


@api_bp.route("/posts/<int:post_id>/offers/<int:offer_id>/accept", methods=["POST"])
def api_accept_offer(post_id, offer_id):
    db = load_db()

    offer, error, status = accept_offer(db, post_id, offer_id)

    if error:
        return jsonify({"error": error}), status

    save_db(db)
    return jsonify(offer), status