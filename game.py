import pygame
import random
import sqlite3
from stadtnamen import STADTNAMEN

TILE_SIZE = 64
SIDEBAR_WIDTH = 240
TOPBAR_HEIGHT = 36

# Terrain types
WIESE  = "wiese"
WALD   = "wald"
BERGE  = "berge"
HUEGEL = "huegel"
SEE    = "see"
SUMPF  = "sumpf"
WUESTE = "wueste"

GELAENDE_NAME = {
    WIESE:  "Wiese",
    WALD:   "Wald",
    BERGE:  "Berge",
    HUEGEL: "Hügel",
    SEE:    "See",
    SUMPF:  "Sumpf",
    WUESTE: "Wüste",
}

GELAENDE_TYPEN      = [WIESE, WALD, HUEGEL, BERGE, SEE, SUMPF, WUESTE]
GELAENDE_GEWICHTE   = [30,    30,   10,     10,    10,  5,     5]

ROWS = 12
COLS = 12

def erzeuge_karte():
    return [
        random.choices(GELAENDE_TYPEN, weights=GELAENDE_GEWICHTE, k=COLS)
        for _ in range(ROWS)
    ]

DB_PFAD = "spiel.db"

def speichere_karte(karte, staedte):
    speichere_staedte(staedte)
    with sqlite3.connect(DB_PFAD) as con:
        con.execute("CREATE TABLE IF NOT EXISTS karte (row INTEGER, col INTEGER, gelaende TEXT)")
        con.execute("DELETE FROM karte")
        con.executemany(
            "INSERT INTO karte (row, col, gelaende) VALUES (?, ?, ?)",
            [(r, c, karte[r][c]) for r in range(ROWS) for c in range(COLS)],
        )

def lade_karte_aus_db():
    try:
        with sqlite3.connect(DB_PFAD) as con:
            rows = con.execute("SELECT row, col, gelaende FROM karte ORDER BY row, col").fetchall()
        if not rows:
            return None
        karte = [[None] * COLS for _ in range(ROWS)]
        for r, c, g in rows:
            karte[r][c] = g
        return karte
    except sqlite3.OperationalError:
        return None

def erzeuge_staedte(anzahl=8):
    positionen = set()
    while len(positionen) < anzahl:
        positionen.add((random.randrange(ROWS), random.randrange(COLS)))
    namen = random.sample(STADTNAMEN, anzahl)
    return {pos: name for pos, name in zip(positionen, namen)}

def speichere_staedte(staedte):
    with sqlite3.connect(DB_PFAD) as con:
        con.execute("CREATE TABLE IF NOT EXISTS staedte (row INTEGER, col INTEGER, name TEXT)")
        con.execute("DELETE FROM staedte")
        con.executemany(
            "INSERT INTO staedte (row, col, name) VALUES (?, ?, ?)",
            [(r, c, name) for (r, c), name in staedte.items()],
        )

def lade_staedte_aus_db():
    try:
        with sqlite3.connect(DB_PFAD) as con:
            rows = con.execute("SELECT row, col, name FROM staedte").fetchall()
        return {(r, c): name for r, c, name in rows} if rows else None
    except sqlite3.OperationalError:
        return None

gespeicherte_karte = lade_karte_aus_db()
if gespeicherte_karte:
    KARTE = gespeicherte_karte
    STAEDTE = lade_staedte_aus_db() or erzeuge_staedte()
else:
    KARTE = erzeuge_karte()
    STAEDTE = erzeuge_staedte()

MAP_WIDTH  = COLS * TILE_SIZE
MAP_HEIGHT = ROWS * TILE_SIZE


def lade_tiles():
    return {
        WIESE:  pygame.image.load("assets/tile_grass.png").convert(),
        WALD:   pygame.image.load("assets/tile_wood.png").convert(),
        BERGE:  pygame.image.load("assets/tile_mountain.png").convert(),
        HUEGEL: pygame.image.load("assets/tile_hills.png").convert(),
        SEE:    pygame.image.load("assets/tile_lake.png").convert(),
        SUMPF:  pygame.image.load("assets/tile_swamp.png").convert(),
        WUESTE: pygame.image.load("assets/tile_desert.png").convert(),
    }


