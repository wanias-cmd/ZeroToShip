from flask import Flask, jsonify, request, session, render_template, redirect, url_for
from models.post import Post
from models.offer import NegotiationOffer
from db import load_db, save_db
from views.auth import auth_bp, login_required
from views.routes import api_bp
from models.logic import create_offer, accept_offer as accept_offer_logic

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-later"
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)


@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = load_db()
    return render_template("index.html", posts=db["posts"], user_id=session["user_id"])


@app.route("/posts/create", methods=["POST"])
@login_required
def create_post_form():
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
@login_required
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
        return redirect(url_for("auth.login"))

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

@app.route("/negotiations")
@login_required
def negotiations():
    db = load_db()
    user_id = session["user_id"]

    my_offers = []
    for offer in db["offers"]:
        post = None
        for p in db["posts"]:
            if p["post_id"] == offer["post_id"]:
                post = p
                break
        if post is None:
            continue

        if offer["proposer_id"] == user_id or post["owner_id"] == user_id:
            my_offers.append({"offer": offer, "post": post})

    return render_template("negotiations.html", my_offers=my_offers, user_id=user_id)


@app.route("/api/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    db = load_db()

    for post in db["posts"]:
        if post["post_id"] == post_id:
            return jsonify(post)

    return jsonify({"error": "Post not found"}), 404


@app.route("/posts/<int:post_id>/offers", methods=["POST"])
@login_required
def create_offer_api(post_id):
    db = load_db()

    offer, error, status = create_offer(
        db,
        post_id=post_id,
        proposer_id=request.get_json()["proposer_id"],
        offered_item_details=request.get_json()["offered_item_details"]
    )

    if error:
        return jsonify({"error": error}), status

    save_db(db)
    return jsonify(offer), status


@app.route("/posts/<int:post_id>/offers", methods=["GET"])
def get_offers_for_post(post_id):
    db = load_db()
    matching_offers = [o for o in db["offers"] if o["post_id"] == post_id]
    return jsonify(matching_offers)


@app.route("/posts/<int:post_id>/offers/<int:offer_id>/accept", methods=["POST"])
@login_required
def accept_offer_api(post_id, offer_id):
    db = load_db()

    target_post = None
    for post in db["posts"]:
        if post["post_id"] == post_id:
            target_post = post
            break

    if target_post is None:
        return jsonify({"error": "Post not found"}), 404

    if session["user_id"] != target_post["owner_id"]:
        return jsonify({"error": "You are not authorized to accept this offer"}), 403

    target_offer = None
    for offer in db["offers"]:
        if offer["offer_id"] == offer_id and offer["post_id"] == post_id:
            target_offer = offer
            break

    if target_offer is None:
        return jsonify({"error": "Offer not found for this post"}), 404

    if session["user_id"] == target_offer["proposer_id"]:
        return jsonify({"error": "You cannot accept your own offer"}), 400

    offer_result, error, status = accept_offer_logic(db, post_id, offer_id)

    if error:
        return jsonify({"error": error}), status

    save_db(db)
    return jsonify(offer_result), status


@app.route("/posts/<int:post_id>/offers/create", methods=["POST"])
@login_required
def create_offer_form(post_id):
    db = load_db()

    offer, error, status = create_offer(
        db,
        post_id=post_id,
        proposer_id=session["user_id"],
        offered_item_details=request.form["offered_item_details"]
    )

    if not error:
        save_db(db)

    return redirect(url_for("view_post", post_id=post_id))


@app.route("/posts/<int:post_id>/offers/<int:offer_id>/accept-form", methods=["POST"])
@login_required
def accept_offer_form(post_id, offer_id):
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

    if target_post is None or target_offer is None:
        return redirect(url_for("index"))

    if session["user_id"] != target_post["owner_id"]:
        return "You are not authorized to accept this offer", 403
    if session["user_id"] == target_offer["proposer_id"]:
        return "You cannot accept your own offer", 400

    _, error, status = accept_offer_logic(db, post_id, offer_id)

    if not error:
        save_db(db)

    return redirect(url_for("view_post", post_id=post_id))


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("auth.login"))


if __name__ == "__main__":
    app.run(debug=True)