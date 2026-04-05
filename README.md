# Black Box
 A deduction and reasoning puzzle game where you interact with an LLM to determine the fate of a derelict spacecraft. 

 devpost page: `https://devpost.com/software/black-box-j8vs3x`

 Made for the Blasterhacks 2026 Hackathon game dev track.
All code made by me. LLM tuning and prompts were heavily supported by gemini + chat (I've never made prompts like this before 😭)
System prompts (interesting stuff) are in `src/core/llm.py`

# Installation
I did not package game files (because I'm tired) and you'd still need to download more stuff anyways 🫟.
*also would not recommend installing this game - the model used for testing is 9 GB! you can adjust the model name in src/core/llm.py on line 71 if you want to use a model you already have or want to try a smaller model.*
- clone repo
- `pip install requirements.txt` (make a venv if you want) - game developed in Python 3.14.3 yada yada
- install LM Studio `https://lmstudio.ai/`
- install [qwen2.5-14b-instruct-1m](https://lmstudio.ai/models/qwen/qwen3.5-9b) within LM Studio