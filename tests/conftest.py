"""Block network access before pytest imports test modules during collection."""

import pytest_socket

pytest_socket.disable_socket(allow_unix_socket=True)
