from typing import Annotated

from fastapi import Header, HTTPException


def current_user(x_user_id: Annotated[str | None, Header()] = None) -> str:
    """DEV ONLY: trusts an X-User-Id header.

    Replace with real authentication (e.g. OIDC/JWT verification) before any shared deployment.
    """
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")
    return x_user_id
