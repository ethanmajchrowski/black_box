from .asset_manager_ import _AssetManager
from .camera_ import Camera
from .game_states import GameState, _StateManager
from .entity import Entity
from .colors import color_linear_blend, modulate_color
from .event_bus import _EventBus
from .timer import _TimeManager
from .input import _InputManager
from .animation import _AnimationManager
from .game_map_ import _MapManager
from .physics_engine import _PhysicsManager

event_bus = _EventBus()

asset_manager = _AssetManager()
state_manager = _StateManager(event_bus)
time_manager = _TimeManager()
input_manager = _InputManager()
animations = _AnimationManager()
physics = _PhysicsManager()
camera = Camera()
map = _MapManager()

def setup(configuration):
    # Some engine things may require pygame to be initialized. When this runs that is true.
    input_manager.setup()
    animations.asset_manager = asset_manager
    asset_manager.load_assets(configuration.ROOT_ASSET_PATH)
    camera.set_screen_size()

def update(dt: float) -> None:
    time_manager.update(dt)
    state_manager.current_state.update(dt)
    input_manager.update(dt)
    animations.update(dt)
    camera.update(dt)
    physics.update(dt)