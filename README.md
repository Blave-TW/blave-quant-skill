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
# Clone the repository
git clone https://github.com/Blave-TW/blave-quant-skill.git
cd blave-quant-skill

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
# Mac/Linux
source venv/bin/activate
# Windows (PowerShell)
# venv\Scripts\Activate.ps1
# Windows (CMD)
# venv\Scripts\activate.bat

# Install the skill in editable mode
pip install -e .

# Install additional dependencies
pip install -r requirements.txt
```
