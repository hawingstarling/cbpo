from typing import Union
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, SlidingToken
from .services import LastModificationServices


def custom_token_handler(user, client=None, user_client=None,
                         token_class: Union[AccessToken, RefreshToken, SlidingToken] = RefreshToken, **kwargs):
    token = token_class.for_user(user)
    kwargs.update(
        dict(
            user_id=str(user.pk),
            email=user.email,
            username=user.username,
            fname=user.first_name,
            lname=user.last_name,
        )
    )
    # update last modified settings
    if client and user_client:
        res1 = LastModificationServices.client_modules(client)
        last_modified_settings = None if not len(res1) else str(max(res1))
        token["client_id"] = str(client.pk)
        token["last_modified_settings"] = last_modified_settings
        kwargs.update(
            dict(
                client_id=str(client.pk),
                last_modified_settings=last_modified_settings
            )
        )
    for k, v in kwargs.items():
        token[k] = v
    return token
