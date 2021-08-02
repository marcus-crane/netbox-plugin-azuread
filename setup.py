import os
from setuptools import find_packages, setup


current_dir = os.path.dirname(os.path.realpath(__file__))

with open(
    f"{current_dir}/netbox_plugin_azuread/VERSION", "r"
) as file:
    VERSION = file.read().strip()

with open(f"{current_dir}/README.md", "r") as file:
    LONG_DESCRIPTION = file.read()


setup(
    name='netbox-plugin-azuread',
    version=VERSION,
    description='Authenticate with Netbox via AzureAD',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/marcus-crane/netbox-plugin-azuread',
    author='Marcus Crane',
    license='MIT',
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
