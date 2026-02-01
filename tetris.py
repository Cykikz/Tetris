"""
Minimal Tetris: clean GUI, sounds, lock delay.
"""

import pygame
import random
import os
import math
import array

# Initialize pygame (mixer before display for sound)
pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.init()

# Screen
SCREEN_WIDTH = 380
SCREEN_HEIGHT = 600
BLOCK_SIZE = 26
PREVIEW_SIZE = 12
MARGIN = 8

# Minimal palette
BG = (18, 18, 24)
GRID_BG = (26, 26, 34)
GRID_LINE = (42, 42, 54)
SIDEBAR_BG = (22, 22, 30)
TEXT = (200, 200, 212)
TEXT_MUTED = (120, 120, 132)
ACCENT = (72, 72, 92)
GHOST_ALPHA = 90

# Tetromino colors (I, O, T, S, Z, L, J)
COLORS = [
    (0, 220, 240), (240, 220, 60), (180, 90, 240),
    (60, 200, 100), (220, 70, 70), (240, 160, 50), (60, 110, 240),
]

# Shapes: each is a list of 4 rotation states (0°, 90°, 180°, 270°)
# I, O, T, S, Z, L, J
SHAPES = [
    [[[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
     [[0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0]],
     [[0, 0, 0, 0], [0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0]],
     [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]]],
    [[[1, 1], [1, 1]], [[1, 1], [1, 1]], [[1, 1], [1, 1]], [[1, 1], [1, 1]]],
    [[[0, 1, 0], [1, 1, 1], [0, 0, 0]],
     [[0, 1, 0], [0, 1, 1], [0, 1, 0]],
     [[0, 0, 0], [1, 1, 1], [0, 1, 0]],
     [[0, 1, 0], [1, 1, 0], [0, 1, 0]]],
    [[[0, 1, 1], [1, 1, 0], [0, 0, 0]],
     [[0, 1, 0], [0, 1, 1], [0, 0, 1]],
     [[0, 0, 0], [0, 1, 1], [1, 1, 0]],
     [[1, 0, 0], [1, 1, 0], [0, 1, 0]]],
    [[[1, 1, 0], [0, 1, 1], [0, 0, 0]],
     [[0, 0, 1], [0, 1, 1], [0, 1, 0]],
     [[0, 0, 0], [1, 1, 0], [0, 1, 1]],
     [[0, 1, 0], [1, 1, 0], [1, 0, 0]]],
    [[[1, 1, 1], [1, 0, 0], [0, 0, 0]],
     [[0, 1, 1], [0, 1, 0], [0, 1, 0]],
     [[0, 0, 0], [0, 0, 1], [1, 1, 1]],
     [[0, 1, 0], [0, 1, 0], [0, 1, 1]]],
    [[[1, 1, 1], [0, 0, 1], [0, 0, 0]],
     [[0, 1, 0], [0, 1, 0], [0, 1, 1]],
     [[0, 0, 0], [1, 0, 0], [1, 1, 1]],
     [[0, 1, 1], [0, 1, 0], [0, 1, 0]]],
]

# Grid
GRID_WIDTH = 10
GRID_HEIGHT = 20
PLAY_W = GRID_WIDTH * BLOCK_SIZE
PLAY_H = GRID_HEIGHT * BLOCK_SIZE
SIDEBAR_W = SCREEN_WIDTH - PLAY_W - MARGIN * 2
SIDEBAR_X = PLAY_W + MARGIN

# Scoring
SCORE_PER_LINE = (0, 100, 300, 500, 800)
SOFT_DROP_POINTS = 1
HARD_DROP_POINTS = 2

# Level & timing
INITIAL_FALL_SPEED = 0.72
LEVEL_SPEED_DECREASE = 0.065
MIN_FALL_SPEED = 0.06
LINES_PER_LEVEL = 10
LOCK_DELAY = 0.5  # seconds to move/rotate after landing before lock

HIGH_SCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscore.txt")

# Sound (generated beeps)
SAMPLE_RATE = 22050
_sounds = {}


def _beep(freq, duration_ms, volume=0.15):
    n = int(SAMPLE_RATE * duration_ms / 1000.0)
    buf = array.array("h")
    for i in range(n):
        val = int(32767 * volume * math.sin(2 * math.pi * freq * i / SAMPLE_RATE))
        buf.append(max(-32768, min(32767, val)))
    return pygame.mixer.Sound(buffer=buf)


def init_sounds():
    try:
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512)
        _sounds["move"] = _beep(180, 35)
        _sounds["rotate"] = _beep(280, 45)
        _sounds["drop"] = _beep(120, 25)
        _sounds["clear"] = _beep(400, 80)
        _sounds["level"] = _beep(520, 60)
        _sounds["gameover"] = _beep(200, 300)
    except Exception:
        _sounds.clear()


