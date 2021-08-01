import os
from setuptools import find_packages, setup

with open(
    f"{os.path.dirname(os.path.realpath(__file__))}/netbox_plugin_azuread/VERSION", "r"
) as file:
    VERSION = file.read().strip()

setup(
    name='netbox-plugin-azuread',
    version=VERSION,
    description='Authenticate with Netbox via AzureAD',
    url='https://github.com/marcus-crane/netbox-plugin-azuread',
    author='Marcus Crane',
    license='MIT',
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
