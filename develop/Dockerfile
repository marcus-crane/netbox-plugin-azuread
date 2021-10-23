ARG NETBOX_VERSION=3.0.0

FROM netboxcommunity/netbox:v${NETBOX_VERSION}

RUN /opt/netbox/venv/bin/pip install -U pip && /opt/netbox/venv/bin/pip install msal

COPY . /opt/netbox/netbox_plugin_azuread/

RUN /opt/netbox/venv/bin/python /opt/netbox/netbox_plugin_azuread/setup.py develop
