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

def speichere_gold(gold):
    with sqlite3.connect(DB_PFAD) as con:
        con.execute("CREATE TABLE IF NOT EXISTS spieler (id INTEGER PRIMARY KEY, gold INTEGER)")
        con.execute("INSERT OR REPLACE INTO spieler (id, gold) VALUES (1, ?)", (gold,))

def lade_gold_aus_db():
    try:
        with sqlite3.connect(DB_PFAD) as con:
            row = con.execute("SELECT gold FROM spieler WHERE id = 1").fetchone()
        return row[0] if row else None
    except sqlite3.OperationalError:
        return None

def speichere_einheiten(einheiten):
    with sqlite3.connect(DB_PFAD) as con:
        con.execute("CREATE TABLE IF NOT EXISTS einheiten (name TEXT, besitzer TEXT, row INTEGER, col INTEGER)")
        con.execute("DELETE FROM einheiten")
        con.executemany(
            "INSERT INTO einheiten (name, besitzer, row, col) VALUES (?, ?, ?, ?)",
            [(e["name"], e["besitzer"], e["row"], e["col"]) for e in einheiten],
        )

def lade_einheiten_aus_db():
    try:
        with sqlite3.connect(DB_PFAD) as con:
            rows = con.execute("SELECT name, besitzer, row, col FROM einheiten").fetchall()
        return [{"name": name, "besitzer": besitzer, "row": row, "col": col}
                for name, besitzer, row, col in rows]
    except sqlite3.OperationalError:
        return []

def speichere_rekrutierung(rekrutierung):
    with sqlite3.connect(DB_PFAD) as con:
        con.execute("CREATE TABLE IF NOT EXISTS rekrutierung (name TEXT, kosten INTEGER, row INTEGER, col INTEGER)")
        con.execute("DELETE FROM rekrutierung")
        if rekrutierung:
            con.execute("INSERT INTO rekrutierung (name, kosten, row, col) VALUES (?, ?, ?, ?)",
                        (rekrutierung["name"], rekrutierung["kosten"], rekrutierung["row"], rekrutierung["col"]))

def lade_rekrutierung_aus_db():
    try:
        with sqlite3.connect(DB_PFAD) as con:
            row = con.execute("SELECT name, kosten, row, col FROM rekrutierung").fetchone()
        return {"name": row[0], "kosten": row[1], "row": row[2], "col": row[3]} if row else None
    except sqlite3.OperationalError:
        return None

def speichere_karte(karte, staedte, gold, einheiten, rekrutierung):
    speichere_staedte(staedte)
    speichere_gold(gold)
    speichere_einheiten(einheiten)
    speichere_rekrutierung(rekrutierung)
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

BESITZER_SPIELER = "spieler"
BESITZER_KI      = "ki"
BESITZER_KEINER  = None

EINHEITEN = [
    {"name": "Späher",  "kosten": 1},
    {"name": "Kämpfer", "kosten": 3},
    {"name": "Ritter",  "kosten": 5},
]

def erzeuge_staedte(anzahl=8):
    positionen = list({
        (random.randrange(ROWS), random.randrange(COLS))
        for _ in range(anzahl * 10)
    })[:anzahl]
    while len(positionen) < anzahl:
        pos = (random.randrange(ROWS), random.randrange(COLS))
        if pos not in positionen:
            positionen.append(pos)
    namen = random.sample(STADTNAMEN, anzahl)
    spieler_pos = random.choice(positionen)
    return {
        pos: {
            "name": name,
            "produktion": random.randint(2, 12),
            "besitzer": BESITZER_SPIELER if pos == spieler_pos else BESITZER_KEINER,
        }
        for pos, name in zip(positionen, namen)
    }

def speichere_staedte(staedte):
    with sqlite3.connect(DB_PFAD) as con:
        con.execute("CREATE TABLE IF NOT EXISTS staedte (row INTEGER, col INTEGER, name TEXT, produktion INTEGER, besitzer TEXT)")
        con.execute("DELETE FROM staedte")
        con.executemany(
            "INSERT INTO staedte (row, col, name, produktion, besitzer) VALUES (?, ?, ?, ?, ?)",
            [(r, c, s["name"], s["produktion"], s["besitzer"]) for (r, c), s in staedte.items()],
        )

