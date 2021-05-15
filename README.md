# Redfin

This is a _Custom Integration_ for [Home Assistant](https://www.home-assistant.io/). It uses the unofficial [Redfin](https://www.redfin.com) API to get property value estimates.

![GitHub release](https://img.shields.io/badge/release-v1.1.1-blue)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

There is currently support for the Sensor device type within Home Assistant.

## Installation

### HACS installation

This Integration is part of the default HACS store, so go to the HACS page and search for _Redfin_.

### Manual Installation

To manually add Redfin to your installation, create this folder structure in your /config directory:

`custom_components/redfin`.

Then drop the following files into that folder:

```yaml
translations/en.json
__init__.py
config_flow.py
const.py
hacs.json
sensor.py
manifest.json
```

## Configuration

You will need the Redfin property ID for each property you’d like to track. This information is available from the URL of a property you are interested in. If you’re the owner of this property, it’s recommended to claim the listing and update the property information to help the information be as accurate as possible.

For example, given this Redfin URL: https://www.redfin.com/DC/Washington/1745-Q-St-NW-20009/unit-3/home/9860590 the property ID is 9860590.

To enable this sensor, add new Redfin integration component in the Home Assistant UI and follow the prompts to add your properties.

The sensor provides the following attributes:

- amount
- amount_currency
- amount_formatted
- address
- full_address
- redfin_url
- street_view
