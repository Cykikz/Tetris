<div align="center">

# 🎮 Tetris Python

<img src="https://user-images.githubusercontent.com/74038190/212257467-871d32b7-e401-42e8-a166-fcfd7baa4c6b.gif" width="200" />

**A classic Tetris recreation with smooth gameplay and modern features**

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.5.0+-00C853?style=for-the-badge&logo=python&logoColor=white)](https://www.pygame.org/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

[Features](#-features) • [Installation](#-installation) • [How to Play](#-how-to-play) • [Game Mechanics](#-game-mechanics) • [Technical Details](#-technical-details)

</div>

---

## ✨ Features

- 🎯 **Classic Tetris Gameplay** - Authentic mechanics with 7 standard tetrominoes
- 👻 **Ghost Piece** - See where your piece will land with semi-transparent preview
- ⏱️ **Lock Delay System** - 0.5s grace period with slide mechanics for advanced play
- 🎵 **Procedural Sound Effects** - All audio generated in-code using sine waves
- 📊 **Progressive Difficulty** - Speed increases every level for endless challenge
- 💾 **High Score Tracking** - Best score automatically saved and persists between sessions
- 🎨 **Clean Minimal UI** - Dark theme with essential information at a glance
- 🔄 **Hold Piece System** - Strategic piece storage for optimal play
- ⌨️ **Responsive Controls** - Smooth movement, rotation, and instant hard drop

---

## 🚀 Installation

### Prerequisites
- Python 3.x
- pip (Python package installer)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/tetris-python.git
cd tetris-python
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the game**
```bash
python tetris.py
```

That's it! The game will launch in a new window.

---

## 🎮 How to Play

### Controls

| Key | Action |
|-----|--------|
| **←** / **→** | Move piece left/right |
| **↑** | Rotate piece clockwise |
| **↓** | Soft drop (faster fall) |
| **Space** | Hard drop (instant placement) |
| **C** | Hold current piece |
| **P** | Pause/Resume game |
| **Space** (Game Over) | Restart game |

### Objective

- Stack falling tetrominoes to create complete horizontal lines
- Completed lines disappear and award points
- Game ends when pieces stack to the top of the playfield
- Achieve the highest score possible!

---

## 🧩 Game Mechanics

### Tetrominoes

Seven classic shapes, each with 4 rotation states:

```
I-piece  O-piece  T-piece  S-piece  Z-piece  L-piece  J-piece
  ████     ██       ██       ██     ██         ██     ██
  ████     ████   ██████   ████     ████       ██   ████
  ████     ██       ██       ██     ██       ████     ██
  ████     ████   ██████   ████     ████       ██   ████
```

### Scoring System

**Line Clears** (Nintendo-style multiplier):
- Single (1 line): `100 × level`
- Double (2 lines): `300 × level`
- Triple (3 lines): `500 × level`
- Tetris (4 lines): `800 × level`

**Drop Points**:
- Soft drop: `+1 point per row`
- Hard drop: `+2 points per row`

### Level Progression

- Start at **Level 1**
- Level up every **10 lines cleared**
- Fall speed increases with each level
- Minimum fall interval caps at higher levels for playability

### Lock Delay ("Slide")

- **0.5 seconds** grace period after piece lands
- Moving or rotating the piece **resets** the lock timer
- Enables advanced techniques like sliding and T-spins setup

### Ghost Piece

- Semi-transparent preview shows landing position
- Same color as active piece with reduced opacity
- Updates in real-time as you move/rotate

---

## 🏗️ Technical Details

### Tech Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3 |
| **Graphics & Input** | Pygame 2.5.0+ |
| **Audio** | Pygame Mixer (procedural generation) |
| **Dependencies** | Standard library only (random, os, math, array) |

### Project Structure

```
tetris-python/
├── tetris.py              # Main game file (all logic, rendering, audio)
├── requirements.txt       # Python dependencies
├── highscore.txt         # Auto-generated high score file
└── .vscode/
    └── settings.json     # Optional editor configuration
```

### Architecture

**Single-file design** (`tetris.py`):
- Game state management
- Collision detection
- Line clearing algorithm
- Scoring & leveling system
- Pygame rendering
- Procedural audio generation
- Input handling
- Main game loop

### Game Grid

- **Dimensions**: 10 columns × 20 rows
- **Block size**: 26×26 pixels
- **Play area**: 260×520 pixels
- **Window size**: 380×600 pixels (includes sidebar)

### Audio System

All sounds are **generated programmatically** using sine waves:

```python
# Example: Generate tone using math.sin and array
frequency = 440  # Hz
duration = 0.1   # seconds
samples = int(22050 * duration)
wave = array.array('h', [
    int(32767 * math.sin(2 * math.pi * frequency * i / 22050))
    for i in range(samples)
])
```

**Sound Events**:
- Move piece
- Rotate piece
- Hard drop
- Line clear
- Level up
- Game over

**Fallback**: If audio initialization fails, game continues silently.

### UI Design

**Color Scheme** (Dark Theme):
```python
BG           = (20, 20, 30)      # Background
GRID_BG      = (30, 30, 40)      # Play area
GRID_LINE    = (50, 50, 60)      # Grid lines
SIDEBAR_BG   = (25, 25, 35)      # Sidebar
TEXT         = (255, 255, 255)   # Primary text
TEXT_MUTED   = (150, 150, 160)   # Secondary text
ACCENT       = (0, 217, 255)     # Highlights
```

**Layout**:
- Left: 10×20 play area with 1px grid lines
- Right sidebar:
  - HOLD preview box
  - NEXT preview box
  - SCORE display
  - BEST (high score)
  - LEVEL counter
  - LINES cleared
  - "P Pause" hint

**Overlays**:
- Game Over: Dimmed background + "GAME OVER" text + restart hint
- Pause: Dimmed background + "PAUSED" text

### Piece Spawning

- Uses **bounding box calculation** for centered spawning
- Handles all rotations correctly (including vertical I-piece)
- Spawns at top-center of playfield

### Collision Detection

```python
def valid_position(shape, x, y, locked):
    # Check if piece position is valid
    # - Within grid boundaries
    # - Not overlapping locked blocks
    # Returns True/False
```

### Line Clearing Algorithm

1. Detect full rows (all 10 columns filled)
2. Remove completed rows from locked positions
3. Shift all rows above downward
4. Update score based on lines cleared
5. Increment level every 10 lines

---

## 📊 Gameplay Stats

The sidebar displays real-time information:

- **HOLD**: Preview of held piece
- **NEXT**: Preview of upcoming piece
- **SCORE**: Current game score
- **BEST**: All-time high score
- **LEVEL**: Current difficulty level
- **LINES**: Total lines cleared

---

## 🎨 Visual Features

### Piece Rendering
- Flat colored rectangles with 1px black outline
- Each tetromino has a distinct color
- Ghost piece uses same color with reduced alpha

### Animations
- Smooth 60 FPS gameplay
- Progressive fall speed increase
- Instant visual feedback on all actions

### Overlays
- **Game Over**: Semi-transparent dark overlay with centered text
- **Pause**: Similar overlay indicating paused state
- No intrusive panels or dialogs

---

## 🔧 Configuration

### Customization

All game parameters are defined in `tetris.py` and can be easily modified:

```python
# Grid dimensions
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 26

# Timing
LOCK_DELAY = 0.5  # seconds
INITIAL_FALL_INTERVAL = 1.0  # seconds

# Scoring multipliers
SCORE_SINGLE = 100
SCORE_DOUBLE = 300
SCORE_TRIPLE = 500
SCORE_TETRIS = 800
```

---

## 🐛 Known Limitations

- No T-spin detection (standard rotation only)
- No wall kicks for advanced piece rotation
- Single-player only (no multiplayer mode)
- No music (sound effects only)

---

## 🚀 Future Enhancements

Potential features for future versions:

- [ ] T-spin detection and bonus scoring
- [ ] Wall kick system (SRS - Super Rotation System)
- [ ] Multiple game modes (Marathon, Sprint, Ultra)
- [ ] Customizable controls
- [ ] Settings menu
- [ ] Background music
- [ ] Visual effects for line clears
- [ ] Combo system
- [ ] Statistics tracking (pieces placed, time played, etc.)

---

## 📝 Requirements

### Minimal Dependencies

```txt
pygame>=2.5.0
```

No NumPy, no external audio files, no images - just Python and Pygame!

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Original Tetris concept by Alexey Pajitnov
- Nintendo scoring system
- Pygame community for excellent documentation

---

<div align="center">

### 💖 Enjoyed the game?

Give it a ⭐ if you found this project helpful!

**Built with ❤️ and Python**

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="100%">

</div>
