# 🧩 Group 19 – Tetris Game

## 📖 Overview
This project is a **modernized implementation of the classic Tetris game** built with **Python** and **Pygame**. It showcases object-oriented programming, modular design, and effective use of 2D rendering libraries.  

Players can enjoy smooth, responsive gameplay while experiencing classic Tetris mechanics such as line clearing, scoring, and piece holding — enhanced with modern features like ghost pieces, multiplayer mode, and a polished UI.  

This documentation serves as both a **user manual** and a **developer reference**, ensuring ease of use, setup, and further development.

---

## 🚀 Features
- 🎮 **Game Modes**: Single-player and Multiplayer.  
- ⏸️ **Pause/Resume**: Gameplay at any time.  
- 🔄 **Rotation system**: Clockwise. 
- 👻 **Ghost piece preview**: For better planning.  
- 📦 **Piece hold system**: Swap current tetromino. 
- 📊 **Statistics tracking**: Score, cleared lines, level/speed.  
- 🎨 **Custom renderer**: With clean, modern visuals  
- 🖱️ **Keyboard & Menu navigation**  

---

## 🎮 Controls
| Key | Action |
|-----|--------|
| **← / →** | Move piece left / right |
| **↓** | Soft drop (accelerated fall) |
| **↑** | Rotate clockwise |
| **Space** | Hard drop (instant fall) |
| **C** | Hold/swap current piece |
| **P** | Pause / Resume |
| **Enter** | Confirm menu selection |
| **Esc** | Back / Exit |

---

## 🛠️ Installation & Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/akanbrown3/group19-tetris-game.git
   cd  group19-tetris-game 
   ```

2. **Install dependencies**:
   ```bash
   pip install pygame
   ```

3. **Run the game**:
   ```bash
   python main.py
   ```

✅ *Python 3.10+ recommended.*  
✅ Runs on **Windows, macOS, and Linux** (with Pygame installed).  

---

## 📂 Project Structure
```
group19-tetris-game/
   ├── .github/
   │   └── workflows/
   │       └── ci.yml
   ├── src/
   │   ├── __init__.py
   │   ├── main.py
   │   ├── board.py
   │   ├── piece.py
   │   └── ui.py
   ├── tests/
   │   ├── __init__.py
   │   ├── test_board.py
   │   ├── test_piece.py
   │   └── test_game_logic.py
   ├── data/
   │   └── .gitkeep
   ├── .gitignore
   ├── Pipfile
   ├── Pipfile.lock
   ├── README.md
    
  


---

## 🧩 Module Documentation

### 🔹 `main.py`
**Role:** Entry point; controls the main loop, input, and game state transitions.  
**Key Classes:**
- `GameState`: Defines states (`MENU`, `PLAYING`, `PAUSED`, `GAME_OVER`).  
- `MenuButton`: Represents interactive UI buttons.  
- `TetrisGame`: Central controller of the game.  

**Responsibilities:**
- Initialize menus and UI (`setup_menu`)  
- Handle input (`handle_menu_input`, `handle_pause_input`, `handle_game_over_input`)  
- Update single-player and multiplayer states  
- Render menus and gameplay  
- Manage the main loop (`run`)  

---

### 🔹 `board.py`
**Role:** Implements the **game board and rules**.  
**Core Class:** `Board`  

**Responsibilities:**
- Piece spawning and movement (`spawn_piece`, `drop_piece`, `hard_drop`)  
- Collision and boundary checks (`is_valid_move`)  
- Piece rotation (`rotate_piece`)  
- Locking and line clearing (`lock_piece`, `clear_lines`)  
- Hold mechanic (`hold_piece`)  
- Return statistics (`get_stats`)  

---

### 🔹 `piece.py`
**Role:** Defines tetromino shapes and behavior.  
**Core Class:** `Piece`  

**Responsibilities:**
- Represent shapes (`I, O, T, S, Z, J, L`)  
- Handle rotation (`rotate_clockwise`)  
- Piece movement (`move`)  
- Duplication for ghost preview (`copy`)  
- Provide block positions (`get_blocks`)  

---

### 🔹 `ui.py`
**Role:** Manages **rendering and visual elements** using Pygame.  
**Core Class:** `TetrisRenderer`  

**Responsibilities:**
- Draw blocks and board background (`draw_block`, `draw_board_background`)  
- Render active and ghost pieces (`draw_piece`, `draw_ghost_piece`)  
- Show previews and held pieces (`draw_piece_preview`)  
- Display stats (score, lines, speed) (`draw_stats_panel`)  
- Render game modes: single-player and multiplayer (`render_single_player`, `render_multiplayer`)  

---

## 🏗️ Architecture & Data Flow
1. **`main.py`**: Runs game loop, processes inputs, and manages game states.  
2. **`board.py`**: Maintains board state, applies rules, calculates scores.  
3. **`piece.py`**: Handles tetromino logic (rotation, movement, cloning).  
4. **`ui.py`**: Renders all visual elements via Pygame.  

**Flow Example:**  
User Input (**main.py**) → Board Update (**board.py**) → Piece Update (**piece.py**) → Render Output (**ui.py**)  

---

## 👨‍💻 Contributors
### Leadership
- **Coordinator/Lead** – Akan Brown  
- **Assistant Coordinator** – Fatima Yusuf Hamman  

### Development  
- **Game Logic & Rendering** – Aiyegbusi Oyindamola, Hassan Praise Jesulayomi, Nuhu Umar (`board.py`,`piece.py`)  
- **Main Controller & UI ** – Otene Attah-Anukwu Daniel  (`main.py`,`ui.py`)  

### Quality & Documentation
- **QA/CI Lead** – Butler-Aneke Valentine (Pytest, GitHub Actions, code quality)  
- **Documentation Lead** – Ofishe Blessing Oghenero (README, reports, code docs)  
- **Media/Presentation Lead** – Akan Brown, Idowu Alao 


###  DEMO Link
-** https://drive.google.com/file/d/1tirV2FHd-XgD2wZH4qPg4vEfP-y8BD4E/view?usp=sharing



## 📄 License
This project is licensed under the **MIT License**.  
You are free to use, modify, and distribute it with attribution.  
