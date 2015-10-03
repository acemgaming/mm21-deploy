"""
Holds data about a specific node on the map
"""

from src.game_constants import *
from src.misc_constants import *
import json as JSON


class RepeatedActionException(Exception):
    pass


class MultiplierMustBePositiveException(Exception):
    pass


class NodeIsDDoSedException(Exception):
    pass


class ActionOwnershipException(Exception):
    pass


class InsufficientPowerException(Exception):
    pass


class IpsPreventsActionException(Exception):
    pass


class DeveloperErrorException(Exception):
    pass


class Node(object):
    def __init__(self, id, adjacent, nodetype, gamemap):
        # int
        self.id = id
        self.nodetype = nodetype
        self.processing = NodeType.processing[nodetype]
        self.networking = NodeType.networking[nodetype]
        self.initialProcessing = self.processing
        self.initialNetworking = self.networking
        self.remainingProcessing = self.processing
        self.remainingNetworking = self.networking
        self.totalPower = self.processing + self.networking
        self.ownerId = -1
        self.targeterId = None
        self.upgradeLevel = 0
        self.upgradePending = False
        self.scanPending = False
        # int[]
        self.adjacentIds = adjacent
        self.rootkitIds = []
        self.supplierIds = []
        # bool
        self.DDoSed = False
        self.DDoSPending = False
        self.isIPSed = False
        self.IPSPending = False
        # dict<int, int>
        self.infiltration = dict()
        # object
        self.map = gamemap

    def getAdjacentNodes(self):
        return [self.map.nodes[nId] for nId in self.adjacentIds]

    def toPlayerDict(self, showRootkits):
        return {
            "id": self.id,
            "nodetype": self.nodetype,
            "processingPower": self.processing,
            "networkingPower": self.networking,
            "totalPower": self.totalPower,
            "owner": self.ownerId,
            "adjacentIds": self.adjacentIds,
            "isIPSed": self.isIPSed,
            "isDDoSed": self.DDoSed,
            "infiltration": self.infiltration,
            "upgradeLevel": self.upgradeLevel,
            "rootkits": self.rootkitIds if showRootkits else []
        }

    """
    Map functions
    """
    # Decrement the power of connected nodes
    # @param processing The processing power required
    # @param networking The networking power required
    # @param supplierIds The nodes to take power from before any others
    # @returns The nodes the power was taken from (if successful)
    def decrementPower(self, processing, networking, supplierIds):

        # Require valid targeter ID
        self.requireTargeterID()

        # Make sure values are positive
        if processing < 0 or networking < 0:
            raise ValueError("Required processing/networking power values must be at least 0.")

        # Get connected nodes
        connectedNodes = [self] if self.ownerId == self.targeterId else []
        for n in self.getAdjacentNodes():
            n.getClusteredNodesPlusRootKit(connectedNodes, self.targeterId)

        # Filter specified-supplier nodes
        for x in supplierIds:
            if x not in self.map.nodes:
                raise KeyError("Invalid supplier node ID")
        supplierNodes = [x for x in [self.map.nodes[y] for y in supplierIds] if x in connectedNodes]

        # Make sure connected nodes have required resource amounts
        totalProcessing = 0
        totalNetworking = 0
        for node in connectedNodes:
            if not node.DDoSed:
                totalProcessing += node.remainingProcessing
                totalNetworking += node.remainingNetworking
        if totalProcessing < processing or totalNetworking < networking:
            raise InsufficientPowerException("networking = %d, processing = %d\nNeeded networking = %d, processing = %d" % (totalNetworking, totalProcessing, networking, processing))

        # Subtract used resources from connected nodes
        powerSourceNodes = []
        for nodeList in [supplierNodes, connectedNodes]:
            for node in nodeList:
                if node.DDoSed:
                    continue
                if processing == 0 and networking == 0:
                    break

                difference = min(processing, node.remainingProcessing)
                node.remainingProcessing -= difference
                processing -= difference
                if difference != 0:
                    powerSourceNodes.append(node.id)

                difference = min(networking, node.remainingNetworking)
                node.remainingNetworking -= difference
                networking -= difference
                if difference != 0:
                    powerSourceNodes.append(node.id)

        # Done!
        return powerSourceNodes

    # Get all nodes that are clustered with (connected to and of the same player as) another node
    # @param clusteredNodes (Output) The list of clustered nodes
    # @param ownerId (Optional) Restrict nodes to those owned by this person; if not specified, the owner of the original node will be used
    def getClusteredNodes(self, clusteredNodes, ownerId=None):
        if ownerId is None:
            ownerId = self.ownerId
        if self.ownerId == ownerId and self not in clusteredNodes:
            clusteredNodes.append(self)
            for adjacent in self.getAdjacentNodes():
                adjacent.getClusteredNodes(clusteredNodes, ownerId)
    
    # Get all nodes that are clustered with (connected to via rootkit or adjacency and of the same player as) another node
    # @param clusteredNodes (Output) The list of clustered nodes
    # @param ownerId (Optional) Restrict nodes to those owned by this person; if not specified, the owner of the original node will be used
    
    def getClusteredNodesPlusRootKit(self, clusteredNodes, ownerId=None):
        if ownerId is None:
            ownerId = self.ownerId
        if (self.ownerId == ownerId or ownerId in self.rootkitIds) and self not in clusteredNodes:
            if self.ownerId == ownerId:
                clusteredNodes.append(self)
            for adjacent in self.getAdjacentNodes():
                adjacent.getClusteredNodes(clusteredNodes, ownerId)

    # Get all nodes visible to (clustered with or adjacent to a cluster containing) another node
    # @param visibleNodes (Output) The list of visible nodes
    # @param ownerId (Optional) Restrict traversed nodes to those owned by this person; if not specified, the owner of the original node will be used
    # @param start (Internal) True if an initial call, False otherwise
    def getVisibleNodes(self, visibleNodes, ownerId=None, start=True):
        if ownerId is None:
            ownerId = self.ownerId
        if self in visibleNodes:
            return

        branchable = self.ownerId == ownerId or ownerId in self.rootkitIds
        if branchable:
            visibleNodes.append(self)
            for adjacent in self.getAdjacentNodes():
                adjacent.getVisibleNodes(visibleNodes, ownerId, False)
        elif not start and not branchable:
            visibleNodes.append(self)

    # Determine whether a player can move through a node
    # @param playerId The ID of the player
    # @returns True if the player can move through the node, false otherwise
    def canMoveThrough(self, playerId):
        return self.ownerId == playerId or playerId in self.rootkitIds

    # Give control of a node to a player
    # @param playerId The ID of the player
    def own(self, playerId):
        if self.ownerId == playerId:
            raise ActionOwnershipException("That player already owns this node.")
        self.isIPSed = False
        self.ownerId = playerId
        self.rootkitIds = []
        self.DDoSed = False
        self.IPSPending = False
        for k in self.infiltration:
            self.infiltration[k] = 0
        return

    """
    Per-node action criteria
    """
    # Consume resources used to perform an action
    # @param processingCost The processing power required
    # @param (Optional) networkingCost The networking power required; if no value is specified, processingCost will be used
    # @returns The nodes power was drawn from 
    def requireResources(self, processingCost, networkingCost=None):
        return self.decrementPower(processingCost, networkingCost if networkingCost is not None else processingCost, self.supplierIds)

    # Throw an exception if a node is DDoSed
    # @actionName The past-tense name of the action being performed
    def requireNotDDoSed(self, actionName):
        if self.DDoSed:
            raise NodeIsDDoSedException("This node is DDoSed and can't be {}.".format(actionName))
        return self

    # Throw an exception if a node is not owned by the player performing the action
    def requireOwned(self):
        self.requireTargeterID()
        if self.targeterId != self.ownerId:
            raise ActionOwnershipException("You must own a node to perform this action on it.")
        return self

    # Throw an exception if a node is owned by the player performing the action
    def requireNotOwned(self):
        self.requireTargeterID()
        if self.targeterId == self.ownerId:
            raise ActionOwnershipException("You cannot perform this action on a node you own.")
        return self

    # Throw an exception if a node is IPSed
    def requireNotIPSed(self):
        if self.isIPSed:
            raise IpsPreventsActionException("This action cannot be performed on an IPSed node.")
        return self

    # Throw an exception if a node has an invalid targeter ID
    def requireTargeterID(self):
        if self.targeterId is None:
            raise DeveloperErrorException("Node isn't targeted.")
        return self

    # Throw an exception if a player has already port-scanned
    def requireNotPortScanned(self):
        if self.ownerId in self.map.portScans:
            raise RepeatedActionException("You may not port scan more than once per turn.")
        return self

    """
    Player actions
    """
    # Player action to infiltrate (AKA control) a node
    # @param multiplier The amount of infiltration to performi
    def doControl(self, multiplier=1):
        if multiplier <= 0:
            raise ValueError("Multiplier must be greater than 0.")
        if self.isIPSed:
            self.requireOwned()
        powerSources = self.requireNotDDoSed("controlled").requireResources(multiplier)

        # Heal your own nodes
        if self.targeterId == self.ownerId:
            for k in self.infiltration.iterkeys():
                self.infiltration[k] = self.infiltration[k] - multiplier  # Will be zero-clamped in resetAfterTurn() - doing it here causes problems

        # Attack others' nodes
        else:
            inf = self.infiltration.get(self.targeterId, 0) + multiplier
            self.infiltration[self.targeterId] = inf

        # Done!
        return powerSources

    # Player action to DDoS a node
    # Note: we allow players to DDoS the same node multiple times (and waste resources doing so) to avoid revealing whether someone else DDoSed it
    def doDDoS(self):
        powerSources = self.requireNotIPSed().requireResources(self.totalPower / 5)
        self.DDoSPending = True
        return powerSources

    # Player action to upgrade a node's Software Level
    def doUpgrade(self):
        self.requireOwned().requireNotDDoSed("upgraded")
        if self.upgradePending:
            raise RepeatedActionException("Each node can only be upgraded once per turn.")
        powerSources = self.requireResources(self.processing, self.networking)
        self.upgradePending = True
        return powerSources

    # Player action to clean a node of rootkits
    def doClean(self):
        powerSources = self.requireOwned().requireNotDDoSed("cleaned").requireResources(100, 0)
        self.rootkitIds = []
        return powerSources

    # Player action to scan a node for rootkits
    def doScan(self):
        powerSources = self.requireOwned().requireNotDDoSed("scanned").requireResources(25, 0)
        self.scanPending = True
        return powerSources

    # Player action to add a rootkit to a node
    def doRootkit(self):
        self.requireNotDDoSed("rootkitted").requireNotOwned().requireNotIPSed()
        if self.targeterId in self.rootkitIds:
            raise RepeatedActionException("This player has a rootkit here already.")
        powerSources = self.requireResources(self.totalPower / 5)
        self.rootkitIds.append(self.targeterId)
        return powerSources

    # Player action to IPS a node
    # This is the only action that can be done despite a DDoS
    def doIPS(self):
        self.requireOwned().requireNotIPSed()
        self.IPSPending = True

    # Player action to do a port scan
    def doPortScan(self):
        powerSources = self.requireOwned().requireNotPortScanned().requireNotDDoSed("port-scanned").requireResources(0, 500)
        self.map.portScans.append(self.ownerId)
        return powerSources
