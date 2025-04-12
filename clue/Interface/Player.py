# Simulate the Player class (server-side player data).
class DumbPlayer:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name  # Return the player's name as the string representation

    def to_dict(self):
        return {"name": self.name}
