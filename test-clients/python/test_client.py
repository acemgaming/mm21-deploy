#!/usr/bin/python2
import socket
import json
import random
import sys

# Python terminal colors; useful for debugging
# Make sure to concat a "printColors.RESET" to the end of your statement!
class printColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Debugging function
def log(x,c=printColors.BLUE):
    pass
    sys.stderr.write(c + str(x) + printColors.RESET + "\n")

# Set initial connection data
def initialResponse():
    # @competitors YOUR CODE HERE
    return {'teamName':'The House Party Protocol'}

# Determine actions to take on a given turn, given the server response
def processTurn(serverResponse):
    # @competitors YOUR CODE HERE

    # Helpful variables
    actions = []
    myId = serverResponse["playerInfo"]["id"]
    myNodes = [x for x in serverResponse["map"] if x["owner"] == myId]
    myP = sum(x["processingPower"] for x in myNodes)
    myN = sum(x["networkingPower"] for x in myNodes)

    # AI variables
    bestScore = 0
    target = None
    action = "control"
    turn = 0

    # Node lists
    attackedNodes = [x for x in myNodes if max(x["infiltration"]) != 0]
    otherNodes = [x for x in serverResponse["map"] if x["owner"] != myId and x["isIPSed"] == False]
    #log("Player {} P {} / N {}".format(myId, myP, myN))
    #log("MINE " + str([x["id"] for x in myNodes]))
    #log("VIS  " + str([x["id"] for x in otherNodes]))

    # 1) 1st turn throw an ips
    if turn == 0:
        runAction = 0

    # 2) Defend our nodes under attack
    if len(attackedNodes) != 0:
        for n in attackedNodes:
            score = max(n["infiltration"])*4
            if score > bestScore:
                target = n
                bestScore = score

                # Last stand of the DDoS
                if max(n["infiltration"]) > 0.5*(n["processingPower"] + n["networkingPower"]):
                    action = "ddos"

    # 3) Capture most powerful nearby node (with free ones being slightly worse than taken ones)
    if len(otherNodes) != 0:
        target = otherNodes[0]
        bestScore = 0
        for n in otherNodes:
            maxI = max(int(x) for x in n["infiltration"]) #choose the node with max infiltration
            iBoost = 0
            if not maxI:
                iBoost = (0 if int(n["infiltration"][str(myId)]) == maxI else maxI)
            score = n["processingPower"] + n["networkingPower"] - iBoost
            if myP < myN:
                score = n["networkingPower"]
            if myP > myN:
                score = n["processingPower"]

            score = score * 1.5 if n["owner"] != None else score #attacks players first
            if score > bestScore:
                target = n #sets target
                bestScore = score
                action = "control"

    #runAction = random.randint(0, 7) #original code just picked a random number
    runAction = 1

   #run clean command
    if runAction == 0:
        actions.append({
            "action": "clean",
            "target": target["id"],
        })
   #run control command
    elif runAction == 1:
	actions.append({
		"action": "control",
		"target": target["id"],
		"multiplier": min(myP, myN) #selects the minimum amount of proc and net power
	})
   #run ddos command
    elif runAction == 2:
        actions.append({
            "action": "ddos",
            "target": myNodes[0]['id'] 
        })
   #run ips command
    elif runAction == 3:
        actions.append({
            "action": "ips",
            "target": myNodes[0]['id'] 
        })
   #run port scan command
    elif runAction == 4:
        actions.append({
            "action": "portscan",
            "target": target["id"]
        })
   #run rootkit command
    elif runAction == 5:
        actions.append({
            "action": "rootkit",
            "target": target["id"]
        })
 #run scan command
    elif rand == 6:
        actions.append({
            "action": "scan",
            "target": target["id"]
        })
 #run upgrade command
    elif runAction == 7:
        actions.append({
            "action": "upgrade",
            "target": target["id"]
        })

    #increment turn
    turn = turn + 1
    log(turn)

    # Send actions to the server
    return {
        'teamName': 'The House Party Protocol',
        'actions': actions
    }

# Main method
# @competitors DO NOT MODIFY
if __name__ == "__main__":

    # Config
    conn = ('localhost', 1337)
    if len(sys.argv) > 2:
        conn = (sys.argv[1], int(sys.argv[2]))

    # Handshake
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(conn)

    # Initial connection
    s.sendall(json.dumps(initialResponse()) + '\n')

    # Initialize test client
    game_running = True
    members = None

    # Run game
    data = s.recv(1024)
    while len(data) > 0 and game_running:
        value = None
        if "\n" in data:
            data = data.split('\n')
            if len(data) > 1 and data[1] != "":
                data = data[1]
                data += s.recv(1024)
            else:
                value = json.loads(data[0])

                # Check game status
                if 'winner' in value:
                    game_running = False

                # Send next turn (if appropriate)
                else:
                    msg = processTurn(value) if "map" in value else initialResponse()
                    s.sendall(json.dumps(msg) + '\n')
                    data = s.recv(1024)
        else:
            data += s.recv(1024)
    s.close()
