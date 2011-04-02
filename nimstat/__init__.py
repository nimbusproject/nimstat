import logging

Version = "0.1"

def make_logger(log_level, dbname, logfile=None):

    if not logfile:
        return None

    if log_level == "debug":
        loglevel = logging.DEBUG
    elif log_level == "info":
        loglevel = logging.INFO
    elif log_level == "warn":
        loglevel = logging.WARN
    elif log_level == "error":
        loglevel = logging.ERROR

    if logfile == "-":
        handler = logging.StreamHandler()
    else:
        handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=100*1024*1024, backupCount=5)

    logger = logging.getLogger(dbname)
    logger.setLevel(loglevel)
    logger.addHandler(handler)

    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)

    return logger
