"""Thin HashiCorp Vault client used for optional secret injection.

Reads a KV v2 secret and returns its data dict. Kept dependency-light so the
app still runs when Vault is not configured.
"""
from typing import Dict


def read_secret(addr: str, token: str, path: str) -> Dict[str, str]:
    import hvac

    client = hvac.Client(url=addr, token=token)
    if not client.is_authenticated():
        raise RuntimeError("Vault authentication failed")

    # Path is expected like "secret/data/grocery" (KV v2). Normalize for the
    # hvac KV v2 helper which wants mount_point + path separately.
    parts = path.split("/")
    mount = parts[0]
    # Drop the "data" segment KV v2 inserts in the raw API path.
    sub = [p for p in parts[1:] if p != "data"]
    secret_path = "/".join(sub)

    resp = client.secrets.kv.v2.read_secret_version(
        path=secret_path, mount_point=mount
    )
    return resp["data"]["data"]
