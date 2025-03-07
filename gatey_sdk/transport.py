"""
    Transport classes, that handles sending events from Gatey.
"""
import json
from typing import Callable, Any, Union, Optional, Dict
from gatey_sdk.exceptions import (
    GateyTransportError,
    GateyTransportImproperlyConfiguredError,
)
from gatey_sdk.api import Api
from gatey_sdk.auth import Auth


class BaseTransport:
    """
    Base transport class. Cannot be used as transport.
    Abstract class for implementing transport classes.
    """

    def __init__(self):
        pass

    def send_event(self, event_dict: Dict):
        """
        Handles transport event callback (handle event sending).
        Should be inherited from BaseTransport and implemented in transports.
        """
        raise NotImplementedError()


class HttpTransport(BaseTransport):
    """
    HTTP Transport. Sends event to the Gatey Server when event sends.
    """

    # Allowed aggreation / composition..
    _api_provider: Api = None
    _auth_provider: Optional[Auth] = None

    def __init__(self, api: Optional[Api] = None, auth: Optional[Auth] = None):
        """
        :param api: Api provider.
        :param auth: Authentication provider.
        """

        BaseTransport.__init__(self)
        self._auth_provider = auth if auth else Auth()
        self._api_provider = api if api else Api(self._auth_provider)
        self._check_improperly_configured()

    def send_event(self, event_dict: Dict):
        api_params = self._api_params_from_event_dict(event_dict=event_dict)
        api_response = self._api_provider.method(
            "event.capture", send_project_auth=True, **api_params
        )
        return api_response

    def _api_params_from_event_dict(self, event_dict: Dict):
        api_params = {
            "level": event_dict["level"],
        }

        # Event data.
        if "exception" in event_dict:
            api_params["exception"] = json.dumps(event_dict["exception"])
        if "message" in event_dict:
            api_params["message"] = event_dict["message"]

        # System data.
        if "platform" in event_dict:
            api_params["platform"] = json.dumps(event_dict["platform"])
        if "runtime" in event_dict:
            api_params["runtime"] = json.dumps(event_dict["runtime"])
        if "sdk" in event_dict:
            api_params["sdk"] = json.dumps(event_dict["sdk"])

        return api_params

    def _check_improperly_configured(self):
        """
        Raises error if auth provider improperly configured for sending event.
        """
        if self._auth_provider.project_id is None:
            raise GateyTransportImproperlyConfiguredError(
                "HttpTransport improperly configured! No project id found in auth provider!"
            )
        if (
            self._auth_provider.server_secret is None
            and self._auth_provider.client_secret is None
        ):
            raise GateyTransportImproperlyConfiguredError(
                "HttpTransport improperly configured! No client / server secret found in auth provider!"
            )


class FuncTransport(BaseTransport):
    """
    Function transport. Calls your function when event sends.
    """

    def __init__(self, function: Callable):
        """
        :param function: Function to call when event sends.
        """
        BaseTransport.__init__(self)
        self._function = function

    def send_event(self, event_dict: Dict) -> None:
        """
        Handles transport event callback (handle event sending).
        Function transport just takes event and passed it raw to function call.
        """
        try:
            self._function(event_dict)
        except Exception as transport_exception:
            raise GateyTransportError(
                f"Unable to handle event send with Function transport (FuncTransport). Raised exception: {transport_exception}"
            )


def build_transport_instance(
    transport_argument: Any = None,
    api: Optional[Api] = None,
    auth: Optional[Auth] = None,
) -> Union[BaseTransport, None]:
    """
    Builds transport instance by transport argument.
    """
    transport_class = None

    if transport_argument is None:
        # If nothing is passed, should be default http transport type.
        return HttpTransport(api=api, auth=auth)

    if isinstance(transport_argument, type) and issubclass(
        transport_argument, BaseTransport
    ):
        # Passed subclass of BaseTransport as transport.
        # Should be instantiated as cls.
        transport_class = transport_argument
        return transport_class(api=api, auth=auth)

    if callable(transport_argument):
        # Passed callable (function) as transport.
        # Should be Function transport, as it handles raw function call.
        return FuncTransport(function=transport_argument)

    # Unable to instantiate transport instance.
    raise GateyTransportImproperlyConfiguredError(
        "Failed to build transport instance. Please pass valid transport argument!"
    )
