from logger import logger
from typing import Callable, TYPE_CHECKING
if TYPE_CHECKING:
    from engine.asset_manager_ import _AssetManager

class _Animation():
    def __init__(self, asset_name: str, num_frames: int, callback: Callable | None, repeating: bool = False, fps: int = 24) -> None:
        self.asset_name = asset_name
        self.num_frames = num_frames
        self.callback = callback
        self.repeating = repeating

        self.frame_time = (1000 / fps) / 1000
        self.current_time: float = 0.0
        self.current_frame = 0
        
        self.asset = None

class _AnimationManager:
    def __init__(self) -> None:
        self.animations: dict[str, _Animation] = {}
        self._running_animations: list[_Animation] = []
        self.asset_manager: _AssetManager
        
    def update(self, dt):                
        for i in range(len(self._running_animations)-1, -1, -1):
            anim = self._running_animations[i]
            anim.asset = self.asset_manager.get("animations", f"{anim.asset_name}_{anim.current_frame}")
            anim.current_time += dt
            if not anim.current_time >= anim.frame_time:
                continue
            
            if anim.current_frame+1 == anim.num_frames:
                self._running_animations.remove(anim)
                if anim.callback: anim.callback()
                if anim.repeating:
                    self._running_animations.append(anim)
                continue
            
            anim.current_frame += 1
            anim.current_time = 0
            anim.asset = self.asset_manager.get("animations", f"{anim.asset_name}_{anim.current_frame}")
    
    def get_running_animation(self, name: str):
        anim = self.animations.get(name)
        if not anim: return None
        if not anim in self._running_animations: return None

        return anim
    
    def create_animation(self, animation_name: str, asset_name: str, num_frames: int, callback: Callable | None = None, 
                         repeating: bool = False, fps: int = 24, start_on_creation: bool = False):
        self.animations[animation_name] = _Animation(asset_name, num_frames, callback, repeating, fps)
        if start_on_creation:
            self.start_animation(animation_name)
    
    def start_animation(self, name: str):
        anim = self.animations.get(name)
        if not anim: 
            logger.warning(f"Animation not started: {name} (animation not found).")
            return
        
        # handle other startup stuff
        anim.current_time = 0
        anim.current_frame = 0
        
        self._running_animations.append(anim)