def zeichne_topbar(screen, font, zug):
    topbar_rect = pygame.Rect(0, 0, MAP_WIDTH + SIDEBAR_WIDTH, TOPBAR_HEIGHT)
    pygame.draw.rect(screen, (20, 20, 20), topbar_rect)
    pygame.draw.line(screen, (80, 80, 80), (0, TOPBAR_HEIGHT - 1), (MAP_WIDTH + SIDEBAR_WIDTH, TOPBAR_HEIGHT - 1), 1)
    text = font.render(f"Zug {zug}", True, (220, 220, 220))
    screen.blit(text, (12, (TOPBAR_HEIGHT - text.get_height()) // 2))

    btn_h = TOPBAR_HEIGHT - 8
    btn_y = 4

    beenden_text = font.render("Spiel beenden", True, (220, 220, 220))
    beenden_w = beenden_text.get_width() + 20
    beenden_x = MAP_WIDTH + SIDEBAR_WIDTH - beenden_w - 8
    beenden_rect = pygame.Rect(beenden_x, btn_y, beenden_w, btn_h)
    pygame.draw.rect(screen, (100, 40, 40), beenden_rect, border_radius=4)
    pygame.draw.rect(screen, (160, 80, 80), beenden_rect, 1, border_radius=4)
    screen.blit(beenden_text, (beenden_x + 10, btn_y + (btn_h - beenden_text.get_height()) // 2))

    naechster_text = font.render("Nächster Spielzug", True, (220, 220, 220))
    naechster_w = naechster_text.get_width() + 20
    naechster_x = beenden_x - naechster_w - 8
    naechster_rect = pygame.Rect(naechster_x, btn_y, naechster_w, btn_h)
    pygame.draw.rect(screen, (60, 60, 100), naechster_rect, border_radius=4)
    pygame.draw.rect(screen, (100, 100, 160), naechster_rect, 1, border_radius=4)
    screen.blit(naechster_text, (naechster_x + 10, btn_y + (btn_h - naechster_text.get_height()) // 2))

    return naechster_rect, beenden_rect


def zeichne_karte(screen, tiles, auswahl, staedte):
    for row in range(ROWS):
        for col in range(COLS):
            gelaende = KARTE[row][col]
            x = col * TILE_SIZE
            y = TOPBAR_HEIGHT + row * TILE_SIZE
            screen.blit(tiles[gelaende], (x, y))

    for (sr, sc) in staedte:
        cx = sc * TILE_SIZE + TILE_SIZE // 4
        cy = TOPBAR_HEIGHT + sr * TILE_SIZE + 3 * TILE_SIZE // 4
        pygame.draw.circle(screen, (200, 0, 0), (cx, cy), 10)
        pygame.draw.circle(screen, (255, 80, 80), (cx, cy), 10, 2)

    if auswahl:
        col, row = auswahl
        rect = pygame.Rect(col * TILE_SIZE, TOPBAR_HEIGHT + row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, (255, 255, 0), rect, 3)


def zeichne_sidebar(screen, font, auswahl, staedte):
    sidebar_rect = pygame.Rect(MAP_WIDTH, TOPBAR_HEIGHT, SIDEBAR_WIDTH, MAP_HEIGHT)
    pygame.draw.rect(screen, (30, 30, 30), sidebar_rect)
    pygame.draw.line(screen, (80, 80, 80), (MAP_WIDTH, TOPBAR_HEIGHT), (MAP_WIDTH, TOPBAR_HEIGHT + MAP_HEIGHT), 2)

    if auswahl is None:
        text = font.render("Kein Feld gewählt", True, (160, 160, 160))
        screen.blit(text, (MAP_WIDTH + 16, TOPBAR_HEIGHT + 20))
        return

    col, row = auswahl
    gelaende = KARTE[row][col]

    titel = font.render("Feld-Info", True, (200, 200, 200))
    screen.blit(titel, (MAP_WIDTH + 16, TOPBAR_HEIGHT + 16))

    pygame.draw.line(screen, (80, 80, 80),
                     (MAP_WIDTH + 16, TOPBAR_HEIGHT + 44),
                     (MAP_WIDTH + SIDEBAR_WIDTH - 16, TOPBAR_HEIGHT + 44), 1)

    name_surface = font.render(GELAENDE_NAME[gelaende], True, (255, 255, 255))
    screen.blit(name_surface, (MAP_WIDTH + 16, TOPBAR_HEIGHT + 56))

    pos_surface = font.render(f"Spalte {col + 1}, Zeile {row + 1}", True, (160, 160, 160))
    screen.blit(pos_surface, (MAP_WIDTH + 16, TOPBAR_HEIGHT + 84))

    if (row, col) in staedte:
        stadt_surface = font.render(staedte[(row, col)], True, (220, 100, 100))
        screen.blit(stadt_surface, (MAP_WIDTH + 16, TOPBAR_HEIGHT + 112))


def main():
    pygame.init()
    screen = pygame.display.set_mode((MAP_WIDTH + SIDEBAR_WIDTH, TOPBAR_HEIGHT + MAP_HEIGHT))
    pygame.display.set_caption("Spiel")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 26)
    klein_font = pygame.font.SysFont(None, 18)

    tiles = lade_tiles()
    auswahl = None  # (col, row) des angeklickten Feldes
    zug = 1
    naechster_btn = pygame.Rect(0, 0, 0, 0)
    beenden_btn = pygame.Rect(0, 0, 0, 0)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                speichere_karte(KARTE, STAEDTE)
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if my < TOPBAR_HEIGHT:
                    if naechster_btn.collidepoint(mx, my):
                        zug += 1
                    elif beenden_btn.collidepoint(mx, my):
                        speichere_karte(KARTE, STAEDTE)
                        running = False
                elif mx < MAP_WIDTH:
                    col = mx // TILE_SIZE
                    row = (my - TOPBAR_HEIGHT) // TILE_SIZE
                    auswahl = (col, row)

        naechster_btn, beenden_btn = zeichne_topbar(screen, font, zug)
        zeichne_karte(screen, tiles, auswahl, STAEDTE)
        zeichne_sidebar(screen, font, auswahl, STAEDTE)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
