# netbox-plugin-azuread

[![Version](https://img.shields.io/badge/version-1.0.2-informational.svg)](https://pypi.org/project/netbox-plugin-azuread/)

A plugin for the [IPAM](https://docs.microsoft.com/en-us/windows-server/networking/technologies/ipam/ipam-top) tool [Netbox](github.com/netbox-community/netbox) to support OAuth2 authentication via [Azure Active Directory](https://azure.microsoft.com/en-us/services/active-directory/).

`netbox-plugin-azuread` is effectively a light wrapper around Microsoft's own [`msal`](https://github.com/AzureAD/microsoft-authentication-library-for-python) library with the added ability to map AzureAD groups to Django permissions.

## Installation

Before installing any plugins, it's worth familiarising yourself with the [Netbox documentation](https://netbox.readthedocs.io/en/stable/).

Regardless of environment, it's always a good idea to pin your dependencies. I haven't done it explicitly in this README but I recommend doing it for your own deployments eg; `pip install msal==1.2.3 netbox_plugin_azuread==1.0.0`.

### Bare metal

If you're using a non-containerised deployment of Netbox, you'll want to first activate the virtual environment as [referenced in the Netbox setup process](https://netbox.readthedocs.io/en/stable/installation/3-netbox/#run-the-upgrade-script).

```shell
cd /opt/netbox
source venv/bin/activate
```

Once activated, you'll be able to use pip install `netbox-plugin-azuread` by way of its hosted [PyPI](https://pypi.org/) distribution. We'll also be installing `msal` as a dependency. Once done, you'll need to restart Netbox to see your changes.

```shell
pip install msal netbox_plugin_azuread
systemctl restart netbox
```

If you prefer to install this package manually, both a `.tar.gz` and `.whl` distribution are available under under the [releases](https://github.com/marcus-crane/netbox-plugin-azuread/releases) section of this Github repository.

Once installed, don't forget to add these changes to your `requirements.txt` or better yet, store them in their own distinct requirements file from the Netbox base requirements.

### Containerisation

If you're looking to use this plugin in conjunction with your own dockerised version of Netbox, or one of the available [netbox-docker](https://github.com/netbox-community/netbox-docker) images, it's a little bit more involved.

At work, we run this plugin within a build of Netbox deployed via Kubernetes but the steps are the same for any Docker deployment.

Here's the simplest possible Dockerfile you could write:

```dockerfile
FROM netboxcommunity/netbox:v2.11.12

RUN /opt/netbox/venv/bin/pip install netbox_plugin_azuread msal
```

As above, `msal` is a dependency of this plugin so we need to install it as well. Despite this container being extremely small, the rest of the `netbox-docker` build scripts will implicitly execute as we haven't overridden the entrypoint or any other commands.

## Usage

In order to use this plugin, you'll need to add it to the [PLUGINS_CONFIG](https://netbox.readthedocs.io/en/stable/configuration/optional-settings/#plugins_config) portion of your [Netbox configuration](https://netbox.readthedocs.io/en/stable/configuration/).

Here's a sample of all of the possible settings you can configure:

```shell
PLUGINS = [
  'netbox_plugin_azuread'  # Note that we use underscores for the plugin internally but the name has dashes
]
PLUGINS_CONFIG = {
  'netbox_plugin_azuread': {
    'CLIENT_ID': '<YOUR-CLIENT-ID-HERE>',  # Available for viewing in the Azure Portal under Azure Active Directory
    'CLIENT_SECRET': '<YOUR-CLIENT-SECRET-HERE>',
    'AUTHORITY': '<YOUR-CLIENT-AUTHORITY-HERE>',
    'LOGIN_URL': '<LOGIN-URL>',  # Should be /plugins/azuread/login/ unless you remap it using eg; nginx
    'REPLY_URL': '<REPLY_URL>',  # Should be /plugins/azuread/complete/ unless you remap it using eg; nginx
    'SCOPES': ['https://graph.microsoft.com/.default'],
    'AD_GROUP_MAP': {
      'STAFF': ['abc123', 'blahblah'],
      'SUPERUSER': ['blahadmin']  # Set one or more Azure AD groups and users with this group will receive the superuser or staff flag
    }
  }
}
REMOTE_AUTH_AUTO_CREATE_USER = True
REMOTE_AUTH_BACKEND = 'netbox_plugin_azuread.backends.AzureADRemoteUserBackend'
REMOTE_AUTH_ENABLED = True
```

Realistically, they're all required except for the `AD_GROUP_MAP` which is totally optional.

## Redirecting the login page

Out of the box, you'll notice that `http://netbox.blah/login` still shows the usual login page. Due to the nature of this being a plugin and not a core part of Netbox, it lives under `/plugins/azuread` and can't overwrite Netbox URLs.

One possible solution is to request that Netbox allows updating which route is considered the login page via configuration but in lieu of that, we can work around this. To be clear, you can always just ask users to manually visit `/plugins/azuread/login/` each time but that's a pain to remember.

In my own case, I use an [nginx](https://www.nginx.com/) instance to write `/login/` to point to `/plugins/azuread/login/` instead.

Here's an example of how your configuration could look:

```nginx
worker_processes 1;
pid /tmp/nginx.pid;

error_log /dev/stderr info;

events {
    worker_connections 1024;
}

http {
    include              /etc/nginx/mime.types;
    default_type         application/octet-stream;
    server_tokens        off;
    client_max_body_size 25m;
    access_log           /dev/stdout;

    server {
        listen      8000;
        server_name _;
        access_log  off;

        location / {
            proxy_pass http://localhost:8080/;
        }

        location /login/ {
            proxy_pass http://localhost:8080/plugins/azuread/login/;
        }

        location /complete/ {
            proxy_pass http://localhost:8080/plugins/azuread/complete/;
        }
    }
}
```

This may seem a bit overkill just for one plugin but originally, nginx was required regardless to serve static assets. In our case, `netbox-docker` has since updated to use nginx unit under the hood so this is no longer relevant to my knowledge.

## Questions

While this project is open sourced with no guarantees, feel free to open an issue and I'll attempt to provide support as I can.

## Screenshots

[![A slightly modified version of the Netbox login screen that shows two buttons. One is labelled Azure AD while the other is labelled Password](/docs/netbox-login.png)](/docs/netbox-login.png)

[![The normal Netbox login screen showing a logged in user, who has been created via OAuth with Azure AD](/docs/netbox-profile.png)](/docs/netbox-profile.png)
