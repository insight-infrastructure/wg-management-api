# Wireguard Management API

The Wireguard Management API is a tool that enables automatic peer registration to a Wireguard server over a REST API.

## Prerequisites

The Wireguard Management API requires:

- A Linux OS (tested on Ubuntu)
- Python 3
- pip
- virtualenv (not required, but highly suggested)
- Wireguard

## Installation and use

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

5. Start server with sudo

```bash
cd /path/to/repo/app
sudo uvicorn main:app --host 0.0.0.0
```
