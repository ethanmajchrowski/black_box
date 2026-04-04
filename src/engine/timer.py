from logger import logger
from typing import Callable, Any
5
class _TimerContainer:
    """Container object for timing events.
    """
    def __init__(self, total_time: float, event: Callable, *event_args, **event_kwargs) -> None:
        self.total_time: float = total_time
        self.time_remaining: float = total_time
        
        self.event: Callable = event
        self.event_args = event_args
        self.event_kwargs = event_kwargs
    
    def update(self, dt) -> bool:
        # Tick down remaining time
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            # Call timer event and pass in arguments
            self.event(*self.event_args, **self.event_kwargs)
            # Log & pop/delete timer container object
            logger.info(f"Timer expired with event {self.event}")
            return True
        return False

class _Tween:
    def __init__(self, total_time: float, obj: Any, var: str, end_val: Any, func: Callable | None, *func_args, **func_kwargs) -> None:
        self.start_val = getattr(obj, var)
        if not isinstance(end_val, type(self.start_val)):
            logger.warning(f"""Cannot create tween with start value type {type(self.start_val)} and end type {type(end_val)}!
                           Please ensure start and end values are of same type.""")
            return
        self.total_time: float = total_time
        self.time_remaining: float = total_time
        self.var: str = var
        self.end_val = end_val
        self.obj = obj
        self.obj_name: str = obj.__class__

        self.func: Callable | None = func
        self.func_args = func_args
        self.func_kwargs = func_kwargs

    def update(self, dt: float) -> bool:
        """Returns true if finished with the tween."""
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            if not self.obj:
                logger.warning(f"Tween referencing object {self.obj_name} that no longer exists!")
                return True
            
            setattr(self.obj, self.var, self.end_val)
            if self.func:
                self.func(self.func_args, self.func_kwargs)
            return True
        
        # Lerp the current value
        # t is from 0 to 1 as the tween progresses
        t = 1.0 - (self.time_remaining / self.total_time)
        
        # modify the target variable
        gap = self.end_val - self.start_val
        to_add = gap * t
        current_val = self.start_val + to_add
        
        if not self.obj:
            logger.warning(f"Tween referencing object {self.obj_name} that no longer exists!")
            return True

        setattr(self.obj, self.var, current_val)

        return False

class _TimeManager:
    def __init__(self) -> None:
        self._timers: list[_TimerContainer | _Tween] = []
    
    def update(self, dt: float) -> None:        
        # Update everything
        for i in range(len(self._timers)-1, -1, -1):
            obj = self._timers[i]
            if obj.update(dt):
                self._timers.remove(obj)
                del obj
                
    
    def create_timer(self, time: float, event: Callable, *event_args, **event_kwargs) -> None:
        self._timers.append(_TimerContainer(time, event, *event_args, **event_kwargs))
    
    def create_tween(self, total_time: float, obj: Any, var: str, end_val: Any, func: Callable | None = None, *func_args, **func_kwargs) -> None:
        """Register a tween in the timer manager.

        Args:
            total_time (float): Time for tween to last.
            obj (Any): Object to modify attribute of.
            var (str): Variable name of object to modify value of.
            end_val (Any): End value for obj.var to reach (must be of same type as var)
            func (Callable): Optional callback to be run when tween expires. Additional arguments passed as args and kwargs.
        """
        self._timers.append(_Tween(total_time, obj, var, end_val, func, *func_args, **func_kwargs))
    
