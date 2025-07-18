import threading

def defer(func, delay_seconds, *args, **kwargs):
    """
    Schedules a function to be executed after a specified delay.

    Args:
        func (callable): The function to be executed.
        delay_seconds (float or int): The delay in seconds before the function is executed.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        threading.Timer: The Timer object, which can be used to cancel the execution
                            before the delay expires (e.g., timer.cancel()).
    """
    timer = threading.Timer(delay_seconds, func, args=args, kwargs=kwargs)
    timer.start()
    return timer
