from setuptools import setup

setup(
    name="blave-quant-skill",
    version="0.1",
    py_modules=["hyperliquid_cli"],
    entry_points={
        "console_scripts": [
            "hyperliquid=hyperliquid_cli:main_cli",
        ],
    },
)
