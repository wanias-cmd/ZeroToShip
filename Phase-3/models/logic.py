from models.offer import NegotiationOffer


def get_open_posts(db):
    return [p for p in db["posts"] if p.get("status") == "Open"]


def find_post(db, post_id):
    for post in db["posts"]:
        if post["post_id"] == post_id:
            return post
    return None


def find_offer(db, offer_id):
    for offer in db["offers"]:
        if offer["offer_id"] == offer_id:
            return offer
    return None


def create_offer(db, post_id, proposer_id, offered_item_details):
    target_post = find_post(db, post_id)
    if target_post is None:
        return None, "Post not found", 404
    if target_post["status"] != "Open":
        return None, "This post is no longer open for offers", 400

    new_offer_id = len(db["offers"]) + 1
    new_offer = NegotiationOffer(
        offer_id=new_offer_id,
        post_id=post_id,
        proposer_id=proposer_id,
        offered_item_details=offered_item_details,
        turn_holder_id=target_post["owner_id"]
    )
    db["offers"].append(new_offer.to_dict())
    return new_offer.to_dict(), None, 201


def submit_counter_offer(db, offer_id, new_terms, actor_id):
    offer = find_offer(db, offer_id)
    if offer is None:
        return None, "Offer not found", 404
    if offer.get("status", "Pending") != "Pending":
        return None, "This offer is no longer pending", 400

    target_post = find_post(db, offer["post_id"])
    if target_post is None:
        return None, "Post not found", 404

    if actor_id != offer["turn_holder_id"]:
        return None, "It is not your turn to counter this offer", 403

    offer["offered_item_details"] = new_terms

    if offer["turn_holder_id"] == target_post["owner_id"]:
        offer["turn_holder_id"] = offer["proposer_id"]
    else:
        offer["turn_holder_id"] = target_post["owner_id"]

    return offer, None, 200


def accept_offer(db, post_id, offer_id):
    target_post = find_post(db, post_id)
    if target_post is None:
        return None, "Post not found", 404
    if target_post["status"] != "Open":
        return None, "This post is already closed", 400

    target_offer = None
    for offer in db["offers"]:
        if offer["offer_id"] == offer_id and offer["post_id"] == post_id:
            target_offer = offer
            break
    if target_offer is None:
        return None, "Offer not found for this post", 404
    if target_offer.get("status", "Pending") != "Pending":
        return None, "This offer is no longer pending", 400

    target_offer["status"] = "Accepted"

    for offer in db["offers"]:
        if offer["post_id"] == post_id and offer["offer_id"] != offer_id and offer.get("status", "Pending") == "Pending":
            offer["status"] = "Declined"

    target_post["status"] = "Traded"

    return target_offer, None, 200