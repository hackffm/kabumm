# kabumm python game master

This folder contains the python code for the game master on a raspberry pi.

## Installation on raspbian

**todo**: install overlay for port expander
**todo**: enable I2C

    python3 -m venv env
    source env/bin/activate
    python -m pip install --editable git+https://github.com/hackffm/kabumm.git@master#subdirectory=python
