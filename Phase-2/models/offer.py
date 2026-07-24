class NegotiationOffer:
    def __init__(self, offer_id, post_id, proposer_id, offered_item_details, turn_holder_id, status="Pending"):
        self.offer_id = offer_id
        self.post_id = post_id
        self.proposer_id = proposer_id
        self.offered_item_details = offered_item_details
        self.turn_holder_id = turn_holder_id
        self.status = status

    def to_dict(self):
        return {
            "offer_id": self.offer_id,
            "post_id": self.post_id,
            "proposer_id": self.proposer_id,
            "offered_item_details": self.offered_item_details,
            "turn_holder_id": self.turn_holder_id,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            offer_id=data["offer_id"],
            post_id=data["post_id"],
            proposer_id=data["proposer_id"],
            offered_item_details=data["offered_item_details"],
            turn_holder_id=data["turn_holder_id"],
            status=data.get("status", "Pending")
        )