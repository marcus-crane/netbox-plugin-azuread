import logging

from django.contrib.auth import login as auth_login, get_user_model
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import User, Group
from django.conf import settings
import msal
from netbox.authentication import RemoteUserBackend
import requests

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG["netbox_plugin_azuread"]
LOGGER = logging.getLogger("netbox_plugin_azuread")


class AzureADRemoteUserBackend(RemoteUserBackend):

    def authenticate(self, request, remote_user):
        return super().authenticate(request, remote_user)

    def configure_user(self, request, user):
        return super().configure_user(request, user)

    def acquire_user_token(self, request, redirect_uri):
        cache = self._load_cache(request)
        client = self._create_msal_client(cache=cache)
        result = client.acquire_token_by_authorization_code(
            request.GET['code'],
            scopes=PLUGIN_SETTINGS['SCOPES'],
            redirect_uri=redirect_uri
        )
        self._save_cache(request, cache)
        return result

    def acquire_client_token(self):
        client = self._create_msal_client()
        result = client.acquire_token_for_client(
            scopes=PLUGIN_SETTINGS['SCOPES']
        )
        return result.get('access_token')

    def login(self, request, user):
        auth_login(request, user, backend='netbox_plugin_azuread.backends.AzureADRemoteUserBackend')

    def retrieve_user(self, auth_result):
        access_token = self.acquire_client_token()
        claims = auth_result.get('id_token_claims')
        try:
            user = get_user_model().objects.get(username=claims.get('preferred_username'))
        except Exception:
            user = self._create_user_from_claims(claims, access_token)
        self._configure_access_groups(user, access_token) # groups change over time so we check each login
        return user

    def _create_user_from_claims(self, claims, access_token):
        username = claims.get('preferred_username')
        profile = self._get_user_profile(username, access_token)
        password = BaseUserManager().make_random_password()
        user = User(
            username=username,
            password=password,
            email=profile.get('mail', ''),
            first_name=profile.get('givenName', ''),
            last_name=profile.get('surname', '')
        )
        user.save()
        return user

    def _retrieve_user_groups(self, user_id, access_token):
        groups_url = f'https://graph.microsoft.com/v1.0/users/{user_id}/memberOf?$select=displayName,id'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        r = requests.get(groups_url, headers=headers)
        return r.json().get('value', [])

    def _configure_access_groups(self, user, access_token):
        user_id = self._get_user_profile(user.username, access_token).get('id')
        azure_groups = self._retrieve_user_groups(user_id, access_token)
        user.is_staff = False
        user.is_superuser = False # Recheck user still has these permissions each time
        # TODO: Remove user from all groups if no groups found in Azure
        if azure_groups:
            azure_group_names = [entry.get('displayName') for entry in azure_groups]
            AD_GROUP_MAP = PLUGIN_SETTINGS.get('AD_GROUP_MAP', {})
            for group_name in azure_group_names:
                group, _ = Group.objects.get_or_create(
                    name=group_name
                )
                group.user_set.add(user)
                if group_name in AD_GROUP_MAP.get('READ_ONLY', []):
                    LOGGER.info(f"Delegated read only permission to f{user.email}")
                    reader_group, _ = Group.objects.get_or_create(name='READ_ONLY')
                    reader_group.user_set.add(user)
                if group_name in AD_GROUP_MAP.get('STAFF', []):
                    LOGGER.info(f"Delegated staff permission to f{user.email}")
                    user.is_staff = True
                if group_name in AD_GROUP_MAP.get('SUPERUSER', []):
                    LOGGER.info(f"Delegated superuser permission to f{user.email}")
                    user.is_superuser = True
                    user.is_staff = True
            for group in Group.objects.all():
                if group.name not in azure_group_names:  # ensure that deleted groups are cleaned up
                    LOGGER.info(f"Removed {user.email} from {group.name}")
                    group.user_set.remove(user)
        user.save() # it would be wasteful to save every time if there are say; 1000 admin groups configured
        return user

    def _get_user_profile(self, username, access_token):
        profile_url = f'https://graph.microsoft.com/v1.0/users/{username}'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        r = requests.get(profile_url, headers=headers)
        return r.json()

    def get_auth_url(self, redirect_url, state=None):
        client = self._create_msal_client()
        return client.get_authorization_request_url(
            scopes=PLUGIN_SETTINGS["SCOPES"],
            state=state,
            redirect_uri=redirect_url
        )

    def _load_cache(self, request):
        cache = msal.SerializableTokenCache()
        if request.session.get('token_cache', False):
            cache.deserialize(request.session['token_cache'])
        return cache

    def _save_cache(self, request, cache):
        if cache.has_state_changed:
            request.session['token_cache'] = cache.serialize()

    def _create_msal_client(self, cache=None):
        return msal.ConfidentialClientApplication(
            client_id=PLUGIN_SETTINGS["CLIENT_ID"],
            client_credential=PLUGIN_SETTINGS["CLIENT_SECRET"],
            authority=PLUGIN_SETTINGS["AUTHORITY"],
            token_cache=cache
        )
