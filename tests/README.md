# Testing Environment Setup

Create a virtual environment and install all necessary dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.test.txt
```

To run tests use:
`pytest tests/<module_name>.py -s -vv`

### Notes:

- Makes use of [pytest-homeassistant-custom-component](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component) by [MatthewFlamm](https://github.com/MatthewFlamm)
