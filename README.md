# Blave Quant Skill

Blave Quant Skill is a tool that allows an agent to learn and perform the following skills, designed for the Blave platform:

### Skills the Agent Can Learn

- 📊 **Data Fetching**: Retrieve market alpha data and news from Blave
- 🤖 **Automated Trading**: Execute buy/sell orders on Hyperliquid based on strategy instructions
- 📌 **Strategy Management**: Set up, modify, and execute different trading strategies

---

## Installation

1. Skills:

```bash
npx skills add https://github.com/Blave-TW/blave-quant-skill --skill blave
npx skills add https://github.com/Blave-TW/blave-quant-skill --skill hyperliquid
```

2. Script:

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

# 4. Install the skill and dependencies
pip install -e .
pip install -r requirements.txt

# 5. Exit venv
deactivate

# 6. Set up CLI as global commands
chmod +x blave_cli.py hyperliquid_cli.py
pwd # To get the path
sudo ln -s /full/path/to/blave_cli.py /usr/local/bin/blave
sudo ln -s /full/path/to/hyperliquid_cli.py /usr/local/bin/hyperliquid

# 7. Test
blave check
hyperliquid check
```

## Notes

The `.env` file must be in the project root and contain:
- `blave_api_key`, `blave_secret_key` — required for the blave skill
- `arbitrum_address`, `arbitrum_secret_key` — required for the hyperliquid skill
