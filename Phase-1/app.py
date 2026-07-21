from flask import Flask, jsonify, request
from models.post import Post
from models.offer import NegotiationOffer
from db import load_db, save_db

app = Flask(__name__)

@app.route("/")
def home():
    return "TradePost server is running!"

@app.route("/posts", methods=["GET"])
def get_posts():
    db = load_db()
    return jsonify(db["posts"])

@app.route("/posts", methods=["POST"])
def create_post():
    db = load_db()
    data = request.get_json()

    new_id = len(db["posts"]) + 1
    new_post = Post(
        post_id=new_id,
        title=data["title"],
        description=data["description"],
        owner_id=data["owner_id"]
    )

    db["posts"].append(new_post.to_dict())
    save_db(db)

    return jsonify(new_post.to_dict()), 201

@app.route("/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    db = load_db()

    for post in db["posts"]:
        if post["post_id"] == post_id:
            return jsonify(post)

    return jsonify({"error": "Post not found"}), 404

@app.route("/posts/<int:post_id>/offers", methods=["POST"])
def create_offer(post_id):
    db = load_db()

    target_post = None
    for post in db["posts"]:
        if post["post_id"] == post_id:
            target_post = post
            break

    if target_post is None:
        return jsonify({"error": "Post not found"}), 404

    if target_post["status"] != "Open":
        return jsonify({"error": "This post is no longer open for offers"}), 400

    data = request.get_json()

    new_offer_id = len(db["offers"]) + 1
    new_offer = NegotiationOffer(
        offer_id=new_offer_id,
        post_id=post_id,
        proposer_id=data["proposer_id"],
        offered_item_details=data["offered_item_details"],
        turn_holder_id=target_post["owner_id"]
    )

    db["offers"].append(new_offer.to_dict())
    save_db(db)

    return jsonify(new_offer.to_dict()), 201

@app.route("/posts/<int:post_id>/offers", methods=["GET"])
def get_offers_for_post(post_id):
    db = load_db()
    matching_offers = [o for o in db["offers"] if o["post_id"] == post_id]
    return jsonify(matching_offers)

if __name__ == "__main__":
    app.run(debug=True)