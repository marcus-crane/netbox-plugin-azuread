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
    project_urls={
        "Bug Tracker": "https://github.com/marcus-crane/netbox-plugin-azuread/issues",
    },
    author='Marcus Crane',
    license='MIT',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Plugins",
        "Framework :: Django :: 3.2",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration :: Authentication/Directory"
    ],
    install_requires=[],
    python_requires=">=3.6",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
