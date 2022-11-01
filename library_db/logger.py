import sys
import logging
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from werkzeug.serving import WSGIRequestHandler, _log


class RequestHandler(WSGIRequestHandler):
    """Custom RequestHandler for formatting log output"""

    def log(self, type, message, *args):
        _log(
            type,
            " %s\n" % (message % args),
        )

    def log_request(self, code="-", size="-"):
        remote_addr = ":".join([str(i) for i in self.client_address])
        self.log(
            "info",
            'Request from %s - "%s" %s %s',
            remote_addr,
            self.requestline,
            code,
            size,
        )


class RequestFilter(logging.Filter):
    """Filter Request Messages"""

    def filter(self, record):
        self.title = "RequestFilter"
        return not "Request" in record.msg

    def __eq__(self, other):
        return "RequestFilter" in str(other)


class AdminLogReqFilter(logging.Filter):
    """Filter Request Messages containing '/api/admin/log'
    since this is a route which is periodically called.
    """

    def filter(self, record):
        return not "/api/admin/log" in record.msg


def get_handlers():
    """Get Handlers for Logger

    Returns:
        tuple: Tuple of Handlers:
                - timed_file_handler:
                    Outputs to /logs/info
                    loglevel: INFO
                - timed_file_handler_error:
                    Outputs to /logs/error
                    loglevel: ERROR
                - stream_handler
                    Outputs to stdout
                    loglevel: DEBUG
    """
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    error_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s:  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    log_path = Path(__file__).parent / "logs"
    log_debug_path = log_path / "info" / "flask_log"
    log_error_path = log_path / "error" / "flask_log"

    log_path.parent.mkdir(exist_ok=True)
    log_debug_path.parent.mkdir(exist_ok=True, parents=True)
    log_error_path.parent.mkdir(exist_ok=True, parents=True)

    timed_file_handler = TimedRotatingFileHandler(
        str(log_debug_path), when="h", backupCount=7
    )
    timed_file_handler_error = TimedRotatingFileHandler(str(log_error_path), when="d")
    stream_handler = logging.StreamHandler(sys.stdout)

    timed_file_handler.setFormatter(formatter)
    timed_file_handler_error.setFormatter(error_formatter)
    stream_handler.setFormatter(formatter)

    timed_file_handler.addFilter(AdminLogReqFilter())
    timed_file_handler.addFilter(RequestFilter())

    timed_file_handler.setLevel(logging.INFO)
    stream_handler.setLevel(logging.DEBUG)
    timed_file_handler_error.setLevel(logging.ERROR)

    return timed_file_handler, timed_file_handler_error, stream_handler


def get_time_file_handler():
    return logging.getLoggerClass().root.handlers[0]


def get_time_file_error_handler():

    return logging.getLoggerClass().root.handlers[1]


def tfh_has_request_filter():
    """Checks if timed_file_handler has a RequestFilter

    Returns:
        bool: True if containing RequestFilter
    """
    if RequestFilter in get_time_file_handler().filters:
        return True

    return False


def get_info_logfile():
    """Get Logfile of timed_file_handler located in logs/info

    Returns:
         str: log filepath
    """
    return get_time_file_handler().baseFilename


def get_error_logfile():
    """Get Logfile of timed_file_handler_error located in logs/error

    Returns:
         str: log filepath
    """
    return get_time_file_error_handler().baseFilename
