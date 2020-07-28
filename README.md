# Wireguard Management API

The Wireguard Management API is a tool that enables automatic peer registration to a Wireguard server over a REST API.

## Prerequisites

The Wireguard Management API requires:

- A Linux OS (tested on Ubuntu)
- Python 3
- pip
- virtualenv (not required, but highly suggested)
- Wireguard

## Installation

1. Clone the repo
```bash
git clone git@github.com:insight-infrastructure/wg-management-api.git
```

2. Create virtual environment
```bash
mkdir /path/to/your/environment
python3 -m venv /path/to/your/environment
```

3. Activate environment
```bash
source /path/to/your/environment/bin/activate
```

4. Install requirements

```bash
pip install -r requirements.txt
```

## Server Usage

1. Ensure Wireguard is configured and running with the wg0 interface

2. Export the server address (i.e. 192.168.123.1/24) as ```WG_SERVER_ADDRESS``` and the server's public key as ```WG_SERVER_PUB_KEY```

5. Start server with sudo

```bash
cd /path/to/repo/app
sudo -E uvicorn main:app --host 0.0.0.0
```

Note: the server will persist the state in two files in the /app folder.
Simply stop the server and then delete these files to reinitialize the state on next launch.

## API Usage

The registration workflow requires that you first register a peer, and then confirm the peer was added to fully activate it.

All queries take the peer's public key as the only parameter.

In the following examples, we will assume a base address of ```http://wireguard.local:8000/```

### Registration

Send a POST query to:

```/register?peer_pub_key=<peer's public key>```

Upon a 200 SUCCESS, a JSON object will be returned containing your assigned Wireguard IP, the server's public key, and the server's Wireguard IP for your configuration file.
Update your local configuration file, start Wireguard, and confirm that you have a connection to the server.
Once this is done, proceed to the Confirmation step.

### Confirmation

Send a POST query to:

```/confirm?peer_pub_key=<peer's public key>```

Upon a 200 SUCCESS, the server's state will be updated to indicate that you have an active connection and your information will be persisted in the configuration.
When you are ready to remove the peer from the server's peer list, proceed to the Deregistration step.

### Deregistration

Send a POST query to:

```/deregister?peer_pub_key=<peer's public key>```

Upon a 200 SUCCESS, the server's state and configuration will be updated to remove your peer from the peer list.
You will be unable to reconnect with your existing peer configuration and will need to re-register.
