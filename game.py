"""
Return to Castle Wolfenstein  –  Python Tribute  (RtCW, 2001 Gray Matter / Activision)
════════════════════════════════════════════════════════════════════════════════════════
B.J. Blazkowicz – US OSA agent – escapes Castle Wolfenstein and fights through
catacombs, a village, and Deathshead's lab to destroy Operation Resurrection.

ENEMIES (from RtCW):
  Wehrmacht Guard  –  standard soldier, Luger
  SS Guard         –  tougher, MP40
  Elite / BlackGuard – FG42, very accurate
  Zombie           –  undead, slow but tanky, spawns in catacombs
  Loper            –  fast demon-creature, melee
  Übersoldat       –  armoured supersoldier, boss-tier
  Heinrich I       –  final supernatural boss

WEAPONS (RtCW-inspired):
  Knife  ·  Luger P08  ·  MP40  ·  Sten  ·  FG42  ·  Panzerfaust
  Flamethrower  ·  Venom Gun (minigun)  ·  Tesla Cannon

CONTROLS
  W/S/↑/↓    Move forward / back      A/D        Strafe
  ←/→        Turn                     SPACE      Shoot (hold for auto)
  G          Throw grenade            TAB        Next weapon
  1-9        Direct weapon select     M          Toggle minimap
  P          Pause                    ESC        Menu / quit
"""

import pygame, math, sys, random, array as _arr

# ══════════════════════════════════════════════════════════════════════════════
#  SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
SW, SH   = 1024, 630
VIEW_H   = SH - 115          # 3-D area
HUD_Y    = VIEW_H
HUD_H    = SH - VIEW_H
RAYS     = SW // 2           # half-width rendered, upscaled ×2
MAP_W    = MAP_H = 26
FOV      = math.pi / 3
HFOV     = FOV / 2
MDIST    = 26
SPD      = 0.058
ROT      = 0.038
CR       = 0.28              # collision radius
MM_CS    = 6                 # minimap cell size

# ── palette ──────────────────────────────────────────────────────────────────
BLACK  = (  0,   0,   0)
WHITE  = (255, 255, 255)
RED    = (210,  35,  35)
YELLOW = (215, 195,  45)
DGRAY  = ( 45,  45,  45)

# Ceiling gradient  top → horizon
CTOP = ( 14,  14,  18)
CMID = ( 22,  22,  28)
# Floor gradient  horizon → bottom
FMID = ( 18,  14,  10)
FBOT = ( 40,  32,  22)

HUD_BG  = ( 12,   8,   4)
HUD_LN  = ( 70,  50,  18)

# Wall tile colours  {id: (NS-face, EW-face)}
#   1 stone  2 brick  3 wood  4 catacomb  5 lab metal  6 bunker  7 dark stone
WCOLORS = {
    1: ((105, 100,  92), ( 68,  64,  58)),   # grey stone
    2: ((115,  58,  50), ( 78,  38,  32)),   # dark red brick
    3: (( 82,  62,  38), ( 55,  42,  25)),   # wood planks
    4: (( 55,  70,  62), ( 35,  48,  42)),   # catacomb stone
    5: (( 72,  88,  92), ( 48,  60,  64)),   # lab metal
    6: (( 50,  55,  50), ( 32,  36,  32)),   # bunker concrete
    7: (( 38,  30,  28), ( 24,  18,  16)),   # black stone
}

