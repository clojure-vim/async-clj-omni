class Error(Exception):
    """Base class for exceptions in this module."""
    pass

def gather_conn_info(vim):
    try:
        client = vim.eval("fireplace#client()")
    except Exception:
        raise Error

    if client:
        connection = client.get("connection", {})
        transport = connection.get("transport")

        if not transport:
            raise Error

    ns = ""
    try:
        ns = vim.eval("fireplace#ns()")
    except Exception:
        pass

    return [client, connection, transport, ns]
