import functools
import logging
from datetime import datetime


logger = logging.getLogger("valutatrade")


def log_action(action_name=None, verbose=False):

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            timestamp = datetime.now().isoformat()
            username = "anonymous"
            currency_code = ""
            amount = 0
            result = "OK"

            try:

                if args and hasattr(args[0], 'current_user') and args[0].current_user:
                    username = args[0].current_user.username

                currency_code = kwargs.get('currency', '')
                amount = kwargs.get('amount', 0)

                result_data = func(*args, **kwargs)

                log_msg = (f"{timestamp} {action_name or func.__name__.upper()} "
                           f"user='{username}' "
                           f"currency='{currency_code}' "
                           f"amount={amount} "
                           f"result={result}")

                logger.info(log_msg)

                if verbose:
                    logger.debug(
                        f"Verbose: {func.__name__} called with args={args}, kwargs={kwargs}")

                return result_data

            except Exception as e:

                result = "ERROR"
                error_type = type(e).__name__

                log_msg = (f"{datetime.now().isoformat()} "
                           f"{action_name or func.__name__.upper()} "
                           f"user='{username}' "
                           f"currency='{currency_code}' "
                           f"amount={amount} "
                           f"result={result} "
                           f"error_type={error_type} "
                           f"error_message={str(e)}")

                logger.error(log_msg)
                raise

        return wrapper
    return decorator
