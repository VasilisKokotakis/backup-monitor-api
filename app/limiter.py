from slowapi import Limiter
from slowapi.util import get_remote_address


# Single shared instance: registered on app.state in main.py and used by the
# @limiter.limit decorators in the routers. Constructing a Limiter per module
# would give each its own counter storage.
limiter = Limiter(key_func=get_remote_address)
