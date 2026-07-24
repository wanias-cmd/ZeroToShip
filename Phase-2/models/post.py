class Post:
    def __init__(self, post_id, title, description, owner_id, status="Open"):
        self.post_id = post_id
        self.title = title
        self.description = description
        self.owner_id = owner_id
        self.status = status

    def to_dict(self):
        return {
            "post_id": self.post_id,
            "title": self.title,
            "description": self.description,
            "owner_id": self.owner_id,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            post_id=data["post_id"],
            title=data["title"],
            description=data["description"],
            owner_id=data["owner_id"],
            status=data.get("status", "Open")
        )