from fastapi import FastAPI
from pydantic import BaseModel
import os
import pickle
import ipaddress
from collections import OrderedDict

app = FastAPI()


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
    server_address = os.getenv("wg_server_address")
    network = ipaddress.ip_interface(server_address)

    # load/init address state
    try:
        state_file = open("address_state.pkl", "rb")
        address_state = pickle.load(state_file)
    except FileNotFoundError:
        address_state = OrderedDict()

        for addr in network.network.hosts():
            address_state[addr] = "free"

        address_state[ipaddress.ip_interface(server_address).ip] = "active"

    # load/init peer state
    try:
        state_file = open("peer_state.pkl", "rb")
        peer_state = pickle.load(state_file)
    except FileNotFoundError:
        peer_state = dict()


@app.on_event("shutdown")
def write_state_on_shutdown():
    write_state()


# Routes
@app.post("/register")
def register_peer(peer_pub_key: str):
    response = call_peer_register(peer_pub_key)
    return response


@app.post("/confirm")
def confirm_peer(peer_pub_key: str):
    pass


@app.post("/deregister")
def deregister_peer(peer_pub_key: str):
    pass


# Utils
def call_peer_register(peer_pub_key):
    server_address = str(network)
    server_key = os.getenv("wg_server_pub_key")

    # find first free address
    for address, state in address_state.items():
        if state is "free":
            selected = address
            break

    try:
        # call config insert

        address_state[selected] = "assigned"

    response = PeerResponse(peerAddress=peer_address, serverAddress=server_address, serverKey=server_key)

    return response


def write_state():
    with open("state.pkl", "wb") as state_file:
        pickle.dump(state, state_file)
