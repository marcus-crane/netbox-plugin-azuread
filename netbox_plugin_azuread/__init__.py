import logging
import os

from extras.plugins import PluginConfig

with open(
    f"{os.path.dirname(os.path.realpath(__file__))}/VERSION", "r"
) as file:
    VERSION = file.read().strip()

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)

LOGGER = logging.getLogger("netbox_plugin_azuread")
LOGGER.info("Initialising Netbox AzureAD plugin")


class NetboxAzureADConfig(PluginConfig):
    name = 'netbox_plugin_azuread'
    verbose_name = 'AzureAD for Netbox'
    description = 'Hello world!'
    version = VERSION
    author = 'Marcus Crane'
    author_email = 'marcus@utf9k.net'
    base_url = 'azuread'
    required_settings = []
    default_settings = {}


config = NetboxAzureADConfig
