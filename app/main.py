from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import pickle
import ipaddress
from collections import OrderedDict
from fastapi_utils.tasks import repeat_every
from wgnlpy import WireGuard, PublicKey

wg = WireGuard()
app = FastAPI()

interface = "wg0"


class PeerResponse(BaseModel):
    peerAddress: str
    serverAddress: str
    serverKey: str


# State will be two dicts with the following formats:
# { IPv4 address : free|assigned|active }
address_state = None

# { peer ID : IPv4 address }
peer_state = None

# Network will be an IPv4Network object that contains the assignable subnet
network = None


# Events
@app.on_event("startup")
def initialize_state():
    global network
    global address_state
    global peer_state

    # init server address
    server_address = os.getenv("WG_SERVER_ADDRESS")
    network = ipaddress.ip_interface(server_address)

    # load/init address state
    try:
        print("Trying to import address state...")
        state_file = open("address_state.pkl", "rb")
        address_state = pickle.load(state_file)
        print("Existing address state imported!")
    except FileNotFoundError:
        print("No existing address state. Initializing new state...")
        address_state = OrderedDict()

        for addr in network.network.hosts():
            address_state[addr] = "free"

        address_state[ipaddress.ip_interface(server_address).ip] = "active"

    # load/init peer state
    try:
        print("Trying to import peer state...")
        state_file = open("peer_state.pkl", "rb")
        peer_state = pickle.load(state_file)
        print("Existing peer state imported!")
    except FileNotFoundError:
        print("No existing peer state. Initializing new state...")
        peer_state = dict()


@app.on_event("shutdown")
@repeat_every(seconds=60 * 5)
def write_state():
    print("Writing state...")
    with open("address_state.pkl", "wb") as state_file:
        pickle.dump(address_state, state_file)

    with open("peer_state.pkl", "wb") as state_file:
        pickle.dump(peer_state, state_file)


# Routes
@app.post("/register")
def register_peer(peer_pub_key: str):
    # check to see if peer already in state
    if peer_pub_key in peer_state.keys():
        raise HTTPException(400, "Peer is already registered.")

    response = call_peer_register(peer_pub_key)
    return response


@app.post("/confirm")
def confirm_peer(peer_pub_key: str):
    try:
        assert peer_state[peer_pub_key]
    except KeyError:
        raise HTTPException(404, "Peer public key was not found in state.")

    if peer_state[peer_pub_key] == "active":
        raise HTTPException(400, "Peer already confirmed")

    try:
        assert PublicKey(peer_pub_key) in wg.get_interface(interface).peers
    except AssertionError:
        raise HTTPException(404, "Peer public key was not found in configuration.")

    peer_state[peer_pub_key] = "active"

    return "Peer activated"


@app.post("/deregister")
def deregister_peer(peer_pub_key: str):
    try:
        assert peer_state[peer_pub_key]
    except KeyError:
        raise HTTPException(404, "Peer public key was not found in state.")

    try:
        assert PublicKey(peer_pub_key) in wg.get_interface(interface).peers
    except AssertionError:
        raise HTTPException(404, "Peer public key was not found in configuration.")

    try:
        wg.remove_peers(interface, peer_pub_key)
        assert PublicKey(peer_pub_key) not in wg.get_interface(interface).peers
    except AssertionError:
        raise HTTPException(500, "Peer removal failed. Try again.")

    peer_add = peer_state[peer_pub_key]
    address_state[peer_add] = "free"
    del peer_state[peer_pub_key]

    return "Peer removed"


# Utils
def call_peer_register(peer_pub_key):
    server_address = str(network)
    server_key = os.getenv("WG_SERVER_PUB_KEY")

    # find first free address
    for address, state in address_state.items():
        if state == "free":
            selected = address
            break

    try:
        wg.set_peer(
            interface, peer_pub_key, allowedips=[str(selected) + "/32"],
        )
        assert PublicKey(peer_pub_key) in wg.get_interface(interface).peers
        address_state[selected] = "assigned"
        peer_state[peer_pub_key] = selected

    except ValueError as e:
        raise HTTPException(400, str(e))

    except Exception as e:
        print(e)

    response = PeerResponse(
        peerAddress=str(selected) + "/32",
        serverAddress=server_address,
        serverKey=server_key,
    )

    return response
