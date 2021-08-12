# netbox-plugin-azuread

<strong>BEWARE:</strong> While this repo works and has been running in a production deployment for many months, I need to write some proper documentation. In the meantime, please feel free to file issues or ask questions.

`netbox-plugin-azuread` is a plugin for the [IPAM](https://docs.microsoft.com/en-us/windows-server/networking/technologies/ipam/ipam-top) tool [Netbox](https://github.com/netbox-community/netbox).

It uses Microsoft's [MSAL for Python](https://github.com/AzureAD/microsoft-authentication-library-for-python) library to add support for [Azure Active Directory](https://azure.microsoft.com/en-us/services/active-directory/) in the form of a [Netbox plugin](https://netbox.readthedocs.io/en/stable/plugins/).

---

### Table of Contents

- [Distribution](#distribution)
- [Installation](#installation)
- [Configuration](#configuration)

## Distribution

TODO

```python
pip install netbox_plugin_azuread
```

## Installation

It looks a little like this:

```shell
pip install netbox_plugin_azuread msal
```

As you can see, we're installing both `netbox-plugin-azuread` and `msal` which might seem odd at first glance.

As of writing, Netbox provides no method for pip installing the requirements of a plugin, but `netbox-plugin-azuread` is dependent on `msal` so we install both at runtime.

## Configuration

In order to use the plugin, you'll need to provide a few inputs for it to function.

Within the [PLUGINS_CONFIG](https://netbox.readthedocs.io/en/stable/configuration/optional-settings/#plugins_config) section of your configuration, you'll want to add a block like so:

``` shell
PLUGINS = [
  'netbox_plugin_azuread'
]
PLUGINS_CONFIG = {
  'netbox_plugin_azuread': {
    'CLIENT_ID': "<YOUR-CLIENT-ID-HERE>",
    'CLIENT_SECRET': "<YOUR-CLIENT-SECRET-HERE>",
    'AUTHORITY': "<YOUR-CLIENT-AUTHORITY-HERE>",
    'LOGIN_URL': '<LOGIN-URL>',  # Should be /plugins/azuread/login/ unless you remap it using eg; nginx
    'REPLY_URL': '<REPLY_URL>',  # Should be /plugins/azuread/complete/ unless you remap it using eg; nginx
    'SCOPES': ['https://graph.microsoft.com/.default'],
    'AD_GROUP_MAP': {
      'READ_ONLY': ['notallowed'],
      'STAFF': ['abc123', 'blahblah'],
      'SUPERUSER': ['blahadmin']
    }
  }
}
```

Assuming the variables above are correct, you can trigger the OAuth flow by visiting `https://<your-netbox-ip>/plugins/azuread/login/`