def play(name):
    if name in _sounds:
        try:
            _sounds[name].play()
        except Exception:
            pass


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()
init_sounds()

try:
    font = pygame.font.Font(None, 26)
    small_font = pygame.font.Font(None, 22)
except Exception:
    font = pygame.font.SysFont("arial", 18)
    small_font = pygame.font.SysFont("arial", 16)


def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                return int(f.read().strip())
        except (ValueError, IOError):
            pass
    return 0


def save_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write(str(score))
    except IOError:
        pass


def get_shape_cells(shape_idx, rotation):
    """Return the 4x4 or 3x3 matrix for the shape at given rotation (0-3)."""
    s = SHAPES[shape_idx]
    r = rotation % len(s)
    return s[r]


def get_spawn_x(shape_matrix):
    """Return x position to center the shape in the grid."""
    cols = len(shape_matrix[0])
    min_x = next((x for x in range(cols) if any(row[x] for row in shape_matrix)), 0)
    max_x = next((x for x in range(cols - 1, -1, -1) if any(row[x] for row in shape_matrix)), cols - 1)
    width = max_x - min_x + 1
    return (GRID_WIDTH - width) // 2 - min_x


def valid_position(shape_matrix, pos_x, pos_y, locked):
    """Check if the shape at (pos_x, pos_y) fits without collision."""
    for y, row in enumerate(shape_matrix):
        for x, cell in enumerate(row):
            if cell:
                nx, ny = pos_x + x, pos_y + y
                if nx < 0 or nx >= GRID_WIDTH or ny >= GRID_HEIGHT:
                    return False
                if ny >= 0 and (nx, ny) in locked:
                    return False
    return True


def get_ghost_y(shape_matrix, pos_x, pos_y, locked):
    """Return the Y position where the piece would land (hard drop position)."""
    gy = pos_y
    while valid_position(shape_matrix, pos_x, gy + 1, locked):
        gy += 1
    return gy


