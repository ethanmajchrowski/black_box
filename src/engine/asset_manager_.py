from os import listdir
from typing import Any

import pygame as pg

from logger import logger


class _AssetManager:
    def __init__(self) -> None:
        self.assets: dict[str, dict[str, Any]] = {}
    
    def register_group(self, group_name: str):
        self.assets.setdefault(group_name, {})
    
    def add_asset(self, group: str, name: str, asset):
        self.register_group(group)
        self.assets[group][name] = asset
    
    def get(self, group: str, name: str) -> Any:
        if group in self.assets and name in self.assets[group]:
            return self.assets[group][name]
        raise FileNotFoundError(f"Asset not found: '{name}' in '{group}'.")
    
    def load_assets(self, root_path: str) -> None:
        #TODO load assets & sort based on positions in the folders in this directory
        # Devise a file organization to support assets
        # Allow .json for more specific cases (ex. animations)
        print(listdir(root_path))
    
    def load_sfx(self, path: str) -> pg.mixer.Sound:
        logger.debug(f"Loading sound {path}")
        return pg.mixer.Sound(path)

    def load_img(self, path: str, size: None | float | tuple[int, int] = None) -> pg.Surface:
        logger.debug(f"Loading image {path} and scaling to {size}")
        if size:
            if isinstance(size, float):
                return pg.transform.smoothscale_by(pg.image.load(path).convert_alpha(), size)
            else:
                assert isinstance(size, tuple)
                return pg.transform.smoothscale(pg.image.load(path).convert_alpha(), size)
        else: return pg.image.load(path).convert_alpha()
    
    def load_animation(self, path: str, num_frames: int, animation_name: str, size: None | float | tuple[int, int] = None):
        """
        Loads a sequence of images to create an animation and adds them to the asset manager.

        Assumes animation frames are named with a numerical suffix (e.g., path_0, path_1, ...).
        Loads .png images.
        
        Directly adds loaded assets into asset manager.

        Args:
            path (str): The base file path or prefix for the animation frame images.
            num_frames (int): The total number of frames in the animation.
            animation_name (str): The base name to identify this animation, 
                used as a prefix for the stored asset keys.

        Example:
            If `path` is "assets/player_run" and `num_frames` is 3, it loads
            "assets/player_run_0.png", "assets/player_run_1.png", etc.
        """
        for i in range(num_frames):
            self.add_asset("animations", f"{animation_name}_{i}", self.load_img(f"{path}_{i}.png", size))