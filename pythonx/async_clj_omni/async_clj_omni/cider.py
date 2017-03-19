import uuid
import threading
import logging

root = logging.getLogger('deoplete')

short_types = {
    "function": "f",
    "macro": "m",
    "var": "v",
    "special-form": "s",
    "class": "c",
    "keyword": "k",
    "local": "l",
    "namespace": "n",
    "field": "i",
    "method": "f",
    "static-field": "i",
    "static-method": "f",
    "resource": "r"
}


def candidate(val):
    arglists = val.get("arglists")
    type = val.get("type")
    return {
        "word": val.get("candidate"),
        "kind": short_types.get(type, type),
        "info": val.get("doc", ""),
        "menu": " ".join(arglists) if arglists else ""
    }


def cider_gather(nrepl, keyword, session, ns):
    # Should be unique for EVERY message
    msgid = uuid.uuid4().hex

    completion_event = threading.Event()
    response = None

    root.debug("cider gather been called {}".format(msgid))

    def completion_callback(cmsg, cwc, ckey):
        nonlocal response
        response = cmsg
        completion_event.set()

    nrepl.watch("{}-completion".format(msgid),
                {"id": msgid},
                completion_callback)

    root.debug("cider_gather watching msgid")

    # TODO: context for context aware completions
    nrepl.send({
        "id": msgid,
        "op": "complete",
        "session": session,
        "symbol": keyword,
        "extra-metadata": ["arglists", "doc"],
        "ns": ns
    })

    completion_event.wait(0.5)

    root.debug("finished waiting for completion to happen")
    root.debug("response truthy? {}".format(bool(response)))

    nrepl.unwatch("{}-completion".format(msgid))

    if response:
        return [candidate(x) for x in response.get("completions", [])]
    return []
