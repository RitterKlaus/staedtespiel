# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pygame
```

## Running the game

```bash
.venv/bin/python game.py
```

## Architecture

`game.py` contains the entire game: terrain constants (`WIESE`, `WALD`, `BERGE`), the map grid (`KARTE` — a 2D list), tile loading (`lade_tiles`), map rendering (`zeichne_karte`), and the main loop. Tiles are 64×64 px images in `assets/`. The window size is derived from the map dimensions.
