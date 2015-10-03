"""
Holds data about a specific Player
"""


class Player(object):
    def __init__(self, id, name):
        # int
        self.id = id
        # string
        self.name = name


# Validate a player ID
# @param playerId the player ID to validate
def validatePlayerId(playerId):
    if not isinstance(playerId, int) or playerId < 0:
        raise ValueError("Player ID {} must be a nonnegative integer.")
