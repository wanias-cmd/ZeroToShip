from flask import Flask, jsonify, request, session, render_template, redirect, url_for
from models.post import Post
from models.offer import NegotiationOffer
from db import load_db, save_db

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-later"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user_id"] = int(request.form["user_id"])
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = load_db()
    return render_template("index.html", posts=db["posts"], user_id=session["user_id"])

@app.route("/posts/create", methods=["POST"])
def create_post_form():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = load_db()

    new_id = len(db["posts"]) + 1
    new_post = Post(
        post_id=new_id,
        title=request.form["title"],
        description=request.form["description"],
        owner_id=session["user_id"]
    )

    db["posts"].append(new_post.to_dict())
    save_db(db)

    return redirect(url_for("index"))

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

@app.route("/posts/<int:post_id>")
def view_post(post_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = load_db()

    target_post = None
    for post in db["posts"]:
        if post["post_id"] == post_id:
            target_post = post
            break

    if target_post is None:
        return "Post not found", 404

    offers = [o for o in db["offers"] if o["post_id"] == post_id]

    return render_template("view_post.html", post=target_post, offers=offers, user_id=session["user_id"])

@app.route("/api/posts/<int:post_id>", methods=["GET"])
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

@app.route("/posts/<int:post_id>/offers/<int:offer_id>/accept", methods=["POST"])
def accept_offer(post_id, offer_id):
    db = load_db()

    target_post = None
    for post in db["posts"]:
        if post["post_id"] == post_id:
            target_post = post
            break

    if target_post is None:
        return jsonify({"error": "Post not found"}), 404

    if target_post["status"] != "Open":
        return jsonify({"error": "This post is already closed"}), 400

    target_offer = None
    for offer in db["offers"]:
        if offer["offer_id"] == offer_id and offer["post_id"] == post_id:
            target_offer = offer
            break

    if target_offer is None:
        return jsonify({"error": "Offer not found for this post"}), 404

    if target_offer.get("status", "Pending") != "Pending":
        return jsonify({"error": "This offer is no longer pending"}), 400

    # Accept the chosen offer
    target_offer["status"] = "Accepted"

    # Cascade: auto-decline every other pending offer on this post
    for offer in db["offers"]:
       if offer["post_id"] == post_id and offer["offer_id"] != offer_id and offer.get("status", "Pending") == "Pending":
            offer["status"] = "Declined"

    # Close the post
    target_post["status"] = "Traded"

    save_db(db)

    return jsonify(target_offer)

@app.route("/posts/<int:post_id>/offers/create", methods=["POST"])
def create_offer_form(post_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = load_db()

    target_post = None
    for post in db["posts"]:
        if post["post_id"] == post_id:
            target_post = post
            break

    if target_post is None or target_post["status"] != "Open":
        return redirect(url_for("index"))

    new_offer_id = len(db["offers"]) + 1
    new_offer = NegotiationOffer(
        offer_id=new_offer_id,
        post_id=post_id,
        proposer_id=session["user_id"],
        offered_item_details=request.form["offered_item_details"],
        turn_holder_id=target_post["owner_id"]
    )

    db["offers"].append(new_offer.to_dict())
    save_db(db)

    return redirect(url_for("view_post", post_id=post_id))


@app.route("/posts/<int:post_id>/offers/<int:offer_id>/accept-form", methods=["POST"])
def accept_offer_form(post_id, offer_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = load_db()

    target_post = None
    for post in db["posts"]:
        if post["post_id"] == post_id:
            target_post = post
            break

    target_offer = None
    for offer in db["offers"]:
        if offer["offer_id"] == offer_id and offer["post_id"] == post_id:
            target_offer = offer
            break

    if target_post and target_offer and target_post["status"] == "Open" and target_offer.get("status", "Pending") == "Pending":
        target_offer["status"] = "Accepted"
        for offer in db["offers"]:
            if offer["post_id"] == post_id and offer["offer_id"] != offer_id and offer.get("status", "Pending") == "Pending":
                offer["status"] = "Declined"
        target_post["status"] = "Traded"
        save_db(db)

    return redirect(url_for("view_post", post_id=post_id))

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)