# Systemair

Integration to integrate with SystemAir VSR IAM module via ModBus

## Installation

### Using HACS

1. Open HACS and go to "Custom integrations". Enter the URL `https://github.com/AN3Orik/systemair`, choose type Integration and click Add. 
2. Restart Home Assistant
3. Go to settings and add new integration. You will find Systemair in the list of available integrations. 

### Manually

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `systemair`.
1. Download _all_ the files from the `custom_components/systemair/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Systemair"

## Configuration is done in the UI
