import logging

# set a logger for debug, log format is:
# %(asctime)s - %(name)s - %(levelname)s - %(message)s
_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
_log.addHandler(console_handler)

# DebugEnable: print the request path, body and response body for each request if set True
DebugEnable = False


def Debug(msg, *args):
    if DebugEnable:
        _log.debug(msg, *args)
