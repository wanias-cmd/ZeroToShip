from flask import Flask, jsonify, request
from models.post import Post
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

if __name__ == "__main__":
    app.run(debug=True)