def create_grid(locked):
    grid = [[GRID_BG for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for (x, y), color in locked.items():
        if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
            grid[y][x] = color
    return grid


def draw_block(surface, x, y, color, size=BLOCK_SIZE):
    r = pygame.Rect(x * size, y * size, size - 1, size - 1)
    pygame.draw.rect(surface, color, r)
    pygame.draw.rect(surface, GRID_LINE, r, 1)


def draw_ghost_block(surface, x, y, color, size=BLOCK_SIZE):
    r = pygame.Rect(x * size, y * size, size - 1, size - 1)
    s = pygame.Surface((size, size))
    s.set_alpha(GHOST_ALPHA)
    s.fill(color)
    surface.blit(s, r.topleft)
    pygame.draw.rect(surface, GRID_LINE, r, 1)


def draw_grid(surface, grid):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            draw_block(surface, x, y, grid[y][x])
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(surface, GRID_LINE, (0, y * BLOCK_SIZE), (PLAY_W, y * BLOCK_SIZE), 1)
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(surface, GRID_LINE, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, PLAY_H), 1)


def draw_play_area(surface):
    pygame.draw.rect(surface, GRID_BG, (0, 0, PLAY_W, PLAY_H))
    pygame.draw.rect(surface, ACCENT, (0, 0, PLAY_W, PLAY_H), 1)


def draw_piece(surface, shape_matrix, pos_x, pos_y, color, ghost=False, size=BLOCK_SIZE):
    for y, row in enumerate(shape_matrix):
        for x, cell in enumerate(row):
            if cell:
                nx, ny = pos_x + x, pos_y + y
                if ny >= 0:
                    if ghost:
                        draw_ghost_block(surface, nx, ny, color, size)
                    else:
                        draw_block(surface, nx, ny, color, size)


def _preview(surface, shape_idx, x, y, size=PREVIEW_SIZE):
    mat = get_shape_cells(shape_idx, 0)
    color = COLORS[shape_idx]
    cw, ch = len(mat[0]), len(mat)
    ox = x + max(0, (SIDEBAR_W - cw * size) // 2)
    oy = y
    for cy, row in enumerate(mat):
        for cx, cell in enumerate(row):
            if cell:
                r = pygame.Rect(ox + cx * size, oy + cy * size, size - 1, size - 1)
                pygame.draw.rect(surface, color, r)
                pygame.draw.rect(surface, GRID_LINE, r, 1)


def draw_sidebar(surface, next_idx, hold_idx, score, high_score, level, lines_cleared):
    pygame.draw.rect(surface, SIDEBAR_BG, (SIDEBAR_X, 0, SIDEBAR_W + MARGIN, SCREEN_HEIGHT))
    x = SIDEBAR_X
    w = SIDEBAR_W
    dy = MARGIN

    surface.blit(small_font.render("HOLD", True, TEXT_MUTED), (x, dy))
    dy += 20
    if hold_idx is not None:
        _preview(surface, hold_idx, x, dy, PREVIEW_SIZE)
    dy += 52

    surface.blit(small_font.render("NEXT", True, TEXT_MUTED), (x, dy))
    dy += 20
    if next_idx is not None:
        _preview(surface, next_idx, x, dy, PREVIEW_SIZE)
    dy += 52

    dy += 8
    surface.blit(small_font.render("SCORE", True, TEXT_MUTED), (x, dy))
    surface.blit(font.render(str(score), True, TEXT), (x, dy + 18))
    dy += 44
    surface.blit(small_font.render("BEST", True, TEXT_MUTED), (x, dy))
    surface.blit(font.render(str(high_score), True, TEXT), (x, dy + 18))
    dy += 44
    surface.blit(small_font.render("LEVEL", True, TEXT_MUTED), (x, dy))
    surface.blit(font.render(str(level), True, TEXT), (x, dy + 18))
    dy += 44
    surface.blit(small_font.render("LINES", True, TEXT_MUTED), (x, dy))
    surface.blit(font.render(str(lines_cleared), True, TEXT), (x, dy + 18))
    dy += 52

    surface.blit(small_font.render("P  Pause", True, TEXT_MUTED), (x, dy))


def clear_full_rows(locked):
    """Clear full rows and shift above blocks down. Returns number of lines cleared."""
    full_rows = []
    for y in range(GRID_HEIGHT):
        if all((x, y) in locked for x in range(GRID_WIDTH)):
            full_rows.append(y)
    if not full_rows:
        return 0
    full_rows.sort()
    new_locked = {}
    for (x, y), color in locked.items():
        if y in full_rows:
            continue
        num_below = sum(1 for r in full_rows if r > y)
        new_locked[(x, y + num_below)] = color
    locked.clear()
    locked.update(new_locked)
    return len(full_rows)


def main():
    high_score = load_high_score()

    def init_game():
        locked = {}
        shape_idx = random.randint(0, len(SHAPES) - 1)
        rotation = 0
        next_idx = random.randint(0, len(SHAPES) - 1)
        hold_idx = None
        can_hold = True
        pos_x = get_spawn_x(get_shape_cells(shape_idx, rotation))
        pos_y = 0
        score = 0
        level = 1
        lines_cleared_total = 0
        fall_time = 0
        fall_speed = INITIAL_FALL_SPEED
        lock_timer = 0
        return {
            "locked": locked,
            "shape_idx": shape_idx,
            "rotation": rotation,
            "next_idx": next_idx,
            "hold_idx": hold_idx,
            "can_hold": can_hold,
            "pos_x": pos_x,
            "pos_y": pos_y,
            "score": score,
            "level": level,
            "lines_cleared_total": lines_cleared_total,
            "fall_time": fall_time,
            "fall_speed": fall_speed,
            "lock_timer": lock_timer,
        }

    state = init_game()
    paused = False
    game_over = False
    run = True

    while run:
        delta_ms = clock.tick(60)
        locked = state["locked"]
        shape_idx = state["shape_idx"]
        rotation = state["rotation"]
        next_idx = state["next_idx"]
        hold_idx = state["hold_idx"]
        can_hold = state["can_hold"]
        pos_x, pos_y = state["pos_x"], state["pos_y"]
        score = state["score"]
        level = state["level"]
        lines_cleared_total = state["lines_cleared_total"]
        fall_speed = state["fall_speed"]
        lock_timer = state["lock_timer"]

        shape_matrix = get_shape_cells(shape_idx, rotation)
        color = COLORS[shape_idx]

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                    continue
                if game_over:
                    if event.key == pygame.K_SPACE:
                        state = init_game()
                        game_over = False
                    continue
                if paused:
                    continue

                if event.key == pygame.K_LEFT:
                    if valid_position(shape_matrix, pos_x - 1, pos_y, locked):
                        state["pos_x"] = pos_x - 1
                        state["lock_timer"] = 0
                        play("move")
                elif event.key == pygame.K_RIGHT:
                    if valid_position(shape_matrix, pos_x + 1, pos_y, locked):
                        state["pos_x"] = pos_x + 1
                        state["lock_timer"] = 0
                        play("move")
                elif event.key == pygame.K_DOWN:
                    if valid_position(shape_matrix, pos_x, pos_y + 1, locked):
                        state["pos_y"] = pos_y + 1
                        state["score"] = score + SOFT_DROP_POINTS
                        state["lock_timer"] = 0
                elif event.key == pygame.K_UP:
                    new_rot = (rotation + 1) % 4
                    new_mat = get_shape_cells(shape_idx, new_rot)
                    if valid_position(new_mat, pos_x, pos_y, locked):
                        state["rotation"] = new_rot
                        state["lock_timer"] = 0
                        play("rotate")
                elif event.key == pygame.K_SPACE:
                    play("drop")
                    gy = get_ghost_y(shape_matrix, pos_x, pos_y, locked)
                    drop_dist = gy - pos_y
                    state["pos_y"] = gy
                    state["score"] = score + HARD_DROP_POINTS * drop_dist
                    state["fall_time"] = 0
                    for y, row in enumerate(shape_matrix):
                        for x, cell in enumerate(row):
                            if cell:
                                nx, ny = pos_x + x, gy + y
                                if ny >= 0:
                                    locked[(nx, ny)] = color
                    lines = clear_full_rows(locked)
                    if lines:
                        play("clear")
                    state["score"] += SCORE_PER_LINE[lines] * level
                    state["lines_cleared_total"] = lines_cleared_total + lines
                    new_level = (lines_cleared_total + lines) // LINES_PER_LEVEL + 1
                    if new_level > level:
                        state["level"] = new_level
                        state["fall_speed"] = max(MIN_FALL_SPEED, INITIAL_FALL_SPEED - (new_level - 1) * LEVEL_SPEED_DECREASE)
                        play("level")
                    state["shape_idx"] = next_idx
                    state["rotation"] = 0
                    state["next_idx"] = random.randint(0, len(SHAPES) - 1)
                    state["pos_x"] = get_spawn_x(get_shape_cells(next_idx, 0))
                    state["pos_y"] = 0
                    state["can_hold"] = True
                    state["lock_timer"] = 0
                    if not valid_position(get_shape_cells(next_idx, 0), state["pos_x"], 0, locked):
                        game_over = True
                        play("gameover")
                        if state["score"] > high_score:
                            high_score = state["score"]
                            save_high_score(high_score)
                    continue
                elif event.key == pygame.K_c:
                    if not can_hold:
                        pass
                    else:
                        if hold_idx is None:
                            state["hold_idx"] = shape_idx
                            state["shape_idx"] = next_idx
                            state["rotation"] = 0
                            state["next_idx"] = random.randint(0, len(SHAPES) - 1)
                            state["pos_x"] = get_spawn_x(get_shape_cells(next_idx, 0))
                            state["pos_y"] = 0
                        else:
                            state["hold_idx"] = shape_idx
                            state["shape_idx"] = hold_idx
                            state["rotation"] = 0
                            state["pos_x"] = get_spawn_x(get_shape_cells(hold_idx, 0))
                            state["pos_y"] = 0
                        state["can_hold"] = False

        if game_over:
            screen.fill(BG)
            draw_play_area(screen)
            grid = create_grid(locked)
            draw_grid(screen, grid)
            draw_sidebar(screen, next_idx, hold_idx, state["score"], high_score, state["level"], state["lines_cleared_total"])
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BG)
            screen.blit(overlay, (0, 0))
            go = font.render("GAME OVER", True, TEXT)
            r = font.render("SPACE to restart", True, TEXT_MUTED)
            screen.blit(go, (SCREEN_WIDTH // 2 - go.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
            screen.blit(r, (SCREEN_WIDTH // 2 - r.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
            pygame.display.flip()
            continue

        if paused:
            screen.fill(BG)
            draw_play_area(screen)
            grid = create_grid(locked)
            draw_grid(screen, grid)
            draw_piece(screen, shape_matrix, pos_x, pos_y, color)
            ghost_y = get_ghost_y(shape_matrix, pos_x, pos_y, locked)
            draw_piece(screen, shape_matrix, pos_x, ghost_y, color, ghost=True)
            draw_sidebar(screen, next_idx, hold_idx, score, high_score, level, lines_cleared_total)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BG)
            screen.blit(overlay, (0, 0))
            p = font.render("PAUSED", True, TEXT)
            screen.blit(p, (SCREEN_WIDTH // 2 - p.get_width() // 2, SCREEN_HEIGHT // 2 - 14))
            pygame.display.flip()
            continue

        # Gravity
        state["fall_time"] += delta_ms / 1000.0
        if state["fall_time"] >= fall_speed:
            state["fall_time"] = 0
            if valid_position(shape_matrix, pos_x, pos_y + 1, locked):
                state["pos_y"] = pos_y + 1
                state["lock_timer"] = 0

        # Lock delay: when piece has landed, wait LOCK_DELAY before locking (so you can slide)
        if not valid_position(shape_matrix, pos_x, pos_y + 1, locked):
            state["lock_timer"] += delta_ms / 1000.0
            if state["lock_timer"] >= LOCK_DELAY:
                for y, row in enumerate(shape_matrix):
                    for x, cell in enumerate(row):
                        if cell:
                            nx, ny = pos_x + x, pos_y + y
                            if ny >= 0:
                                locked[(nx, ny)] = color
                lines = clear_full_rows(locked)
                if lines:
                    play("clear")
                state["score"] += SCORE_PER_LINE[lines] * level
                state["lines_cleared_total"] = lines_cleared_total + lines
                new_level = (lines_cleared_total + lines) // LINES_PER_LEVEL + 1
                if new_level > level:
                    state["level"] = new_level
                    state["fall_speed"] = max(MIN_FALL_SPEED, INITIAL_FALL_SPEED - (new_level - 1) * LEVEL_SPEED_DECREASE)
                    play("level")
                state["shape_idx"] = next_idx
                state["rotation"] = 0
                state["next_idx"] = random.randint(0, len(SHAPES) - 1)
                state["pos_x"] = get_spawn_x(get_shape_cells(next_idx, 0))
                state["pos_y"] = 0
                state["can_hold"] = True
                state["lock_timer"] = 0
                if not valid_position(get_shape_cells(next_idx, 0), state["pos_x"], 0, locked):
                    game_over = True
                    play("gameover")
                    if state["score"] > high_score:
                        high_score = state["score"]
                        save_high_score(high_score)

        # Draw
        screen.fill(BG)
        draw_play_area(screen)
        grid = create_grid(locked)
        draw_grid(screen, grid)
        ghost_y = get_ghost_y(shape_matrix, pos_x, pos_y, locked)
        draw_piece(screen, shape_matrix, pos_x, ghost_y, color, ghost=True)
        draw_piece(screen, shape_matrix, pos_x, pos_y, color)
        draw_sidebar(screen, next_idx, hold_idx, state["score"], high_score, state["level"], state["lines_cleared_total"])
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