# ══════════════════════════════════════════════════════════════════════════════
#  MAP  (Castle → Catacombs → Bunker)
#  0 = open  1-7 = wall types
# ══════════════════════════════════════════════════════════════════════════════
GAME_MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,2,2,2,2,2,0,0,0,0,1],
    [1,0,0,1,1,0,1,0,0,1,1,0,0,0,0,0,2,0,0,0,2,0,0,0,0,1],
    [1,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,2,0,5,0,2,0,0,7,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,2,0,0,7,0,1],
    [1,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,2,2,0,2,2,0,0,7,0,1],
    [1,0,0,1,1,0,1,0,0,1,1,0,0,1,0,0,0,0,0,0,0,0,0,7,7,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,0,1,1,1,0,1,1,1,0,1,1,0,0,4,4,4,0,0,4,4,4,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,4,0,1],
    [1,0,0,3,3,3,0,0,3,3,3,0,0,0,0,0,4,0,0,0,0,0,0,4,0,1],
    [1,0,0,3,0,3,0,0,3,0,3,0,0,0,0,0,4,0,7,7,0,0,0,4,0,1],
    [1,0,0,3,0,0,0,0,0,0,3,0,0,0,0,0,0,0,7,7,0,0,0,0,0,1],
    [1,0,0,3,0,3,0,0,3,0,3,0,0,0,0,0,4,0,0,0,0,0,0,4,0,1],
    [1,0,0,3,3,3,0,0,3,3,3,0,0,0,0,0,4,4,4,4,4,4,4,4,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,6,6,6,0,0,0,0,6,6,6,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,6,0,6,0,0,0,0,6,0,6,0,0,5,5,5,5,0,5,5,5,5,0,0,1],
    [1,0,6,0,0,0,0,0,0,0,0,6,0,0,5,0,0,5,0,5,0,0,5,0,0,1],
    [1,0,6,0,6,0,0,0,0,6,0,6,0,0,5,0,5,0,0,0,5,0,5,0,0,1],
    [1,0,6,6,6,0,0,0,0,6,6,6,0,0,5,5,5,0,0,0,5,5,5,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

# ══════════════════════════════════════════════════════════════════════════════
#  WEAPONS
# name, dmg_lo, dmg_hi, range, cooldown, uses_ammo, ammo_key, autofire, splash
# ══════════════════════════════════════════════════════════════════════════════
WPN = {
    "knife":   ("KNIFE",        4, 14,  1.8, 22, False, None,       False, False),
    "luger":   ("LUGER P08",    7, 20, 22,   20, True,  "pistol",   False, False),
    "mp40":    ("MP40",         6, 17, 22,    8, True,  "smg",      True,  False),
    "sten":    ("STEN",         5, 15, 22,    9, True,  "smg",      True,  False),
    "fg42":    ("FG 42",        9, 25, 24,   14, True,  "rifle",    True,  False),
    "panzerfaust":("PANZERFAUST",30,55,18,   60, True,  "rockets",  False, True ),
    "flame":   ("FLAMETHROWER",10, 22,  4,    4, True,  "fuel",     True,  False),
    "venom":   ("VENOM GUN",   12, 28, 22,    3, True,  "venom",    True,  False),
    "tesla":   ("TESLA CANNON",18, 40, 16,   18, True,  "tesla",    False, False),
}
WPN_ORDER = ["knife","luger","mp40","sten","fg42","panzerfaust","flame","venom","tesla"]

# ══════════════════════════════════════════════════════════════════════════════
#  ENEMY DEFINITIONS
# hp, spd, melee_dmg, ranged_dmg, detect_r, score, col_idle, col_alert, ranged_range
# ══════════════════════════════════════════════════════════════════════════════
EDEFS = {
    # NAZI SOLDIERS ────────────────────────────────────────────────────────────
    "guard":      ( 5, 0.022, (3,10),  (5,15), 8,   100, (145,130, 90), (200, 75, 75),  8.0),
    "ss":         ( 8, 0.026, (5,14),  (7,20), 9,   250, ( 80, 95,160), (100, 45,185),  9.0),
    "elite":      (10, 0.030, (7,18), (10,28),10,   500, (180,175,160), (230,100, 50), 12.0),
    # UNDEAD ───────────────────────────────────────────────────────────────────
    "zombie":     (18, 0.014, (8,20),  None,   6,   150, ( 42, 65, 42), ( 60, 90, 55),  0.0),
    "loper":      ( 6, 0.055, (10,24), None,   9,   300, ( 65, 30, 75), (100, 40,115),  0.0),
    # SUPER SOLDIERS ───────────────────────────────────────────────────────────
    "ubersoldaten":(45, 0.018,(15,35),(18,42),14,  2000, ( 60, 75, 95), ( 80, 40,120), 14.0),
    # BOSS ─────────────────────────────────────────────────────────────────────
    "heinrich":   (80, 0.016,(20,50),(25,60),20, 10000, ( 90, 70, 50), (130, 40, 30), 18.0),
}

SPAWNS = [
    ("guard",       2.5,  6.5),
    ("guard",       8.5,  2.5),
    ("ss",         12.5,  2.5),
    ("guard",       5.5, 12.5),
    ("zombie",     17.5,  3.5),
    ("zombie",     22.5,  4.5),
    ("loper",      10.5, 13.5),
    ("ss",         19.5, 10.5),
    ("elite",       3.5, 19.5),
    ("elite",      11.5, 20.5),
    ("zombie",     17.5, 20.5),
    ("loper",      21.5, 18.5),
    ("ubersoldaten",20.5,  1.5),
    ("guard",       2.5, 22.5),
    ("ss",          8.5, 22.5),
    ("heinrich",   24.5, 23.5),
]

PICKUPS = [
    # x,    y,    type
    ( 4.5,  4.5, "health"),
    (10.5,  5.5, "armor"),
    ( 6.5, 15.5, "health"),
    (18.5,  7.5, "ammo_smg"),
    (12.5, 12.5, "ammo_rifle"),
    ( 3.5, 22.5, "health"),
    (14.5, 22.5, "armor"),
    (20.5, 22.5, "ammo_venom"),
    ( 6.5,  9.5, "ammo_pistol"),
    (22.5, 12.5, "ammo_rockets"),
    (15.5, 14.5, "weapon_sten"),
    (23.5, 19.5, "weapon_fg42"),
    (19.5, 23.5, "weapon_venom"),
    (23.5, 23.5, "weapon_tesla"),
    ( 9.5, 19.5, "food"),
    (16.5,  9.5, "food"),
]

PICKUP_COL = {
    "health":       ( 45, 210,  45),
    "armor":        ( 45, 120, 210),
    "food":         (200, 160,  45),
    "ammo_smg":     (210, 205,  50),
    "ammo_rifle":   (200, 180,  40),
    "ammo_pistol":  (195, 200,  60),
    "ammo_rockets": (215,  90,  50),
    "ammo_venom":   (180, 100, 210),
    "weapon_sten":  (160, 160, 100),
    "weapon_fg42":  (100, 160, 100),
    "weapon_venom": (120, 60,  200),
    "weapon_tesla": ( 80, 160, 230),
}

PICKUP_LABEL = {
    "health":      "HEALTH PACK",
    "armor":       "ARMOR",
    "food":        "FOOD +10 HP",
    "ammo_smg":    "SMG AMMO",
    "ammo_rifle":  "RIFLE AMMO",
    "ammo_pistol": "PISTOL AMMO",
    "ammo_rockets":"ROCKETS",
    "ammo_venom":  "VENOM CELLS",
    "weapon_sten": "STEN SMG",
    "weapon_fg42": "FG 42 RIFLE",
    "weapon_venom":"VENOM GUN",
    "weapon_tesla":"TESLA CANNON",
}

# ══════════════════════════════════════════════════════════════════════════════
#  SOUND
# ══════════════════════════════════════════════════════════════════════════════
def _snd(freq, ms, vol=0.42, shape="sq"):
    try:
        sr = 22050; n = int(sr*ms/1000)
        buf = _arr.array("h")
        amp = int(32767*vol)
        for i in range(n):
            t   = i/sr
            env = 1.0 - i/n
            if   shape=="sq":   v = amp if int(t*freq*2)%2==0 else -amp
            elif shape=="nz":   v = random.randint(-amp,amp)
            elif shape=="fall": v = int(amp*math.sin(2*math.pi*freq*(1-i/n*.8)*t)*env)
            elif shape=="blip": v = int(amp*math.sin(2*math.pi*freq*t)*env)
            elif shape=="low":  v = int(amp*math.sin(2*math.pi*freq*t*env*.4)*env)
            else:               v = int(amp*math.sin(2*math.pi*freq*t))
        buf.append(v)
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

# ══════════════════════════════════════════════════════════════════════════════
#  PARTICLE  (for flames, sparks, explosions)
# ══════════════════════════════════════════════════════════════════════════════
class Particle:
    def __init__(self, x, y, vx, vy, col, life, size=3):
        self.x, self.y     = x, y
        self.vx, self.vy   = vx, vy
        self.col   = col
        self.life  = life
        self.maxl  = life
        self.size  = size
    def update(self):
        self.x  += self.vx; self.y  += self.vy
        self.vy += 0.04   # gravity
        self.life -= 1
        return self.life > 0
    def alpha_col(self):
        f = self.life / self.maxl
        return tuple(int(c*f) for c in self.col)

# ══════════════════════════════════════════════════════════════════════════════
#  GRENADE
# ══════════════════════════════════════════════════════════════════════════════
class Grenade:
    def __init__(self, x, y, vx, vy):
        self.x, self.y   = x, y
        self.vx, self.vy = vx, vy
        self.fuse        = 120   # frames
        self.dist        = 0.0
    def update(self, gmap):
        nx = self.x + self.vx
        ny = self.y + self.vy
        if 0 < nx < MAP_W and 0 < ny < MAP_H and gmap[int(ny)][int(nx)] == 0:
            self.x, self.y = nx, ny
        else:
            self.vx *= -0.5; self.vy *= -0.5
        self.fuse -= 1
        return self.fuse > 0

# ══════════════════════════════════════════════════════════════════════════════
#  PLAYER
# ══════════════════════════════════════════════════════════════════════════════
class Player:
    def __init__(self):
        self.x, self.y = 1.5, 1.5
        self.angle     = 0.25
        self.hp        = 100
        self.armor     = 0
        self.ammo      = {
            "pistol": 30, "smg": 60, "rifle": 20,
            "rockets": 4, "fuel": 40, "venom": 0, "tesla": 8
        }
        self.score     = 0
        self.kills     = 0
        self.weapon    = "luger"
        self.unlocked  = {"knife", "luger", "mp40"}

        self.shoot_cd  = 0
        self.pain_t    = 0
        self.muzzle_t  = 0
        self.walk_t    = 0.0
        self.moving    = False
        self.grenade_cd= 0

    def _free(self, gmap, nx, ny):
        for dx in (-CR, CR):
            for dy in (-CR, CR):
                cx,cy = nx+dx, ny+dy
                if not (0<cx<MAP_W and 0<cy<MAP_H): return False
                if gmap[int(cy)][int(cx)] != 0: return False
        return True

    def move(self, gmap):
        k  = pygame.key.get_pressed()
        ca = math.cos(self.angle); sa = math.sin(self.angle)
        mv = False

        def slide(nx, ny):
            nonlocal mv
            if self._free(gmap, nx, ny):   self.x,self.y=nx,ny; mv=True
            elif self._free(gmap, nx, self.y): self.x=nx;        mv=True
            elif self._free(gmap, self.x, ny): self.y=ny;        mv=True

        if k[pygame.K_w] or k[pygame.K_UP]:
            slide(self.x+ca*SPD, self.y+sa*SPD)
        if k[pygame.K_s] or k[pygame.K_DOWN]:
            slide(self.x-ca*SPD, self.y-sa*SPD)
        if k[pygame.K_a]:
            slide(self.x+math.cos(self.angle-math.pi/2)*SPD,
                  self.y+math.sin(self.angle-math.pi/2)*SPD)
        if k[pygame.K_d]:
            slide(self.x+math.cos(self.angle+math.pi/2)*SPD,
                  self.y+math.sin(self.angle+math.pi/2)*SPD)
        if k[pygame.K_LEFT]:  self.angle = (self.angle-ROT)%(2*math.pi)
        if k[pygame.K_RIGHT]: self.angle = (self.angle+ROT)%(2*math.pi)

        self.moving = mv
        if mv: self.walk_t += 0.13
        for attr in ("shoot_cd","pain_t","muzzle_t","grenade_cd"):
            v = getattr(self, attr)
            if v > 0: setattr(self, attr, v-1)

    def can_shoot(self):
        if self.shoot_cd > 0: return False
        w = WPN[self.weapon]
        if w[5]:   # uses ammo
            key = w[6]
            if key and self.ammo.get(key, 0) <= 0: return False
        return True

    def do_shoot(self):
        if not self.can_shoot(): return False
        w = WPN[self.weapon]
        if w[5]:
            key = w[6]
            if key: self.ammo[key] = max(0, self.ammo[key]-1)
        self.shoot_cd = w[4]
        self.muzzle_t = min(w[4], 10)
        return True

    def take_hit(self, dmg):
        absorbed = min(self.armor, dmg//2)
        self.armor = max(0, self.armor - absorbed)
        self.hp    = max(0, self.hp - (dmg - absorbed))
        self.pain_t = 32

    def throw_grenade(self):
        if self.grenade_cd > 0: return None
        self.grenade_cd = 90
        vx =  math.cos(self.angle)*0.09
        vy =  math.sin(self.angle)*0.09
        return Grenade(self.x + vx*2, self.y + vy*2, vx, vy)

# ══════════════════════════════════════════════════════════════════════════════
#  ENEMY
# ══════════════════════════════════════════════════════════════════════════════
class Enemy:
    def __init__(self, etype, x, y):
        self.type = etype
        self.x, self.y = x, y
        d = EDEFS[etype]
        self.hp         = d[0]
        self.spd        = d[1]
        self.melee_dmg  = d[2]
        self.range_dmg  = d[3]
        self.detect_r   = d[4]
        self.score_val  = d[5]
        self.col_idle   = d[6]
        self.col_alert  = d[7]
        self.range_r    = d[8]

        self.alive      = True
        self.state      = "idle"
        self.patrol_ang = random.uniform(0, 2*math.pi)
        self.patrol_t   = 0
        self.melee_cd   = 0
        self.range_cd   = random.randint(20, 80)
        self.pain_t     = 0
        self.dist       = 999.0
        self.anim       = 0
        self.anim_t     = 0

    def update(self, player, gmap):
        if not self.alive: return None
        dx = player.x - self.x
        dy = player.y - self.y
        self.dist = math.hypot(dx, dy)

        self.anim_t += 1
        if self.anim_t >= 10: self.anim_t = 0; self.anim ^= 1

        if self.pain_t > 0:
            self.pain_t -= 1
            if self.melee_cd > 0: self.melee_cd -= 1
            if self.range_cd > 0: self.range_cd -= 1
            return None

        # state machine
        if self.dist < self.detect_r: self.state = "chase"
        elif self.state == "chase" and self.dist > self.detect_r+7: self.state = "idle"

        result = None
        if self.state == "chase":
            ang = math.atan2(dy, dx)
            nx  = self.x + math.cos(ang)*self.spd
            ny  = self.y + math.sin(ang)*self.spd
            if 0<nx<MAP_W and 0<ny<MAP_H and gmap[int(ny)][int(nx)]==0:
                self.x, self.y = nx, ny
            else:
                if 0<nx<MAP_W and gmap[int(self.y)][int(nx)]==0: self.x=nx
                elif 0<ny<MAP_H and gmap[int(ny)][int(self.x)]==0: self.y=ny

            melee_r = 1.0 if self.type=="loper" else 1.5
            if self.dist < melee_r:
                if self.melee_cd <= 0:
                    rate = 28 if self.type in ("loper","zombie") else 45
                    self.melee_cd = rate
                    result = "melee"
            elif self.range_dmg and self.dist < self.range_r:
                if self.range_cd <= 0:
                    rate = 35 if self.type=="heinrich" else \
                           25 if self.type=="ubersoldaten" else \
                           50 if self.type=="elite" else 70
                    self.range_cd = random.randint(rate-10, rate+25)
                    result = "ranged"
        else:
            self.patrol_t += 1
            if self.patrol_t > random.randint(40,100):
                self.patrol_t = 0
                self.patrol_ang += random.uniform(-1.3, 1.3)
            nx = self.x + math.cos(self.patrol_ang)*self.spd*0.5
            ny = self.y + math.sin(self.patrol_ang)*self.spd*0.5
            if 0<nx<MAP_W and 0<ny<MAP_H and gmap[int(ny)][int(nx)]==0:
                self.x, self.y = nx, ny
            else:
                self.patrol_ang += math.pi + random.uniform(-0.5,0.5)

        if self.melee_cd > 0: self.melee_cd -= 1
        if self.range_cd > 0: self.range_cd -= 1
        return result

    def hit(self, dmg):
        # Übersoldaten takes half damage from non-explosive
        if self.type in ("ubersoldaten","heinrich"):
            dmg = max(1, dmg//2)
        self.hp     -= dmg
        self.pain_t  = 7
        self.state   = "chase"
        return self.hp <= 0

# ══════════════════════════════════════════════════════════════════════════════
#  PICKUP
# ══════════════════════════════════════════════════════════════════════════════
class Pickup:
    __slots__ = ("x","y","type","active","dist")
    def __init__(self, x, y, ptype):
        self.x=x; self.y=y; self.type=ptype; self.active=True; self.dist=0.0

# ══════════════════════════════════════════════════════════════════════════════
#  GAME
# ══════════════════════════════════════════════════════════════════════════════
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(22050, -16, 2, 512)
        pygame.mixer.set_num_channels(16)
        self.scr   = pygame.display.set_mode((SW, SH))
        pygame.display.set_caption("Return to Castle Wolfenstein  –  Python Tribute")
        self.clk   = pygame.time.Clock()

        # fonts
        self.FXL = pygame.font.SysFont("Courier New", 48, bold=True)
        self.FLG = pygame.font.SysFont("Courier New", 28, bold=True)
        self.FMD = pygame.font.SysFont("Courier New", 18, bold=True)
        self.FSM = pygame.font.SysFont("Courier New", 12)
        self.FTI = pygame.font.SysFont("Courier New", 14, bold=True)

        # render buffers
        self.vsurf = pygame.Surface((RAYS, VIEW_H))
        self.bg    = self._build_bg()
        self.zbuf  = [0.0]*RAYS

        # sounds  (procedurally generated)
        self.SND = {
            "luger":    _snd( 820,  85, .50, "sq"),
            "mp40":     _snd( 870,  60, .47, "sq"),
            "fg42":     _snd( 950,  70, .52, "sq"),
            "sten":     _snd( 790,  65, .45, "sq"),
            "panzerfaust":_snd(250, 550, .60, "fall"),
            "flame":    _snd( 180,  55, .30, "nz"),
            "venom":    _snd(1050,  40, .55, "nz"),
            "tesla":    _snd( 320, 180, .55, "blip"),
            "knife":    _snd( 250,  65, .28, "nz"),
            "hit":      _snd( 160, 120, .42, "fall"),
            "kill":     _snd( 110, 600, .45, "fall"),
            "pickup":   _snd(1150, 130, .28, "blip"),
            "unlock":   _snd( 550, 220, .32, "blip"),
            "noammo":   _snd( 210,  85, .22, "sq"),
            "grenade":  _snd( 200, 650, .55, "fall"),
        }

        self.state    = "menu"
        self.tick     = 0
        self.show_map = True

        self.notifs   = []    # (text, color, frames)
        self.killfeed = []    # (text, frames)
        self.particles= []
        self.grenades = []

        self.win_flag = False
        self.reset()

    # ── gradient background ───────────────────────────────────────────────────
    def _build_bg(self):
        s = pygame.Surface((SW, VIEW_H))
        half = VIEW_H//2
        for y in range(half):
            t = y/max(1, half-1)
            r = int(CTOP[0]+(CMID[0]-CTOP[0])*t)
            g = int(CTOP[1]+(CMID[1]-CTOP[1])*t)
            b = int(CTOP[2]+(CMID[2]-CTOP[2])*t)
            pygame.draw.line(s,(r,g,b),(0,y),(SW-1,y))
        for y in range(half, VIEW_H):
            t = (y-half)/max(1, VIEW_H-half-1)
            r = int(FMID[0]+(FBOT[0]-FMID[0])*t)
            g = int(FMID[1]+(FBOT[1]-FMID[1])*t)
            b = int(FMID[2]+(FBOT[2]-FMID[2])*t)
            pygame.draw.line(s,(r,g,b),(0,y),(SW-1,y))
        return s

    def reset(self):
        self.player    = Player()
        self.enemies   = [Enemy(t,x,y) for t,x,y in SPAWNS]
        self.pickups   = [Pickup(x,y,tp) for x,y,tp in PICKUPS]
        self.particles = []
        self.grenades  = []
        self.notifs    = []
        self.killfeed  = []
        self.zbuf      = [0.0]*RAYS
        self.tick      = 0
        self.win_flag  = False

    # ══════════════════════════════════════════════════════════════════════════
    #  RAYCASTING  (DDA)
    # ══════════════════════════════════════════════════════════════════════════
    def cast_rays(self):
        self.vsurf.blit(self.bg, (0,0))
        self.zbuf = []
        ang  = self.player.angle - HFOV
        step = FOV/RAYS
        h    = VIEW_H
        px,py,pa = self.player.x, self.player.y, self.player.angle

        for i in range(RAYS):
            ca = math.cos(ang); sa = math.sin(ang)
            if abs(ca)<1e-7: ca=1e-7
            if abs(sa)<1e-7: sa=1e-7
            mx,my = int(px),int(py)
            sx,sy = (1 if ca>0 else -1),(1 if sa>0 else -1)
            ddx,ddy = abs(1/ca),abs(1/sa)
            sdx = ((mx+(1 if ca>0 else 0))-px)/ca
            sdy = ((my+(1 if sa>0 else 0))-py)/sa
            hit=False; side=0; wt=1

            for _ in range(MDIST*4):
                if sdx<sdy: sdx+=ddx; mx+=sx; side=1
                else:       sdy+=ddy; my+=sy; side=0
                if 0<=my<MAP_H and 0<=mx<MAP_W and GAME_MAP[my][mx]:
                    wt=GAME_MAP[my][mx]; hit=True; break

            if hit:
                dist = abs(((mx-px+(1-sx)*.5)/ca if side==1 else (my-py+(1-sy)*.5)/sa)
                           * math.cos(ang-pa))
                dist = max(dist, 0.001)
                self.zbuf.append(dist)
                wh   = int(h/dist)
                pair = WCOLORS.get(wt,((120,115,110),(78,74,70)))
                base = pair[0] if side==0 else pair[1]
                sh   = max(0.14, 1.0 - dist/MDIST)
                col  = (int(base[0]*sh),int(base[1]*sh),int(base[2]*sh))
                top  = h//2 - wh//2
                pygame.draw.line(self.vsurf, col,
                                 (i, max(0,top)), (i, min(h,top+wh)))
            else:
                self.zbuf.append(1e9)
            ang += step

        scaled = pygame.transform.scale(self.vsurf, (SW, VIEW_H))
        self.scr.blit(scaled, (0,0))

    # ══════════════════════════════════════════════════════════════════════════
    #  SPRITES
    # ══════════════════════════════════════════════════════════════════════════
    def draw_sprites(self):
        sprites=[]
        for e in self.enemies:
            dx=e.x-self.player.x; dy=e.y-self.player.y
            e.dist=math.hypot(dx,dy); sprites.append(("e",e))
        for p in self.pickups:
            if p.active:
                dx=p.x-self.player.x; dy=p.y-self.player.y
                p.dist=math.hypot(dx,dy); sprites.append(("p",p))
        for g in self.grenades:
            dx=g.x-self.player.x; dy=g.y-self.player.y
            g.dist=math.hypot(dx,dy); sprites.append(("g",g))
        sprites.sort(key=lambda s:s[1].dist, reverse=True)

        nb = len(self.zbuf)
        for stype, obj in sprites:
            dx=obj.x-self.player.x; dy=obj.y-self.player.y
            rel=math.atan2(dy,dx)-self.player.angle
            while rel> math.pi: rel-=2*math.pi
            while rel<-math.pi: rel+=2*math.pi
            if abs(rel)>HFOV+0.3: continue
            dist=obj.dist
            if dist<0.22: continue

            sx   = int((0.5+rel/FOV)*SW)
            sh_  = max(4, int(VIEW_H/dist))
            sw_  = sh_
            ty   = VIEW_H//2 - sh_//2
            lx   = sx - sw_//2
            shade= max(0.08, 1.0-dist/16.0)

            def zbuf_ok(x):
                if nb==0: return False
                ri=max(0,min(nb-1, x*nb//SW))
                return dist < self.zbuf[ri]

            if stype=="e":
                self._draw_enemy(obj,sx,sh_,sw_,ty,lx,shade,dist,zbuf_ok)
            elif stype=="p":
                self._draw_pickup(obj,sx,sh_,sw_,ty,lx,shade,dist,zbuf_ok)
            elif stype=="g":
                # grenade as small dark sphere
                if zbuf_ok(sx):
                    r=max(2,sh_//10)
                    pygame.draw.circle(self.scr,(80,65,30),(sx,VIEW_H//2+sh_//4),r)

    def _draw_enemy(self, e, sx, sh, sw, ty, lx, shade, dist, zbuf_ok):
        if not e.alive:
            dh=max(3,sh//5); dy_=VIEW_H-dh
            c=(int(40*shade),int(12*shade),int(12*shade))
            for x in range(max(0,lx),min(SW,lx+sw)):
                if zbuf_ok(x): pygame.draw.line(self.scr,c,(x,dy_),(x,dy_+dh))
            return

        base = e.col_alert if e.state=="chase" else e.col_idle
        if e.pain_t>0: base=(230,230,230)

        # bigger sprites for heavier enemies
        if e.type in ("ubersoldaten","heinrich"):
            sh=int(sh*1.6); ty=VIEW_H//2-sh//2
        elif e.type=="zombie":
            sh=int(sh*1.2); ty=VIEW_H//2-sh//2

        col=tuple(int(c*shade) for c in base)

        # unique body shape per type ──────────────────────────────────────────
        if e.type=="loper":
            # crouched, wide, low
            lh=max(3,sh//2); ly_=VIEW_H//2+sh//4
            lw_=int(sw*1.5); llx=sx-lw_//2
            for x in range(max(0,llx),min(SW,llx+lw_)):
                if zbuf_ok(x): pygame.draw.line(self.scr,col,(x,ly_),(x,ly_+lh))
        elif e.type=="zombie":
            # greenish, tattered – body with "torn" gaps
            for x in range(max(0,lx),min(SW,lx+sw)):
                if zbuf_ok(x):
                    for y in range(max(0,ty),min(VIEW_H,ty+sh)):
                        # torn gaps every few pixels for tattered look
                        if (x+y)%7 < (1 if shade<0.4 else 2):
                            continue
                        self.scr.set_at((x,y),col)
        elif e.type in ("ubersoldaten","heinrich"):
            # solid gradient body (darker toward feet)
            for x in range(max(0,lx),min(SW,lx+sw)):
                if zbuf_ok(x):
                    for y in range(max(0,ty),min(VIEW_H,ty+sh)):
                        tt=(y-ty)/max(1,sh)
                        dc=tuple(int(c*(1-tt*0.35)) for c in col)
                        self.scr.set_at((x,y),dc)
        else:
            for x in range(max(0,lx),min(SW,lx+sw)):
                if zbuf_ok(x): pygame.draw.line(self.scr,col,(x,max(0,ty)),(x,min(VIEW_H-1,ty+sh)))

        # head blob
        hr=max(2,sh//8); hy=max(hr,ty+hr)
        if 0<=sx<SW and 0<hy<VIEW_H and zbuf_ok(sx):
            hc=(min(255,col[0]+45),min(255,col[1]+35),min(255,col[2]+25))
            pygame.draw.circle(self.scr,hc,(sx,hy),hr)

        # HP bar close-up + name tag
        if dist<6:
            tc=(255,60,60) if e.type in ("ubersoldaten","heinrich") else (255,190,40)
            tag=self.FSM.render(f"{e.type.upper()}  HP:{e.hp}",True,tc)
            self.scr.blit(tag,(sx-tag.get_width()//2, max(0,ty-hr*2-15)))

    def _draw_pickup(self, p, sx, sh, sw, ty, lx, shade, dist, zbuf_ok):
        base=PICKUP_COL.get(p.type,(180,180,180))
        col=tuple(int(c*shade) for c in base)
        ih=max(4,sh//2); iy=VIEW_H//2-ih//2
        for x in range(max(0,lx+sw//4),min(SW,lx+3*sw//4)):
            if zbuf_ok(x):
                pygame.draw.line(self.scr,col,(x,max(0,iy)),(x,min(VIEW_H-1,iy+ih)))
        if dist<5:
            lbl=self.FSM.render(PICKUP_LABEL.get(p.type,"?"),True,col)
            self.scr.blit(lbl,(sx-lbl.get_width()//2, max(0,iy-14)))

    # ── particles ─────────────────────────────────────────────────────────────
    def draw_particles(self):
        """Project world-space particles to screen (approximate billboard)."""
        alive=[]
        for pt in self.particles:
            if pt.update():
                alive.append(pt)
                dx=pt.x-self.player.x; dy=pt.y-self.player.y
                dist=math.hypot(dx,dy)
                if dist<0.15: continue
                rel=math.atan2(dy,dx)-self.player.angle
                while rel> math.pi: rel-=2*math.pi
                while rel<-math.pi: rel+=2*math.pi
                if abs(rel)>HFOV+0.2: continue
                px_=int((0.5+rel/FOV)*SW)
                py_=VIEW_H//2+random.randint(-6,6)
                size=max(1,int(pt.size*(1-pt.life/pt.maxl*0.5)/max(0.5,dist)))
                if 0<=px_<SW and 0<=py_<VIEW_H:
                    col=pt.alpha_col()
                    pygame.draw.circle(self.scr,col,(px_,py_),size)
        self.particles=alive

    def _spawn_explosion(self, x, y, n=30):
        for _ in range(n):
            a=random.uniform(0,2*math.pi); s=random.uniform(0.01,0.06)
            self.particles.append(Particle(
                x,y, math.cos(a)*s, math.sin(a)*s,
                random.choice([(255,180,40),(255,100,20),(255,220,60)]),
                random.randint(18,45), random.randint(3,7)))

    def _spawn_flame(self, x, y):
        for _ in range(5):
            a=self.player.angle+random.uniform(-0.3,0.3)
            s=random.uniform(0.025,0.06)
            self.particles.append(Particle(
                x,y, math.cos(a)*s, math.sin(a)*s,
                random.choice([(255,120,30),(255,60,10),(255,200,40)]),
                random.randint(8,20), random.randint(2,5)))

    def _spawn_tesla(self, x, y):
        for _ in range(8):
            a=random.uniform(0,2*math.pi)
            self.particles.append(Particle(
                x,y, math.cos(a)*random.uniform(0.01,0.04),
                math.sin(a)*random.uniform(0.01,0.04),
                random.choice([(100,180,255),(50,100,255),(200,220,255)]),
                random.randint(5,14), random.randint(2,4)))

    # ══════════════════════════════════════════════════════════════════════════
    #  MINIMAP
    # ══════════════════════════════════════════════════════════════════════════
    def draw_minimap(self):
        cs=MM_CS; mw=MAP_W*cs; mh=MAP_H*cs
        sf=pygame.Surface((mw,mh),pygame.SRCALPHA)
        sf.fill((0,0,0,180))
        for row in range(MAP_H):
            for col in range(MAP_W):
                v=GAME_MAP[row][col]
                if v:
                    c=WCOLORS.get(v,((110,105,100),(72,68,65)))[0]
                    pygame.draw.rect(sf,c,(col*cs,row*cs,cs-1,cs-1))
        for e in self.enemies:
            ec=(235,40,40) if e.type in ("ubersoldaten","heinrich") else \
               ( 50,200,80) if e.type in ("zombie","loper") else (190,55,55)
            r=4 if e.type in ("ubersoldaten","heinrich") else 2
            pygame.draw.circle(sf, ec if e.alive else (60,20,20),
                               (int(e.x*cs),int(e.y*cs)), r)
        for p in self.pickups:
            if p.active:
                pygame.draw.circle(sf,PICKUP_COL.get(p.type,(180,180,180)),
                                   (int(p.x*cs),int(p.y*cs)),2)
        for g in self.grenades:
            pygame.draw.circle(sf,(210,165,30),(int(g.x*cs),int(g.y*cs)),2)

        ppx=int(self.player.x*cs); ppy=int(self.player.y*cs)
        pygame.draw.circle(sf,(0,210,255),(ppx,ppy),4)
        ex_=ppx+int(math.cos(self.player.angle)*10)
        ey_=ppy+int(math.sin(self.player.angle)*10)
        pygame.draw.line(sf,(0,210,255),(ppx,ppy),(ex_,ey_),2)
        for off in (-HFOV,HFOV):
            fx=ppx+int(math.cos(self.player.angle+off)*20)
            fy=ppy+int(math.sin(self.player.angle+off)*20)
            pygame.draw.line(sf,(0,145,195),(ppx,ppy),(fx,fy),1)

        self.scr.blit(sf,(10,10))
        pygame.draw.rect(self.scr,(88,108,128),(10,10,mw,mh),2)
        nrt=self.FSM.render("N",True,(160,160,240))
        self.scr.blit(nrt,(10+mw//2-4, 12))

    # ══════════════════════════════════════════════════════════════════════════
    #  HUD
    # ══════════════════════════════════════════════════════════════════════════
    def draw_hud(self):
        p=self.player
        pygame.draw.rect(self.scr,HUD_BG,(0,HUD_Y,SW,HUD_H))
        pygame.draw.line(self.scr,HUD_LN,(0,HUD_Y),(SW,HUD_Y),3)

        # ── health ────────────────────────────────────────────────────────────
        self.scr.blit(self.FMD.render("HEALTH",True,(170,130,68)),(18,HUD_Y+8))
        bw=210; hp=max(0,p.hp)/100.0
        hcol=(45,190,45) if hp>.55 else (195,170,0) if hp>.28 else (205,35,35)
        pygame.draw.rect(self.scr,(48,8,8),(18,HUD_Y+30,bw,22))
        if hp>0: pygame.draw.rect(self.scr,hcol,(18,HUD_Y+30,int(bw*hp),22))
        pygame.draw.rect(self.scr,(108,70,35),(18,HUD_Y+30,bw,22),2)
        self.scr.blit(self.FLG.render(str(p.hp),True,WHITE),(236,HUD_Y+26))

        # ── armor ─────────────────────────────────────────────────────────────
        self.scr.blit(self.FMD.render("ARMOR",True,(68,120,170)),(18,HUD_Y+58))
        aw=210; ar=max(0,p.armor)/100.0
        pygame.draw.rect(self.scr,(8,18,42),(18,HUD_Y+76,aw,14))
        if ar>0: pygame.draw.rect(self.scr,(45,90,195),(18,HUD_Y+76,int(aw*ar),14))
        pygame.draw.rect(self.scr,(38,68,120),(18,HUD_Y+76,aw,14),2)
        self.scr.blit(self.FSM.render(str(p.armor)+"%" ,True,(100,160,255)),(236,HUD_Y+74))

        # ── BJ face (dark / gritty) ───────────────────────────────────────────
        fx,fy=SW//2-42,HUD_Y+3
        if   p.pain_t>0:  fcol=(220,65,65)
        elif p.hp<25:     fcol=(165,68,68)
        elif p.hp<60:     fcol=(185,115,68)
        else:             fcol=(182,138,95)
        # head
        pygame.draw.ellipse(self.scr,fcol,(fx,fy,82,95))
        # helmet
        pygame.draw.ellipse(self.scr,(45,50,45),(fx-2,fy-4,86,40))
        pygame.draw.line(self.scr,(28,32,28),(fx-2,fy+20),(fx+83,fy+20),3)
        # eyes
        ey0=fy+38
        for ex0 in (fx+17,fx+51):
            pygame.draw.ellipse(self.scr,WHITE,(ex0,ey0,15,11))
            poff=-4 if p.pain_t>0 else 2
            pygame.draw.circle(self.scr,BLACK,(ex0+7+poff,ey0+5),4)
        # mouth
        my0=fy+68
        if p.pain_t>0:
            pygame.draw.arc(self.scr,(160,15,15),(fx+20,my0,40,14),0,math.pi,3)
        else:
            pygame.draw.line(self.scr,(130,45,45),(fx+22,my0+5),(fx+55,my0+5),2)
        pygame.draw.ellipse(self.scr,(95,65,35),(fx,fy,82,95),3)

        # ── weapon + ammo ─────────────────────────────────────────────────────
        wx0=SW//2+55
        wname=WPN[p.weapon][0]
        akey =WPN[p.weapon][6]
        amt  =p.ammo.get(akey,0) if akey else -1
        self.scr.blit(self.FMD.render("WEAPON",True,(170,130,68)),(wx0,HUD_Y+5))
        self.scr.blit(self.FMD.render(wname,  True,(210,195,110)),(wx0,HUD_Y+26))
        if akey:
            ac=YELLOW if amt>8 else (215,80,40)
            self.scr.blit(self.FLG.render(f"AMO {amt:02d}",True,ac),(wx0,HUD_Y+50))
            if amt==0:
                self.scr.blit(self.FMD.render("NO AMMO!",True,(255,55,55)),(wx0,HUD_Y+84))
        else:
            self.scr.blit(self.FLG.render("∞",True,(150,215,150)),(wx0,HUD_Y+50))

        # ── weapon select row ─────────────────────────────────────────────────
        sel_row = [
            ("1","KNIFE",  (85,80,75)),  ("2","LUGER",  (80,100,80)),
            ("3","MP40",   (80,80,110)), ("4","FG42",   (110,90,60)),
            ("5","PANZR",  (130,65,45)), ("6","FLAME",  (140,65,30)),
            ("7","VENOM",  (90,55,145)), ("8","TESLA",  (55,95,170)),
        ]
        wk=["knife","luger","mp40","fg42","panzerfaust","flame","venom","tesla"]
        sx0=SW-8*74-10
        for idx,(key,lbl,uc) in enumerate(sel_row):
            wkey=wk[idx]
            owned=wkey in p.unlocked; sel=p.weapon==wkey
            bdr=(240,210,45) if sel else ((100,85,55) if owned else (35,35,35))
            bgc=uc if owned else (30,30,30)
            tx0=sx0+idx*74
            pygame.draw.rect(self.scr,bgc,(tx0,HUD_Y+6,66,36),0,4)
            pygame.draw.rect(self.scr,bdr,(tx0,HUD_Y+6,66,36),2,4)
            self.scr.blit(self.FSM.render(f"[{key}]{lbl}",True,
                                          WHITE if owned else (55,55,55)),(tx0+4,HUD_Y+16))

        # ── score / kills ─────────────────────────────────────────────────────
        self.scr.blit(self.FMD.render(f"SCORE {p.score:>8}",True,(200,190,90)),(SW-200,HUD_Y+48))
        self.scr.blit(self.FMD.render(f"KILLS {p.kills:>4}",  True,(200,90,90)),  (SW-200,HUD_Y+76))

        # ── grenade cooldown ──────────────────────────────────────────────────
        gcol=(200,165,50) if p.grenade_cd==0 else (100,80,25)
        self.scr.blit(self.FSM.render(f"[G] GRENADE {'RDY' if p.grenade_cd==0 else str(p.grenade_cd//6)}",
                                      True,gcol),(SW-200,HUD_Y+95))

        # ── pain flash ────────────────────────────────────────────────────────
        if p.pain_t>0:
            fl=pygame.Surface((SW,VIEW_H),pygame.SRCALPHA)
            fl.fill((185,0,0,int(p.pain_t/32*120)))
            self.scr.blit(fl,(0,0))

        # ── crosshair ─────────────────────────────────────────────────────────
        cx,cy=SW//2,VIEW_H//2
        cc=(255,70,70) if p.muzzle_t else (200,200,200)
        if p.weapon=="tesla": cc=(100,180,255) if p.muzzle_t else (150,150,200)
        for pts in [((cx-14,cy),(cx-5,cy)),((cx+5,cy),(cx+14,cy)),
                    ((cx,cy-14),(cx,cy-5)),((cx,cy+5),(cx,cy+14))]:
            pygame.draw.line(self.scr,cc,pts[0],pts[1],2)
        pygame.draw.circle(self.scr,cc,(cx,cy),2)

        # ── gun sprite ────────────────────────────────────────────────────────
        self._draw_gun()
        self._draw_notifs()

    # ─────────────────────────────────────────────────────────────────────────
    def _draw_gun(self):
        p=self.player; w=p.weapon
        cd=WPN[w][4]
        recoil=int(p.shoot_cd/cd*24) if p.shoot_cd>0 else 0
        wbob=int(math.sin(p.walk_t*2)*5) if p.moving else 0
        gx=SW//2; gy=VIEW_H-6+recoil+abs(wbob)
        mf=p.muzzle_t>0

        if w=="knife":
            pts=[(gx+6,gy),(gx+10,gy-62),(gx+16,gy-62),(gx+20,gy-34),(gx+13,gy)]
            pygame.draw.polygon(self.scr,(170,170,190),pts)
            pygame.draw.rect(self.scr,(75,52,28),(gx+4,gy-28,12,35))

        elif w in ("mp40","sten"):
            pygame.draw.rect(self.scr,(52,52,52),(gx-10,gy-72,18,72))
            pygame.draw.rect(self.scr,(36,36,36),(gx-7, gy-88,12,20))
            pygame.draw.rect(self.scr,(85,55,22),(gx-20,gy-45,13,52))
            # fold-down mag
            pygame.draw.rect(self.scr,(40,40,40),(gx-2, gy-60,6, 22))
            if mf:
                for _ in range(5):
                    fx_=gx+random.randint(-10,10); fy_=gy-90+random.randint(-8,2)
                    pygame.draw.circle(self.scr,YELLOW,(fx_,fy_),random.randint(4,9))
                    pygame.draw.circle(self.scr,WHITE, (fx_,fy_),random.randint(2,5))

        elif w=="luger":
            pygame.draw.rect(self.scr,(55,55,55),(gx-7, gy-62,14,62))
            pygame.draw.rect(self.scr,(85,55,22),(gx-16,gy-35,12,42))
            pygame.draw.arc(self.scr,(50,50,50),(gx-14,gy-18,14,14),math.pi,2*math.pi,2)
            if mf:
                pygame.draw.circle(self.scr,YELLOW,(gx,gy-66),9)
                pygame.draw.circle(self.scr,WHITE, (gx,gy-66),5)

        elif w=="fg42":
            # rifle with scope
            pygame.draw.rect(self.scr,(48,48,48),(gx-8, gy-80,16,80))
            pygame.draw.rect(self.scr,(30,30,30),(gx-5, gy-96,10,20))
            pygame.draw.rect(self.scr,(95,60,24),(gx-20,gy-52,14,56))
            # scope
            pygame.draw.rect(self.scr,(28,28,28),(gx-4, gy-88, 8,20))
            pygame.draw.rect(self.scr,(65,65,65),(gx-6, gy-92,12, 8))
            if mf:
                for _ in range(5):
                    pygame.draw.circle(self.scr,YELLOW,
                        (gx+random.randint(-8,8),gy-98+random.randint(-5,2)),
                        random.randint(4,8))

        elif w=="panzerfaust":
            # thick tube
            pygame.draw.rect(self.scr,(85,65,30),(gx-24,gy-55,48,25))
            # warhead
            pygame.draw.ellipse(self.scr,(195,75,30),(gx-14,gy-80,28,30))
            # launch tube
            pygame.draw.rect(self.scr,(60,55,48),(gx-12,gy-55,24,62))
            if mf:
                self._spawn_explosion(self.player.x+math.cos(self.player.angle)*1.2,
                                      self.player.y+math.sin(self.player.angle)*1.2,8)

        elif w=="flame":
            # nozzle + tank
            pygame.draw.rect(self.scr,(55,80,55),(gx-18,gy-45,36,45))
            pygame.draw.rect(self.scr,(40,60,40),(gx-24,gy-35,12,35))
            pygame.draw.rect(self.scr,(48,48,48),(gx-4, gy-65,10,25))
            if mf:
                for _ in range(8):
                    fx_=gx+random.randint(-12,12); fy_=gy-68+random.randint(-10,5)
                    pygame.draw.circle(self.scr,
                        random.choice([(255,100,20),(255,60,10),(255,210,30)]),
                        (fx_,fy_),random.randint(5,12))

        elif w=="venom":
            # hexagonal minigun barrel cluster
            for ang in range(0,360,60):
                ox=int(math.cos(math.radians(ang))*6)
                oy=int(math.sin(math.radians(ang))*5)
                pygame.draw.rect(self.scr,(42,42,42),(gx-5+ox,gy-85,10,85))
            pygame.draw.rect(self.scr,(65,50,28),(gx-26,gy-55,14,58))
            if mf:
                for _ in range(9):
                    fx_=gx+random.randint(-14,14); fy_=gy-88+random.randint(-12,0)
                    pygame.draw.circle(self.scr,YELLOW,(fx_,fy_),random.randint(5,11))
                    pygame.draw.circle(self.scr,WHITE, (fx_,fy_),random.randint(2,6))

        elif w=="tesla":
            # tesla cannon – glowing barrel
            pygame.draw.rect(self.scr,(45,58,80),(gx-14,gy-72,28,72))
            pygame.draw.rect(self.scr,(30,42,60),(gx-10,gy-90,20,22))
            # coils
            for i in range(3):
                yy=gy-30-i*18
                pygame.draw.rect(self.scr,(80,120,180),(gx-16,yy,4,12))
                pygame.draw.rect(self.scr,(80,120,180),(gx+12,yy,4,12))
            if mf:
                for _ in range(10):
                    self._spawn_tesla(
                        self.player.x+math.cos(self.player.angle)*1.5,
                        self.player.y+math.sin(self.player.angle)*1.5)
                # arc on screen
                for _ in range(6):
                    sx_=gx+random.randint(-30,30); sy_=gy-90+random.randint(-20,10)
                    pygame.draw.line(self.scr,(100,185,255),(gx,gy-94),(sx_,sy_),2)

    # ─────────────────────────────────────────────────────────────────────────
    def _draw_notifs(self):
        y0=VIEW_H-35; alive=[]
        for txt,col,t in self.notifs:
            if t>0:
                a=min(255,int(t/120*255))
                s=self.FTI.render(txt,True,col)
                ns=pygame.Surface(s.get_size(),pygame.SRCALPHA); ns.blit(s,(0,0)); ns.set_alpha(a)
                self.scr.blit(ns,(SW//2-s.get_width()//2,y0)); y0-=22
                alive.append((txt,col,t-1))
        self.notifs=alive

        ky=VIEW_H-20; kf=[]
        for txt,t in self.killfeed:
            if t>0:
                a=min(255,int(t/150*255))
                s=self.FSM.render(txt,True,(250,155,55))
                ns=pygame.Surface(s.get_size(),pygame.SRCALPHA); ns.blit(s,(0,0)); ns.set_alpha(a)
                self.scr.blit(ns,(SW-s.get_width()-14,ky)); ky-=16; kf.append((txt,t-1))
        self.killfeed=kf[:6]

    def _notif(self,txt,col=(215,215,80),dur=115): self.notifs.append((txt,col,dur))
    def _kill(self,txt): self.killfeed.append((txt,155)); self.killfeed=self.killfeed[-6:]

    # ══════════════════════════════════════════════════════════════════════════
    #  SHOOTING
    # ══════════════════════════════════════════════════════════════════════════
    def do_shoot(self):
        p=self.player
        if not p.do_shoot():
            if WPN[p.weapon][5] and p.ammo.get(WPN[p.weapon][6],0)==0:
                s=self.SND.get("noammo")
                if s: s.play()
            return

        w=p.weapon
        snd=self.SND.get(w) or self.SND.get("luger")
        if snd: snd.play()

        rang=WPN[w][2]; dmgr=(WPN[w][3],WPN[w][4])
        splash=WPN[w][8]

        if w=="flame":
            self._spawn_flame(p.x+math.cos(p.angle)*0.8, p.y+math.sin(p.angle)*0.8)

        for e in self.enemies:
            if not e.alive: continue
            dx=e.x-p.x; dy=e.y-p.y
            d=math.hypot(dx,dy)
            if d>rang: continue
            ang_to=math.atan2(dy,dx)
            diff=abs(ang_to-p.angle)
            if diff>math.pi: diff=2*math.pi-diff
            arc=0.07+0.15/max(d,0.5)
            # splash weapons always hit nearby
            if splash: hit=d<3.5
            else:      hit=diff<arc

            if hit:
                dmg=random.randint(*dmgr)
                if splash: dmg=max(1,int(dmg*(1-d/3.5)))
                if e.hit(dmg):
                    p.kills+=1; p.score+=e.score_val
                    if self.SND.get("kill"): self.SND["kill"].play()
                    self._kill(f"KILLED {e.type.upper()}! +{e.score_val}")
                    if e.type=="ubersoldaten":
                        self._notif("ÜBERSOLDAT DESTROYED!",(255,90,90),160)
                    if e.type=="heinrich":
                        self._notif("HEINRICH I DEFEATED!",(255,60,60),200)
                    if splash:
                        self._spawn_explosion(e.x,e.y)
                else:
                    if self.SND.get("hit"): self.SND["hit"].play()

    # ══════════════════════════════════════════════════════════════════════════
    #  GRENADES
    # ══════════════════════════════════════════════════════════════════════════
    def update_grenades(self):
        alive=[]; p=self.player
        for g in self.grenades:
            if g.update(GAME_MAP):
                alive.append(g)
            else:
                # EXPLODE
                if self.SND.get("grenade"): self.SND["grenade"].play()
                self._spawn_explosion(g.x,g.y,40)
                # damage enemies
                for e in self.enemies:
                    if not e.alive: continue
                    d=math.hypot(e.x-g.x,e.y-g.y)
                    if d<2.5:
                        dmg=random.randint(20,60); dmg=max(1,int(dmg*(1-d/2.5)))
                        if e.hit(dmg):
                            p.kills+=1; p.score+=e.score_val
                            self._kill(f"KILLED {e.type.upper()} [GRENADE]! +{e.score_val}")
                # damage player if too close
                pd=math.hypot(p.x-g.x,p.y-g.y)
                if pd<1.5: p.take_hit(random.randint(15,40))
        self.grenades=alive

    # ══════════════════════════════════════════════════════════════════════════
    #  PICKUPS
    # ══════════════════════════════════════════════════════════════════════════
    def check_pickups(self):
        p=self.player
        for pk in self.pickups:
            if not pk.active: continue
            if math.hypot(pk.x-p.x,pk.y-p.y)<0.72:
                pk.active=False
                if self.SND.get("pickup"): self.SND["pickup"].play()
                t=pk.type
                if t=="health":
                    p.hp=min(100,p.hp+25); self._notif("HEALTH +25",(45,215,45))
                elif t=="food":
                    p.hp=min(100,p.hp+10); self._notif("FOOD +10 HP",(195,155,45))
                elif t=="armor":
                    p.armor=min(100,p.armor+30); self._notif("ARMOR +30",(45,110,210))
                elif t=="ammo_smg":
                    p.ammo["smg"]=min(99,p.ammo["smg"]+30); self._notif("SMG AMMO +30",YELLOW)
                elif t=="ammo_rifle":
                    p.ammo["rifle"]=min(40,p.ammo["rifle"]+10); self._notif("RIFLE AMMO +10",YELLOW)
                elif t=="ammo_pistol":
                    p.ammo["pistol"]=min(60,p.ammo["pistol"]+20); self._notif("PISTOL AMMO +20",YELLOW)
                elif t=="ammo_rockets":
                    p.ammo["rockets"]=min(10,p.ammo["rockets"]+3); self._notif("ROCKETS +3",(215,85,45))
                elif t=="ammo_venom":
                    p.ammo["venom"]=min(99,p.ammo["venom"]+25); self._notif("VENOM CELLS +25",(175,95,215))
                elif t=="weapon_sten":
                    p.unlocked.add("sten"); p.ammo["smg"]=min(99,p.ammo["smg"]+30)
                    self._notif("STEN SMG ACQUIRED!",(155,155,95),140)
                    if self.SND.get("unlock"): self.SND["unlock"].play()
                elif t=="weapon_fg42":
                    p.unlocked.add("fg42"); p.ammo["rifle"]=min(40,p.ammo["rifle"]+15)
                    self._notif("FG 42 ACQUIRED!",(95,155,95),140)
                    if self.SND.get("unlock"): self.SND["unlock"].play()
                elif t=="weapon_venom":
                    p.unlocked.add("venom"); p.ammo["venom"]=min(99,p.ammo["venom"]+40)
                    p.unlocked.add("panzerfaust")   # panzerfaust also unlocked
                    self._notif("VENOM GUN + PANZERFAUST ACQUIRED!",(115,55,200),160)
                    if self.SND.get("unlock"): self.SND["unlock"].play()
                elif t=="weapon_tesla":
                    p.unlocked.add("tesla"); p.ammo["tesla"]=min(20,p.ammo["tesla"]+12)
                    self._notif("TESLA CANNON ACQUIRED!",(55,95,200),160)
                    if self.SND.get("unlock"): self.SND["unlock"].play()

    # ══════════════════════════════════════════════════════════════════════════
    #  SCREENS
    # ══════════════════════════════════════════════════════════════════════════
    def draw_menu(self):
        self.scr.fill((10,6,3))
        t=self.tick/60.0
        # scanlines
        for y in range(0,SH,4):
            pygame.draw.line(self.scr,(0,0,0,80),(0,y),(SW,y))

        # title
        sc=1.0+0.04*math.sin(t*2.5)
        ts=self.FXL.render("RETURN TO CASTLE WOLFENSTEIN",True,(200,165,40))
        tw=int(ts.get_width()*sc); th=int(ts.get_height()*sc)
        ts=pygame.transform.scale(ts,(tw,th))
        self.scr.blit(ts,(SW//2-tw//2,30))
        self.scr.blit(self.FLG.render("Python Tribute  •  B.J. Blazkowicz  •  OSA 1943",
                                       True,(165,60,35)),(SW//2-255,90))
        pygame.draw.line(self.scr,(72,50,18),(SW//2-310,120),(SW//2+310,120),2)

        # story blurb
        story=[
            "March 1943. You are Captain William J. Blazkowicz, US Army Office of",
            "Secret Actions. Captured while investigating Nazi occult operations,",
            "your partner Agent One is dead. You must escape Castle Wolfenstein,",
            "fight through catacombs and bunkers, and stop Operation: Resurrection",
            "before the SS Paranormal Division resurrects Heinrich I.",
        ]
        for i,line in enumerate(story):
            s=self.FSM.render(line,True,(185,175,155))
            self.scr.blit(s,(SW//2-s.get_width()//2,132+i*16))

        pygame.draw.line(self.scr,(72,50,18),(SW//2-310,218),(SW//2+310,218),2)

        # controls
        rows=[
            ("W S A D / ←→",  "Move, Strafe, Turn"),
            ("SPACE",          "Shoot  (hold for automatic weapons)"),
            ("G",              "Throw Grenade"),
            ("TAB",            "Cycle weapon"),
            ("1 – 8",          "Select weapon directly"),
            ("M",              "Toggle minimap"),
            ("P / ESC",        "Pause / Menu"),
        ]
        ry=226
        for key,desc in rows:
            ks=self.FMD.render(key,True,YELLOW)
            ds=self.FMD.render(desc,True,(195,190,175))
            self.scr.blit(ks,(SW//2-290,ry)); self.scr.blit(ds,(SW//2-80,ry)); ry+=26

        # enemy list
        el=self.FMD.render(
            "Guard  ·  SS  ·  Elite / Black Guard  ·  Zombie  ·  Loper"
            "  ·  Übersoldat  ·  BOSS: Heinrich I",True,(185,80,80))
        self.scr.blit(el,(SW//2-el.get_width()//2,ry+10))

        # prompt
        bc=(50+int(100*abs(math.sin(t*2))),188+int(60*abs(math.sin(t*2))),40)
        pr=self.FLG.render(">>  Press ENTER to begin  <<",True,bc)
        self.scr.blit(pr,(SW//2-pr.get_width()//2,ry+45))

    def draw_paused(self):
        ov=pygame.Surface((SW,SH),pygame.SRCALPHA); ov.fill((0,0,0,150))
        self.scr.blit(ov,(0,0))
        t1=self.FXL.render("PAUSED",True,(210,190,70))
        t2=self.FMD.render("Press P to continue  |  ESC – menu",True,(185,185,185))
        self.scr.blit(t1,(SW//2-t1.get_width()//2,SH//2-65))
        self.scr.blit(t2,(SW//2-t2.get_width()//2,SH//2+20))

    def draw_dead(self):
        ov=pygame.Surface((SW,SH),pygame.SRCALPHA); ov.fill((125,0,0,165))
        self.scr.blit(ov,(0,0))
        t1=self.FXL.render("B.J. BLAZKOWICZ  K.I.A.",True,RED)
        t2=self.FLG.render("Operation Resurrection succeeds...",True,(210,185,175))
        t3=self.FLG.render(f"Score: {self.player.score}   Kills: {self.player.kills}",True,WHITE)
        t4=self.FMD.render("R – Try again  |  ESC – menu",True,(180,180,180))
        for surf,y in zip([t1,t2,t3,t4],[-120,-55,10,70]):
            self.scr.blit(surf,(SW//2-surf.get_width()//2,SH//2+y))

    def draw_win(self):
        ov=pygame.Surface((SW,SH),pygame.SRCALPHA); ov.fill((0,50,0,155))
        self.scr.blit(ov,(0,0))
        t1=self.FXL.render("OPERATION: RESURRECTION STOPPED!",True,(90,255,90))
        t2=self.FLG.render("Heinrich I destroyed. Castle Wolfenstein liberated.",True,WHITE)
        t3=self.FLG.render(f"Final Score:  {self.player.score}   Kills:  {self.player.kills}",True,YELLOW)
        t4=self.FMD.render("Mission Accomplished  —  Press R to play again",True,(180,180,180))
        for surf,y in zip([t1,t2,t3,t4],[-130,-60,15,80]):
            self.scr.blit(surf,(SW//2-surf.get_width()//2,SH//2+y))

    def draw_cbar(self):
        s=self.FSM.render(
            "W/S–Move  A/D–Strafe  ←→–Turn  SPACE–Shoot  G–Grenade  TAB–Weapon  M–Map  P–Pause",
            True,(80,65,38))
        self.scr.blit(s,(SW//2-s.get_width()//2,SH-16))

    # ══════════════════════════════════════════════════════════════════════════
    #  WEAPON CYCLE (TAB)
    # ══════════════════════════════════════════════════════════════════════════
    def cycle_weapon(self):
        p=self.player
        idx=WPN_ORDER.index(p.weapon) if p.weapon in WPN_ORDER else 0
        for _ in range(len(WPN_ORDER)):
            idx=(idx+1)%len(WPN_ORDER)
            nw=WPN_ORDER[idx]
            if nw in p.unlocked:
                p.weapon=nw; break

    # ══════════════════════════════════════════════════════════════════════════
    #  MAIN LOOP
    # ══════════════════════════════════════════════════════════════════════════
    def run(self):
        holding=False
        wkey_map={
            pygame.K_1:"knife",  pygame.K_2:"luger",  pygame.K_3:"mp40",
            pygame.K_4:"fg42",   pygame.K_5:"panzerfaust",pygame.K_6:"flame",
            pygame.K_7:"venom",  pygame.K_8:"tesla",
        }

        while True:
            self.clk.tick(60); self.tick+=1
            fps=self.clk.get_fps()
            pygame.display.set_caption(
                f"RtCW Python  |  FPS {fps:.0f}  |  Score {self.player.score}")

            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
                if ev.type==pygame.KEYDOWN:
                    k=ev.key
                    if k==pygame.K_ESCAPE:
                        if self.state=="playing": self.state="menu"
                        else: pygame.quit(); sys.exit()
                    if k==pygame.K_RETURN and self.state=="menu":
                        self.reset(); self.state="playing"
                    if k==pygame.K_p:
                        if self.state=="playing": self.state="paused"
                        elif self.state=="paused": self.state="playing"
                    if k==pygame.K_r and self.state in ("dead","win"):
                        self.reset(); self.state="playing"
                    if self.state=="playing":
                        if k==pygame.K_SPACE: holding=True; self.do_shoot()
                        if k==pygame.K_g:
                            g=self.player.throw_grenade()
                            if g: self.grenades.append(g)
                        if k==pygame.K_TAB: self.cycle_weapon()
                        for key,wep in wkey_map.items():
                            if k==key and wep in self.player.unlocked:
                                self.player.weapon=wep
                        if k==pygame.K_m: self.show_map=not self.show_map
                if ev.type==pygame.KEYUP:
                    if ev.key==pygame.K_SPACE: holding=False

            # ── game update ──────────────────────────────────────────────────
            if self.state=="playing":
                p=self.player
                p.move(GAME_MAP)

                # autofire
                if holding and WPN[p.weapon][7]: self.do_shoot()

                # enemies
                for e in self.enemies:
                    res=e.update(p,GAME_MAP)
                    if res=="melee":
                        d=random.randint(*EDEFS[e.type][2])
                        p.take_hit(d)
                        if self.SND.get("hit"): self.SND["hit"].play()
                    elif res=="ranged" and EDEFS[e.type][3]:
                        miss=0.38 if e.type=="guard" else \
                             0.25 if e.type=="ss" else \
                             0.15 if e.type=="elite" else \
                             0.10 if e.type in ("ubersoldaten","heinrich") else 0.30
                        if random.random()>miss:
                            d=random.randint(*EDEFS[e.type][3])
                            p.take_hit(d)
                            if self.SND.get("hit"): self.SND["hit"].play()

                self.update_grenades()
                self.check_pickups()

                # death / win
                if p.hp<=0: self.state="dead"
                heinrich=[e for e in self.enemies if e.type=="heinrich" and not e.alive]
                if heinrich and not self.win_flag:
                    self.win_flag=True; p.score+=10000; self.state="win"

            # ── render ───────────────────────────────────────────────────────
            if self.state=="menu":
                self.draw_menu()
            elif self.state in ("playing","paused","dead","win"):
                self.cast_rays()
                self.draw_sprites()
                self.draw_particles()
                self.draw_hud()
                if self.show_map: self.draw_minimap()
                self.draw_cbar()
                if self.state=="paused": self.draw_paused()
                elif self.state=="dead": self.draw_dead()
                elif self.state=="win":  self.draw_win()

            pygame.display.flip()


# ══════════════════════════════════════════════════════════════════════════════
if __name__=="__main__":
    Game().run()
