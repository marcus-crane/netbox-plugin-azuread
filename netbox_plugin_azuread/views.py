import logging
import os
import uuid

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render

from .backends import AzureADRemoteUserBackend

LOGGER = logging.getLogger("netbox_plugin_azuread")
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)
PLUGIN_SETTINGS = settings.PLUGINS_CONFIG["netbox_plugin_azuread"]

ERROR_MAP = {
    'ACCOUNT_CREATION_FAILED': 'Something went wrong trying to log you in.',
    'ACCOUNT_LOGIN_FAILED': 'Something went wrong trying to create a user account.',
    'ALREADY_AUTHED': 'It appears that you have already logged in.',
    'MISSING_COMPLETE_URL': 'Redirect URL has not been configured.',
    'MISSING_AUTH_CODE': 'No authorization code could be found.',
    'USER_TOKEN_FAILURE': 'Failed to acquire a user token.'
}

NETBOX_VERSION = settings.VERSION

LOGIN_TEMPLATE = 'azure/login.html'
if NETBOX_VERSION.startswith('2.'):
    LOGIN_TEMPLATE = 'azure/login_2.x.html'


def login(request):
    context = {
        'auth_url': '#',
        'redirect_url': '#'
    }

    request.session['state'] = str(uuid.uuid4())
    request.session['next_url'] = request.GET.get('next', '/')

    try:
        redirect_url = request.build_absolute_uri(PLUGIN_SETTINGS['REPLY_URL'])
    except KeyError:
        messages.warning(request, ERROR_MAP['MISSING_COMPLETE_URL'])
        return render(
            request,
            LOGIN_TEMPLATE,
            context=context
        )

    auth_url = AzureADRemoteUserBackend().get_auth_url(redirect_url=redirect_url, state=request.session['state'])
    context['auth_url'] = auth_url

    return render(
        request,
        LOGIN_TEMPLATE,
        context
    )


def authorize(request):

    LOGGER.debug("Received a call to authorize")

    if request.user.is_authenticated:
        messages.success(request, ERROR_MAP['ALREADY_AUTHED'])
        LOGGER.debug("User is already authenticated. Redirecting to login URL.")
        return redirect(PLUGIN_SETTINGS['LOGIN_URL'])

    auth_backend = AzureADRemoteUserBackend()

    if not request.GET.get('code', False):
        messages.warning(request, ERROR_MAP['MISSING_AUTH_CODE'])
        LOGGER.error("Received a request missing an authorisation code")
        return redirect(PLUGIN_SETTINGS['LOGIN_URL']) # TODO: Should use view name but having issues

    try:
        redirect_url = request.build_absolute_uri(PLUGIN_SETTINGS['REPLY_URL'])
    except KeyError as ex:
        messages.warning(request, ERROR_MAP['MISSING_COMPLETE_URL'])
        LOGGER.debug(f"Failed to build a reply URL: {ex}")
        return redirect(PLUGIN_SETTINGS['LOGIN_URL'])

    auth_result = auth_backend.acquire_user_token(request, redirect_uri=redirect_url)
    if not auth_result:
        messages.error(request, ERROR_MAP['USER_TOKEN_FAILURE'])
        LOGGER.debug("Failed to acquire a token for the user")
        return redirect(PLUGIN_SETTINGS['LOGIN_URL'])

    user = auth_backend.retrieve_user(auth_result)
    if not user:
        messages.error(request, ERROR_MAP['ACCOUNT_CREATION_FAILED'])
        LOGGER.debug("Failed to retrieve the user's details")
        return redirect(PLUGIN_SETTINGS['LOGIN_URL'])

    try:
        LOGGER.debug("Attempting to log the user in")
        auth_backend.login(request, user)
    except Exception as ex:
        messages.error(request, ERROR_MAP['ACCOUNT_LOGIN_FAILED'])
        LOGGER.debug(f"Failed to log the user in: {ex}")
        return redirect(PLUGIN_SETTINGS['LOGIN_URL'])

    next_url = request.session.get('next_url', '/')
    LOGGER.debug(f"Redirecting to {next_url}")
    return redirect(next_url)
