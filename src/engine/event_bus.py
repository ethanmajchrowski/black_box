from logger import logger
import core.configuration as c

class _EventBus:
    def __init__(self) -> None:
        self._listeners: dict[str, list] = {}

    def emit(self, event: str, *args, **kwargs):
        """Calls all functions associated with an event, passing in args & kwargs.

        Args:
            event (str): Event to emit
        Any arguments after event are passed as args and kwargs.
        """
        if c.PRINT_EVENT_BUS:
            logger.info(f"[EventBus] Emitting {event} with args: {args}, kwargs: {kwargs}")
        
        if event in self._listeners:
            for func in self._listeners[event]:
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    logger.fatal(f"[_EventBus] Error in '{event}' listener {func}: {e}")

    def connect(self, event: str, function):
        """Register function in event bus.

        Args:
            event (str): Event to connect function to
            function (_type_): Function to call when event is emitted
        """
        if event not in self._listeners:
            self._listeners[event] = []
        if function not in self._listeners[event]:
            self._listeners[event].append(function)

    def disconnect(self, event: str, function):
        """Disconnect function from event. Does nothing if the event or function are not registered."""
        if event in self._listeners:
            self._listeners[event].remove(function)
            if not self._listeners[event]:
                del self._listeners[event]
    
    def once(self, event: str, function):
        """Register a function to be called on the event, then disconnected after that."""
        # create a function that calls the function, then disconnects it from the manager
        def wrapper(*args, **kwargs):
            function(*args, **kwargs)
            self.disconnect(event, function)
        self.connect(event, wrapper)