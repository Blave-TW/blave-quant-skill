from setuptools import setup

setup(
    name="blave",
    version="0.1",
    py_modules=["blave_cli"],
    entry_points={
        "console_scripts": [
            "blave=blave_cli:main_cli",
        ],
    },
)
