"""
Holds data about the map
"""

import src.game_constants
import json
import random
from player import validatePlayerId
from node import *


class DuplicatePlayerException(Exception):
    pass


class DuplicateNodeException(Exception):
    pass


class MapReadException(Exception):
    pass


class MapFormatException(Exception):
    pass


class GameMap(object):
    def __init__(self, mapPath=None):

        # Initial values
        self.players = []
        self.portScans = []

        # Load map file (if appropriate)
        if mapPath:
            # Read map file
            try:
                mapText = None
                with open(mapPath, "r") as f:
                    mapText = str(f.read().decode("string-escape").strip('"'))
            except IOError:
                raise MapReadException("Error reading map file {}.".format(mapPath))
            # Store map object
            # TODO: Make map-generator 0-indexed instead of doing it here
            try:
                mapJson = json.loads(mapText)
                self.nodes = {int(x["id"]): Node(int(x["id"]), [int(n) for n in x["adjacent-nodes"]], x["type"], self) for x in mapJson["nodes"]}
            except:
                raise MapFormatException("Invalid map file format.")

        # Use a "null" map
        else:
            self.nodes = []

    # Add a player and assign them a starting node
    # @param playerId The ID of the player to add
    def addPlayer(self, playerId):

        # Validate player ID (since this is crucial later throughout the game)
        validatePlayerId(playerId)

        # Add player
        if playerId in self.players:
            raise DuplicatePlayerException("playerId {} is already in players".format(playerId))
        self.players.append(playerId)

        # Initialize infiltration values
        for n in self.nodes.values():
            n.infiltration[playerId] = 0

        # Assign starting node
        freeNodes = self.getNodesOfType("Large City")  # TODO make this "fairer"
        freeNodes = [x for x in freeNodes if x.ownerId == -1]
        startNode = random.choice(freeNodes)
        startNode.own(playerId)
        startNode.isIPSed = True

        # Done!
        return

    # Get all nodes of a given type (e.g. all ISPs)
    # @param nodetype The node type to filter by (as a string)
    def getNodesOfType(self, nodetype):
        return [x for x in self.nodes.values() if x.nodetype == nodetype]

    # Get all nodes owned by a given player
    # @param nodetype The player ID to filter by (as an int)
    def getPlayerNodes(self, playerId):
        validatePlayerId(playerId)
        return [x for x in self.nodes.values() if x.ownerId == playerId]

    # Reset the map after a turn has finished
    def resetAfterTurn(self):

        # Map updates
        self.portScans = []

        # Node updates
        for n in self.nodes.values():

            # Update DDoS status
            n.DDoSed = n.DDoSPending
            n.DDoSPending = False

            # Update scan status
            n.scanPending = False

            # Update upgrade level
            if n.upgradePending:
                n.upgradeLevel += 1
                n.upgradePending = False

                n.processing += n.initialProcessing / 10
                n.networking += n.initialNetworking / 10
                n.totalPower = n.processing + n.networking

            # Reset remaining resource counts
            n.remainingProcessing = 0 if n.DDoSed else n.processing
            n.remainingNetworking = 0 if n.DDoSed else n.networking

            # Reset targeter/supplier IDs (defensive programming)
            n.targeterId = None
            n.supplierIds = []

            # Zero-clamp infiltration levels
            # We do this here so that heals that come before attacks still count
            for x in n.infiltration.iterkeys():
                n.infiltration[x] = max(n.infiltration[x], 0)

            # Update owned-states
            # We do this here so that people can't conquer a node by being earlier in the turn order
            inf = max(n.infiltration.values())
            if inf > n.totalPower * 2:
                maxPlayers = [x for x in n.infiltration if n.infiltration[x] == inf]
                n.own(random.choice(maxPlayers))  # Don't favor lower/higher player IDs

        # IPS status updates
        ipsChangedNodes = [x for x in self.nodes.values() if x.IPSPending]
        ipsChangedPlayers = set([x.ownerId for x in ipsChangedNodes])
        for pId in ipsChangedPlayers:
            pNodes = self.getPlayerNodes(pId)
            ipsedNodes = [x for x in pNodes if x.ownerId == pId and x.IPSPending]
            if len(ipsedNodes) != 0:
                for n in pNodes:
                    n.isIPSed = False
                for n in ipsedNodes:
                    n.IPSPending = False
                ipsedNodes[-1].isIPSed = True  # Use the last-IPSed node