def lade_staedte_aus_db():
    try:
        with sqlite3.connect(DB_PFAD) as con:
            rows = con.execute("SELECT row, col, name, produktion, besitzer FROM staedte").fetchall()
        return {
            (r, c): {"name": name, "produktion": prod, "besitzer": besitzer or BESITZER_KEINER}
            for r, c, name, prod, besitzer in rows
        } if rows else None
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


def zeichne_topbar(screen, font, zug, gold):
    topbar_rect = pygame.Rect(0, 0, MAP_WIDTH + SIDEBAR_WIDTH, TOPBAR_HEIGHT)
    pygame.draw.rect(screen, (20, 20, 20), topbar_rect)
    pygame.draw.line(screen, (80, 80, 80), (0, TOPBAR_HEIGHT - 1), (MAP_WIDTH + SIDEBAR_WIDTH, TOPBAR_HEIGHT - 1), 1)
    text = font.render(f"Zug {zug}", True, (220, 220, 220))
    screen.blit(text, (12, (TOPBAR_HEIGHT - text.get_height()) // 2))
    gold_text = font.render(f"Gold: {gold}", True, (255, 215, 0))
    screen.blit(gold_text, (100, (TOPBAR_HEIGHT - gold_text.get_height()) // 2))

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


def benachbarte_felder(row, col):
    nachbarn = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, col + dc
            if 0 <= r < ROWS and 0 <= c < COLS:
                nachbarn.append((r, c))
    return nachbarn

EINHEIT_KUERZEL = {"Späher": "S", "Kämpfer": "K", "Ritter": "R"}
EINHEIT_FARBE   = {
    BESITZER_SPIELER: (60, 200, 60),
    BESITZER_KI:      (200, 60, 60),
    BESITZER_KEINER:  (160, 160, 160),
}

def zeichne_karte(screen, tiles, auswahl, staedte, einheiten, symbol_font,
                  beweg_modus=False, beweg_ursprung=None):
    for row in range(ROWS):
        for col in range(COLS):
            gelaende = KARTE[row][col]
            x = col * TILE_SIZE
            y = TOPBAR_HEIGHT + row * TILE_SIZE
            screen.blit(tiles[gelaende], (x, y))

    FARBE_BESITZER = {
        BESITZER_SPIELER: ((0, 180, 0),   (80, 255, 80)),
        BESITZER_KI:      ((180, 0, 0),   (255, 80, 80)),
        BESITZER_KEINER:  ((120, 120, 120), (200, 200, 200)),
    }
    for (sr, sc), stadt in staedte.items():
        cx = sc * TILE_SIZE + TILE_SIZE // 4
        cy = TOPBAR_HEIGHT + sr * TILE_SIZE + 3 * TILE_SIZE // 4
        farbe_innen, farbe_rand = FARBE_BESITZER[stadt["besitzer"]]
        pygame.draw.circle(screen, farbe_innen, (cx, cy), 10)
        pygame.draw.circle(screen, farbe_rand, (cx, cy), 10, 2)

    # Einheitensymbole: unteres rechtes Viertel
    SYM = 13  # Symbol-Breite/-Höhe
    GAP = 2
    einheiten_pro_feld = {}
    for e in einheiten:
        einheiten_pro_feld.setdefault((e["row"], e["col"]), []).append(e)
    for (er, ec), elist in einheiten_pro_feld.items():
        qx = ec * TILE_SIZE + TILE_SIZE // 2   # unteres rechtes Viertel: x-Start
        qy = TOPBAR_HEIGHT + er * TILE_SIZE + TILE_SIZE // 2
        for i, e in enumerate(elist[:4]):      # max. 4 Symbole
            sx = qx + (i % 2) * (SYM + GAP)
            sy = qy + (i // 2) * (SYM + GAP)
            farbe = EINHEIT_FARBE[e["besitzer"]]
            pygame.draw.rect(screen, farbe, pygame.Rect(sx, sy, SYM, SYM), border_radius=2)
            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(sx, sy, SYM, SYM), 1, border_radius=2)
            lbl = symbol_font.render(EINHEIT_KUERZEL.get(e["name"], "?"), True, (0, 0, 0))
            screen.blit(lbl, (sx + (SYM - lbl.get_width()) // 2, sy + (SYM - lbl.get_height()) // 2))
        if len(elist) > 4:
            mehr = symbol_font.render(f"+{len(elist)-4}", True, (255, 255, 255))
            screen.blit(mehr, (qx, qy + 2 * (SYM + GAP)))

    if beweg_modus and beweg_ursprung:
        ur, uc = beweg_ursprung
        for nr, nc in benachbarte_felder(ur, uc):
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill((0, 180, 255, 80))
            screen.blit(overlay, (nc * TILE_SIZE, TOPBAR_HEIGHT + nr * TILE_SIZE))
            pygame.draw.rect(screen, (0, 180, 255),
                             pygame.Rect(nc * TILE_SIZE, TOPBAR_HEIGHT + nr * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)

    if auswahl:
        col, row = auswahl
        rect = pygame.Rect(col * TILE_SIZE, TOPBAR_HEIGHT + row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, (255, 255, 0), rect, 3)


BESITZER_LABEL = {
    BESITZER_SPIELER: ("Spieler",       (80, 220, 80)),
    BESITZER_KI:      ("Computergegner",(220, 80, 80)),
    BESITZER_KEINER:  ("Keiner",        (160, 160, 160)),
}

def zeichne_sidebar(screen, font, auswahl, staedte, auswahl_einheit, rekrutierung, einheiten,
                    auswahl_einheit_auf_karte, beweg_modus):
    sidebar_rect = pygame.Rect(MAP_WIDTH, TOPBAR_HEIGHT, SIDEBAR_WIDTH, MAP_HEIGHT)
    pygame.draw.rect(screen, (30, 30, 30), sidebar_rect)
    pygame.draw.line(screen, (80, 80, 80), (MAP_WIDTH, TOPBAR_HEIGHT), (MAP_WIDTH, TOPBAR_HEIGHT + MAP_HEIGHT), 2)

    einheit_rects = []
    rekrutieren_rect = pygame.Rect(0, 0, 0, 0)
    einheit_auf_karte_rects = []  # list of (rect, einheiten_index)
    bewegen_rect = pygame.Rect(0, 0, 0, 0)

    if auswahl is None:
        text = font.render("Kein Feld gewählt", True, (160, 160, 160))
        screen.blit(text, (MAP_WIDTH + 16, TOPBAR_HEIGHT + 20))
        return einheit_rects, rekrutieren_rect, einheit_auf_karte_rects, bewegen_rect

    col, row = auswahl
    gelaende = KARTE[row][col]

    def sep(y):
        pygame.draw.line(screen, (80, 80, 80),
                         (MAP_WIDTH + 16, y), (MAP_WIDTH + SIDEBAR_WIDTH - 16, y), 1)

    y = TOPBAR_HEIGHT + 16
    screen.blit(font.render("Feld-Info", True, (200, 200, 200)), (MAP_WIDTH + 16, y))
    y += 28; sep(y); y += 12
    screen.blit(font.render(GELAENDE_NAME[gelaende], True, (255, 255, 255)), (MAP_WIDTH + 16, y))
    y += 28
    screen.blit(font.render(f"Spalte {col + 1}, Zeile {row + 1}", True, (160, 160, 160)), (MAP_WIDTH + 16, y))
    y += 28

    if (row, col) in staedte:
        stadt = staedte[(row, col)]
        sep(y); y += 12
        screen.blit(font.render(stadt["name"], True, (220, 100, 100)), (MAP_WIDTH + 16, y))
        y += 28
        screen.blit(font.render(f"Produktion: {stadt['produktion']} Gold", True, (255, 215, 0)), (MAP_WIDTH + 16, y))
        y += 28
        lbl, farbe = BESITZER_LABEL[stadt["besitzer"]]
        screen.blit(font.render(f"Besitzer: {lbl}", True, farbe), (MAP_WIDTH + 16, y))
        y += 28

        if stadt["besitzer"] == BESITZER_SPIELER:
            sep(y); y += 12
            screen.blit(font.render("Rekrutierung", True, (200, 200, 200)), (MAP_WIDTH + 16, y))
            y += 28; sep(y); y += 12
            for i, einheit in enumerate(EINHEITEN):
                erect = pygame.Rect(MAP_WIDTH + 8, y - 2, SIDEBAR_WIDTH - 16, 24)
                einheit_rects.append(erect)
                if auswahl_einheit == i:
                    pygame.draw.rect(screen, (60, 60, 80), erect, border_radius=3)
                screen.blit(font.render(f"{einheit['name']}  {einheit['kosten']} Gold", True, (220, 220, 220)), (MAP_WIDTH + 16, y))
                y += 28
            rek_text_str = f"In Arbeit: {rekrutierung['name']}" if rekrutierung else "Rekrutieren"
            rek_farbe    = (60, 80, 60) if rekrutierung else (60, 60, 100)
            rek_text = font.render(rek_text_str, True, (220, 220, 220))
            rekrutieren_rect = pygame.Rect(MAP_WIDTH + 16, y, rek_text.get_width() + 20, 26)
            pygame.draw.rect(screen, rek_farbe, rekrutieren_rect, border_radius=4)
            pygame.draw.rect(screen, (100, 100, 160), rekrutieren_rect, 1, border_radius=4)
            screen.blit(rek_text, (MAP_WIDTH + 26, y + (26 - rek_text.get_height()) // 2))
            y += 38

    # Einheiten auf diesem Feld
    sep(y); y += 12
    screen.blit(font.render("Einheiten", True, (200, 200, 200)), (MAP_WIDTH + 16, y))
    y += 28; sep(y); y += 12
    einheiten_hier = [(i, e) for i, e in enumerate(einheiten) if e["row"] == row and e["col"] == col]
    if einheiten_hier:
        for idx, e in einheiten_hier:
            erect = pygame.Rect(MAP_WIDTH + 8, y - 2, SIDEBAR_WIDTH - 16, 22)
            einheit_auf_karte_rects.append((erect, idx))
            if auswahl_einheit_auf_karte == idx:
                pygame.draw.rect(screen, (50, 70, 50), erect, border_radius=3)
            lbl, farbe = BESITZER_LABEL[e["besitzer"]]
            hat_auftrag = "bewegen_ziel" in e
            name_text = f"{e['name']}  [{lbl[0]}]" + (" →" if hat_auftrag else "")
            screen.blit(font.render(name_text, True, farbe), (MAP_WIDTH + 16, y))
            y += 24
        # Bewegen-Button für ausgewählte Spieler-Einheit
        if auswahl_einheit_auf_karte is not None:
            sel = einheiten[auswahl_einheit_auf_karte]
            if sel["besitzer"] == BESITZER_SPIELER and sel["row"] == row and sel["col"] == col:
                bew_str = "Bewegen abbrechen" if beweg_modus else "Bewegen"
                bew_farbe = (80, 60, 20) if beweg_modus else (40, 80, 40)
                bew_text = font.render(bew_str, True, (220, 220, 220))
                bewegen_rect = pygame.Rect(MAP_WIDTH + 16, y, bew_text.get_width() + 20, 26)
                pygame.draw.rect(screen, bew_farbe, bewegen_rect, border_radius=4)
                pygame.draw.rect(screen, (100, 160, 100), bewegen_rect, 1, border_radius=4)
                screen.blit(bew_text, (MAP_WIDTH + 26, y + (26 - bew_text.get_height()) // 2))
                y += 34
    else:
        screen.blit(font.render("Keine", True, (100, 100, 100)), (MAP_WIDTH + 16, y))

    return einheit_rects, rekrutieren_rect, einheit_auf_karte_rects, bewegen_rect


def main():
    pygame.init()
    screen = pygame.display.set_mode((MAP_WIDTH + SIDEBAR_WIDTH, TOPBAR_HEIGHT + MAP_HEIGHT))
    pygame.display.set_caption("Spiel")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 26)
    klein_font = pygame.font.SysFont(None, 18)
    symbol_font = pygame.font.SysFont(None, 14)

    tiles = lade_tiles()
    auswahl = None  # (col, row) des angeklickten Feldes
    auswahl_einheit = None           # Index in EINHEITEN (Rekrutierung)
    auswahl_einheit_auf_karte = None # Index in einheiten-Liste
    beweg_modus = False
    rekrutierung = lade_rekrutierung_aus_db() if gespeicherte_karte else None
    einheiten = lade_einheiten_aus_db() if gespeicherte_karte else []
    zug = 1
    gold = lade_gold_aus_db() if lade_karte_aus_db() else 10
    naechster_btn = pygame.Rect(0, 0, 0, 0)
    beenden_btn = pygame.Rect(0, 0, 0, 0)
    einheit_rects = []
    rekrutieren_rect = pygame.Rect(0, 0, 0, 0)
    einheit_auf_karte_rects = []
    bewegen_rect = pygame.Rect(0, 0, 0, 0)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                speichere_karte(KARTE, STAEDTE, gold, einheiten, rekrutierung)
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if my < TOPBAR_HEIGHT:
                    if naechster_btn.collidepoint(mx, my):
                        zug += 1
                        gold += sum(s["produktion"] for s in STAEDTE.values() if s["besitzer"] == BESITZER_SPIELER)
                        if rekrutierung:
                            einheiten.append({
                                "name": rekrutierung["name"],
                                "besitzer": BESITZER_SPIELER,
                                "row": rekrutierung["row"],
                                "col": rekrutierung["col"],
                            })
                            rekrutierung = None
                            auswahl_einheit = None
                        # Bewegungsaufträge ausführen
                        for e in einheiten:
                            if "bewegen_ziel" in e:
                                e["row"], e["col"] = e.pop("bewegen_ziel")
                        beweg_modus = False
                    elif beenden_btn.collidepoint(mx, my):
                        speichere_karte(KARTE, STAEDTE, gold, einheiten, rekrutierung)
                        running = False
                elif mx >= MAP_WIDTH:
                    for i, erect in enumerate(einheit_rects):
                        if erect.collidepoint(mx, my):
                            auswahl_einheit = i
                            break
                    if rekrutieren_rect.collidepoint(mx, my) and not rekrutierung:
                        if auswahl_einheit is not None and auswahl is not None:
                            einheit = EINHEITEN[auswahl_einheit]
                            if gold >= einheit["kosten"]:
                                gold -= einheit["kosten"]
                                rekrutierung = {**einheit, "row": auswahl[1], "col": auswahl[0]}
                    for erect, eidx in einheit_auf_karte_rects:
                        if erect.collidepoint(mx, my):
                            auswahl_einheit_auf_karte = eidx
                            beweg_modus = False
                            break
                    if bewegen_rect.collidepoint(mx, my):
                        beweg_modus = not beweg_modus
                elif mx < MAP_WIDTH:
                    col = mx // TILE_SIZE
                    row = (my - TOPBAR_HEIGHT) // TILE_SIZE
                    if beweg_modus and auswahl_einheit_auf_karte is not None:
                        e = einheiten[auswahl_einheit_auf_karte]
                        if (row, col) in benachbarte_felder(e["row"], e["col"]):
                            e["bewegen_ziel"] = (row, col)
                            beweg_modus = False
                    else:
                        if (col, row) != auswahl:
                            auswahl_einheit = None
                            auswahl_einheit_auf_karte = None
                            beweg_modus = False
                        auswahl = (col, row)

        naechster_btn, beenden_btn = zeichne_topbar(screen, font, zug, gold)
        beweg_ursprung = None
        if beweg_modus and auswahl_einheit_auf_karte is not None:
            e = einheiten[auswahl_einheit_auf_karte]
            beweg_ursprung = (e["row"], e["col"])
        zeichne_karte(screen, tiles, auswahl, STAEDTE, einheiten, symbol_font, beweg_modus, beweg_ursprung)
        einheit_rects, rekrutieren_rect, einheit_auf_karte_rects, bewegen_rect = zeichne_sidebar(
            screen, font, auswahl, STAEDTE, auswahl_einheit, rekrutierung, einheiten,
            auswahl_einheit_auf_karte, beweg_modus)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
