# Blave Quant Skill

Blave Quant Skill is a collection of skills that allows an agent to interact with crypto market data and trading platforms.

### Skills

- 📊 **blave** — Fetch market alpha data (Holder Concentration, Taker Intensity) directly from the Blave API
- 🤖 **hyperliquid** — Fetch account info and execute trades on Hyperliquid

---

## Installation

```bash
npx skills add https://github.com/Blave-TW/blave-quant-skill/blave
npx skills add https://github.com/Blave-TW/blave-quant-skill/hyperliquid
```

---

## Blave Skill Setup

The blave skill calls the Blave API directly. No CLI installation required.

Add the following to your `.env`:

```
blave_api_key=YOUR_API_KEY
blave_secret_key=YOUR_SECRET_KEY
```

---

## Hyperliquid Skill Setup

```bash
# 1. Clone the repository
git clone https://github.com/Blave-TW/blave-quant-skill.git
cd blave-quant-skill

# 2. Create a Python virtual environment
python3 -m venv venv

# 3. Activate the virtual environment
source venv/bin/activate   # Mac/Linux
# venv\Scripts\activate.bat  # Windows CMD
# venv\Scripts\Activate.ps1 # Windows PowerShell

# 4. Install dependencies
pip install -e .
pip install -r requirements.txt

# 5. Exit venv
deactivate

# 6. Set up CLI as a global command
chmod +x hyperliquid_cli.py
pwd # To get the path
sudo ln -s /full/path/to/hyperliquid_cli.py /usr/local/bin/hyperliquid

# 7. Test
hyperliquid check
```

Add the following to your `.env`:

```
arbitrum_address=YOUR_WALLET_ADDRESS
arbitrum_secret_key=YOUR_PRIVATE_KEY
```
