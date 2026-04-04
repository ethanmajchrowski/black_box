Overall Game Plan
You are an engineer who has woken up early from a medically induced coma on your multi-year deep space mission. Your goal is to determine the cause of this early wake, determine if the ship is safe to continue it's voyage, and figure out a way to return to your coma to survive the long years still remaining in the voyage. Your main source of information is the computer program in control of the ship, which will respond to commands you enter into your terminal.

Gameplay
- event -> evidence -> AI reasoning -> player questioning -> player decision
- player informs AI of their intended decision, AI responds with possible engine-bound responses and allows the player to choose one
  - player says "i want to divert oxygen" -> AI will determine close binary operations to be performed on internal data in the engine

special sauce
- AI has internal secrets
  - hide something about the mission?
  - fears being shut down
  - some bug in programming gives it faulty values?
- corrupted database / unable to access certain sensors or information sources



**Settings**

Resolution scaling:
```py
import pygame

# Set your internal "game" resolution
internal_res = (640, 480)
# Pygame scales this to fit the desktop or window automatically
screen = pygame.display.set_mode(internal_res, pygame.SCALED | pygame.FULLSCREEN)
```


**Todo**
- [x] Setup project (bring in engine)
- [x] Engine updates (add game state register so that engine handles all state switching) ~*note: not sure if this is actually needed, skipping for now*~
- [ ] AI connection (send and recieve messages from LLM)
- [ ] 