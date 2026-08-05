# Pytherra

Pytherra is a small 2D sandbox/terrain exploration prototype written in Python using pygame-ce and Perlin noise for procedural terrain generation. The project contains a simple player, world/chunk system, input controls, and debug tools for experimenting with camera/scaling and block interactions.

> Note: The codebase is located under the `src/` directory. To run the project run from the `src/` directory (see instructions below).

## Features

- Procedurally generated terrain using Perlin noise
- Smooth camera with zoom and scaling
- Player with basic physics and collision
- Inventory hotkeys and mouse interaction
- Debug overlays and toggleable debug modes

## Requirements

- Python 3.8+ (3.10+ recommended)
- pip

Install dependencies:

```bash
pip install -r requirements.txt
```

Current requirements (requirements.txt):
- perlin-noise>=1.13
- pygame-ce>=2.5.7

(There is an empty line at the end of requirements.txt — ensure it is valid for your environment.)

## Running the game

Recommended: run from the `src` directory so imports resolve correctly.

```bash
cd src
python main.py
```

Alternatively you can run from repository root by adding `src` to PYTHONPATH:

```bash
PYTHONPATH=src python src/main.py
# On Windows (PowerShell):
# $env:PYTHONPATH = "src"; python src/main.py
```

The game creates a `pytherra` application instance in `src/main.py`. You can change the seed by editing the line near the bottom:

```py
if __name__ == "__main__":
    app = pytherra(0)  # pass an integer seed or None for a random seed
    app.run()
```

## Controls

- ESC: Quit
- R: Reset window size (1000x800)
- + / - (equals / minus): Zoom in / out
- C: Toggle simple color mode for the world
- N: Toggle NO_CLIP (only when GAME_DEBUG is enabled)
- F1: Toggle GAME_DEBUG
- F2: Toggle CONSOLE_DEBUG
- F3: Toggle UI_DEBUG
- Number keys 1–9: Select inventory slot 0–8
- E: Toggle inventory UI
- Mouse wheel: Scroll inventory (if inventory is closed)
- Left / Right mouse: interact/place/break blocks (see Controls implementation in src/Controls)

## Project layout

- src/
  - main.py — entry point and main game loop
  - Player/ — player character, physics, inventory
  - Controls/ — mouse and input handling
  - Game/ — world generation, drawing, utilities, loading screen
  - Jsons/ — sample JSON data used by the game
- World_data/ — pre-generated or exported world data
- assets/ — images and other assets used by the game
- requirements.txt — Python dependencies

## Development

- Code lives under `src/`. Use `cd src` when running or set PYTHONPATH appropriately.
- The game uses pygame for rendering. If you're on Linux ensure SDL-related system packages are installed so pygame-ce can build and run.
- To change the default world seed or world size, edit `src/main.py` where `pytherra` is instantiated and `WORLD_SIZE` is set.

## Contributing

Contributions are welcome. If you want to contribute:

1. Fork the repository
2. Create a branch for your feature or fix
3. Make changes and commit
4. Open a pull request describing the change

Please include a short description of the goal and any reproducible steps for bugs.

## Troubleshooting

- If imports fail (ModuleNotFoundError for Player, Game, Controls): make sure you run `main.py` from within the `src` directory or add `src` to PYTHONPATH.
- If pygame fails to install, check system libraries (SDL2) and use your system package manager to install required dependencies.

## License

No license is specified in this repository. If you want an explicit license, add a `LICENSE` file (for example MIT or Apache-2.0).

---

If you'd like, I can also:
- Add a small example image in the README that references `assets/` screenshots
- Add a requirements/tips section for Windows/macOS/Linux (SDL dependencies)
- Update `requirements.txt` to remove the empty trailing line

