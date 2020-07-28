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

## Usage

1. Ensure Wireguard is configured and running with the wg0 interface

2. Export the server address (i.e. 192.168.123.1/24) as ```WG_SERVER_ADDRESS``` and the server's public key as ```WG_SERVER_PUB_KEY```

5. Start server with sudo

```bash
cd /path/to/repo/app
sudo -E uvicorn main:app --host 0.0.0.0
```

Note: the server will persist the state in two files in the /app folder.
Simply stop the server and then delete these files to reinitialize the state on next launch.
