# Labyrinth of Despair

A highly difficult procedural roguelike game built with a **Python FastAPI (WebSocket)** server as the "Dungeon Master" and a **C# Spectre.Console** client as the player interface.

## Architecture Overview

### 1. Python Server (DM AI)
- **Role:** Central source of truth, map generation, AI logic, and game state management.
- **Tech:** `FastAPI`, `uvicorn`, `websockets`.
- **Map Generation:** Cellular Automata algorithm to generate claustrophobic, organic cave structures.
- **AI Logic:**
  - Enemies have varying behaviors:
    - **Stalkers:** Follow A* pathfinding precisely.
    - **Rushers:** Move faster but in straight lines.
    - **Lurkers:** Wait in shadows until the player is adjacent.

### 2. C# Client (Adventurer UI)
- **Role:** Handles player input, communicates with the server, and renders the game beautifully.
- **Tech:** `.NET 9`, `Spectre.Console`, `System.Net.WebSockets.ClientWebSocket`.
- **Rendering:** Uses `Canvas` or `Grid` components from `Spectre.Console` for rich, high-performance terminal rendering of characters, walls, shadows, and UI (Health, Logs).

## Communication Protocol (JSON over WebSockets)
- **Client to Server (Input):**
  - `{ "action": "move", "dir": [dx, dy] }`
  - `{ "action": "attack", "dir": [dx, dy] }`
- **Server to Client (State Update):**
  - Sends a limited viewport around the player.
  - `{ "player": { "hp": 10, "pos": [x,y] }, "map": [...], "entities": [...] }`

## Difficulty Factors
- Fog of War (Field of View constraint)
- Extremely low HP regeneration (if any)
- Intelligent enemy pathfinding (A* routing) that swarms the player
- Turn-based, where moving takes 1 action, but certain enemies take 2 actions per player action
