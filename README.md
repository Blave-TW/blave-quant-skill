# Blave Quant Skill

Blave Quant Skill is a tool that allows an agent to learn and perform the following skills, designed for the Blave platform:

### Skills the Agent Can Learn

- 📊 **Data Fetching**: Retrieve market data and historical trading information from Blave
- 📈 **Data Analysis & Backtesting**: Analyze strategy performance and simulate trades
- 🤖 **Automated Trading**: Execute buy/sell orders based on strategy instructions
- 📌 **Strategy Management**: Set up, modify, and execute different trading strategies
- 📝 **Report Generation**: Generate backtest and trading reports for strategy evaluation

---

## Installation

1. Skills:

```bash
npx skills add https://github.com/Blave-TW/blave-quant-skill --skill blave-quant
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

# 6. Set up the blave CLI as a global command
chmod +x blave_cli.py
pwd # To get the path
sudo ln -s /full/path/to/blave_cli.py /usr/local/bin/blave # Replace /full/path/to with the actual path

# 7. Test
blave check
```

## Notes

The .env file must be in the project root and contain your blave_api_key and blave_secret_key.

Ensure the virtual environment is activated and .env is loaded before running any CLI or Python commands.
