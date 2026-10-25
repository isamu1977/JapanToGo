"""Anti-SSRF validation for externally supplied URLs.

Every URL that reaches the server from a client is validated here before any
network connection is opened:

1. the scheme must be exactly ``https``;
2. the hostname must resolve to at least one IP address;
3. every resolved address must be a *public* Internet address.

Loopback, RFC 1918 private ranges, RFC 3927 link-local (including the
``169.254.169.254`` cloud metadata endpoint), multicast, reserved and
unspecified addresses are rejected.
"""

from __future__ import annotations

import ipaddress
import logging
import socket
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from app.core.errors import ValidationError

logger = logging.getLogger("app.security.ssrf")

ALLOWED_SCHEMES = frozenset({"https"})


class SSRFError(ValidationError):
    """Raised when a URL points at a forbidden destination.

    The request is refused with HTTP 400 Bad Request, matching the design
    decision for the anti-SSRF validator.
    """

    status_code = 400
    code = "ssrf_blocked"


@dataclass(frozen=True)
class ValidatedURL:
    """A URL that passed every SSRF check."""

    url: str
    scheme: str
    hostname: str
    port: int
    resolved_ips: tuple[str, ...]


def _is_blocked_address(ip: ipaddress._BaseAddress) -> bool:
    """Return True when the address must not be contacted."""
    return (
        ip.is_loopback
        or ip.is_private
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def resolve_hostname(hostname: str, port: int = 443) -> list[ipaddress._BaseAddress]:
    """Resolve a hostname into a list of IP addresses."""
    try:
        infos = socket.getaddrinfo(hostname, port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise SSRFError(
            f"The hostname '{hostname}' could not be resolved.",
            details={"hostname": hostname},
        ) from exc

    addresses: list[ipaddress._BaseAddress] = []
    for info in infos:
        sockaddr = info[4]
        raw_ip = sockaddr[0]
        try:
            addresses.append(ipaddress.ip_address(raw_ip))
        except ValueError:  # pragma: no cover - getaddrinfo always returns IPs
            continue

    if not addresses:
        raise SSRFError(
            f"The hostname '{hostname}' did not resolve to any IP address.",
            details={"hostname": hostname},
        )
    return addresses


def validate_url(url: str) -> ValidatedURL:
    """Validate an external URL against the SSRF policy.

    Raises ``SSRFError`` (HTTP 400) when the URL is malformed, uses a scheme
    other than ``https``, or resolves to a forbidden address.
    """
    if not url or not isinstance(url, str):
        raise SSRFError("A URL is required.")

    candidate = url.strip()
    if len(candidate) > 2048:
        raise SSRFError("The URL is too long.")

    try:
        parts = urlsplit(candidate)
    except ValueError as exc:
        raise SSRFError("The URL is malformed.") from exc

    scheme = (parts.scheme or "").lower()
    if scheme not in ALLOWED_SCHEMES:
        raise SSRFError(
            "Only HTTPS URLs are accepted.",
            details={"scheme": scheme or None, "allowed": sorted(ALLOWED_SCHEMES)},
        )

    hostname = parts.hostname
    if not hostname:
        raise SSRFError("The URL does not contain a hostname.")

    try:
        port = parts.port or 443
    except ValueError as exc:
        raise SSRFError("The URL contains an invalid port.") from exc

    # A literal IP address bypasses DNS, so it is checked directly.
    try:
        literal = ipaddress.ip_address(hostname)
    except ValueError:
        literal = None

    if literal is not None:
        addresses = [literal]
    else:
        addresses = resolve_hostname(hostname, port)

    blocked = [str(ip) for ip in addresses if _is_blocked_address(ip)]
    if blocked:
        logger.warning(
            "SSRF prevention: blocked request to %s (resolved to %s)",
            candidate,
            ", ".join(blocked),
        )
        raise SSRFError(
            "The URL points to a private or restricted network address.",
            details={"hostname": hostname, "blocked_addresses": blocked},
        )

    # Normalise the URL so the caller always uses a canonical form.
    normalized = urlunsplit(
        (scheme, parts.netloc.lower(), parts.path, parts.query, "")
    )

    return ValidatedURL(
        url=normalized,
        scheme=scheme,
        hostname=hostname.lower(),
        port=port,
        resolved_ips=tuple(str(ip) for ip in addresses),
    )


def is_safe_url(url: str) -> bool:
    """Return True when the URL passes the SSRF policy."""
    try:
        validate_url(url)
    except SSRFError:
        return False
    return True
