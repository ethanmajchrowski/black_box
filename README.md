# Black Box
A deduction and reasoning puzzle game where you interact with an LLM to determine the fate of a derelict spacecraft. 

[devpost](https://devpost.com/software/black-box-j8vs3x)

Made for the Blasterhacks 2026 Hackathon game dev track.
All code made by me. LLM tuning and prompts were heavily supported by gemini + chat (I've never made prompts like this before 😭)
System prompts (interesting stuff) are in `src/core/llm.py`

# Installation
I did not package game files (because I'm tired) and you'd still need to download more stuff anyways 🫟.
*also would not recommend installing this game - the model used for testing is 9 GB! you can adjust the model name in src/core/llm.py on line 71 if you want to use a model you already have or want to try a smaller model.*
- clone repo
- `pip install requirements.txt` (make a venv if you want) - game developed in Python 3.14.3 yada yada
- install LM Studio `https://lmstudio.ai/`
- install [qwen2.5-14b-instruct-1m](https://huggingface.co/lmstudio-community/Qwen2.5-14B-Instruct-1M-GGUF) within LM Studio

Asset Credit
- [Game Icon](https://thenounproject.com/icon/black-box-2024500/)
- [Pygame Logo](https://www.pygame.org/docs/logos.html)
- [LLM (qwen2.5-14b)](https://huggingface.co/lmstudio-community/Qwen2.5-14B-Instruct-1M-GGUF)
- [SFX](https://pixabay.com/sound-effects/film-special-effects-high-speed-mechanical-relay-98245/)
- [Font](https://fonts.google.com/specimen/Inter)