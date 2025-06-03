import logging


class CorrelationIdFilter(logging.Filter):
    """
    Logging filter to add correlation_id from request.state to log records.
    """

    def filter(self, record):
        # Attempt to get the current request from context (this is tricky outside of request scope)
        # This approach might not work reliably for all loggers if they are not request-bound.
        # A more robust way is to pass 'extra' to logger calls within request handlers.
        # However, for middleware-set IDs, this is a common pattern.

        # This filter is more effective if logger calls use `extra` dict.
        # For now, we'll assume it's primarily for formatters that can access it.
        # The `_get_trace_id` in main.py already handles this for exception logs.
        # For general logs, it's better to pass `extra` in logger calls.

        # Let's try a simplified approach for the formatter to pick up.
        # The `jsonlogger.JsonFormatter` can be configured to include specific record attributes.
        # We need to ensure 'correlation_id' is on the record.

        # This filter might not be strictly necessary if the formatter is configured
        # to look for 'correlation_id' and it's added to 'extra' in logging calls.
        # For now, let's assume the formatter will be adapted.

        # A more direct way for the formatter:
        # If using `logging.basicConfig` or `logger.addHandler` with a formatter
        # that supports `format='%(asctime)s %(correlation_id)s ...'`,
        # then `correlation_id` needs to be in `record.__dict__`.

        # This filter is a placeholder; actual injection into record for all logs
        # might need contextvars or passing 'extra' to each log call.
        # The `_get_trace_id` in `main.py` for exceptions is more direct.

        # For the `python-json-logger` formatter, we can add fields to the record
        # if they are not already present.
        if not hasattr(record, "correlation_id"):
            record.correlation_id = None  # Default if not set

        # If we had access to the request object here (e.g. via contextvars)
        # try:
        #     from app.utils.request_context import get_request # Hypothetical
        #     request = get_request()
        #     if request and hasattr(request.state, 'correlation_id'):
        #         record.correlation_id = request.state.correlation_id
        # except Exception:
        #     pass # Keep it resilient

        return True


# For a more robust solution with python-json-logger,
# you typically pass 'extra' to your logging calls:
# logger.info("My message", extra={'correlation_id': request.state.correlation_id})
# Or, customize the add_fields in the formatter.
