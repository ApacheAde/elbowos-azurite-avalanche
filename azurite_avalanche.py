"""Azurite Avalanche — neon crystal-bank arcade for ElbowOS. Python 3 + pygame."""
import math, os, random, subprocess, sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if not PLAY or RECORD:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/workspace/artifacts/AZURITE_AVALANCHE_ElbowOS.mp4")
NAVY, INK = (7, 14, 28), (5, 10, 20)
TEAL, AMBER = (64, 224, 196), (255, 176, 72)
COPPER, CREAM = (196, 112, 62), (255, 236, 210)
COLS = [(62, 198, 255), (255, 210, 122), (255, 107, 120), (125, 255, 179)]
NAMES = ["AZURE", "GOLD", "CORAL", "MINT"]
LANES = [270, 430, 590, 750, 910]


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY and not RECORD else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H), pygame.HIDDEN)
        pygame.display.set_caption("Azurite Avalanche")
        self.surf = pygame.Surface((W, H))
        self.font = pygame.font.SysFont("dejavusans", 58, bold=True)
        self.mid = pygame.font.SysFont("dejavusans", 36, bold=True)
        self.small = pygame.font.SysFont("dejavusans", 26, bold=True)
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.t = 0.0
        self.score = 0
        self.banked = [0, 0, 0, 0]
        self.lives = 3
        self.plow = 540.0
        self.ramp = 1
        self.gems, self.bits = [], []
        self.spawn = 0.3
        self.flash = 0.0
        self.keys = set()
        random.seed(11)

    def spawn_gem(self):
        c = random.randrange(4)
        self.gems.append({
            "x": float(random.choice(LANES)), "y": 250.0,
            "vy": random.uniform(360, 500), "vx": 0.0, "c": c,
            "rot": random.random() * 6.28, "spin": random.uniform(-4, 4),
            "held": False, "alive": True,
        })

    def burst(self, x, y, col, n=14):
        for _ in range(n):
            a, s = random.random() * 6.28, random.uniform(90, 460)
            self.bits.append([x, y, math.cos(a) * s, math.sin(a) * s, 0.55, col])

    def update(self, dt, auto):
        self.t += dt
        self.flash = max(0.0, self.flash - dt)
        self.spawn -= dt
        if self.spawn <= 0 and len(self.gems) < 7:
            self.spawn_gem()
            self.spawn = random.uniform(0.40, 0.68)
        if auto:
            target, best = None, -1
            for g in self.gems:
                if g["alive"] and not g["held"] and g["y"] > best:
                    best, target = g["y"], g
            if target:
                self.plow += max(-1, min(1, (target["x"] - self.plow) / 36)) * 1040 * dt
                self.ramp = -1 if target["c"] % 2 == 0 else 1
        else:
            if pygame.K_LEFT in self.keys or pygame.K_a in self.keys:
                self.plow -= 900 * dt
            if pygame.K_RIGHT in self.keys or pygame.K_d in self.keys:
                self.plow += 900 * dt
        self.plow = max(230, min(850, self.plow))
        plow_y = 1460
        for g in self.gems:
            if not g["alive"]:
                continue
            g["rot"] += g["spin"] * dt
            if not g["held"]:
                g["y"] += g["vy"] * dt
                if g["y"] >= plow_y - 6 and abs(g["x"] - self.plow) < 112:
                    g["held"] = True
                    g["vx"] = self.ramp * 820
                    g["vy"] = 70
                    g["y"] = plow_y - 20
                elif g["y"] > 1688:
                    g["alive"] = False
                    self.lives = max(0, self.lives - 1)
                    self.burst(g["x"], 1660, (170, 70, 80), 8)
            else:
                g["x"] += g["vx"] * dt
                g["y"] += math.sin(self.t * 8) * 10 * dt
                if (g["vx"] < 0 and g["x"] < 188) or (g["vx"] > 0 and g["x"] > W - 188):
                    g["alive"] = False
                    self.score += 130 + g["c"] * 15
                    self.banked[g["c"]] += 1
                    self.flash = 0.16
                    side = 96 if g["vx"] < 0 else W - 96
                    self.burst(side, 430 + g["c"] * 230, COLS[g["c"]], 18)
        self.gems = [g for g in self.gems if g["alive"]]
        kept = []
        for b in self.bits:
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            b[3] += 280 * dt
            b[4] -= dt
            if b[4] > 0:
                kept.append(b)
        self.bits = kept

    def draw_gem(self, g):
        col = COLS[g["c"]]
        pts = []
        for i in range(6):
            a = g["rot"] + i * math.pi / 3
            rad = 30 if i % 2 == 0 else 16
            pts.append((g["x"] + math.cos(a) * rad, g["y"] + math.sin(a) * rad))
        pygame.draw.polygon(self.surf, col, pts)
        pygame.draw.polygon(self.surf, CREAM, pts, 3)
        pygame.draw.circle(self.surf, CREAM, (int(g["x"]), int(g["y"])), 4)

    def draw(self):
        s = self.surf
        s.fill(NAVY)
        for i in range(6):
            col = TEAL if i % 2 == 0 else AMBER
            base = 300 + i * 150
            pts = [(x, base + math.sin(x * 0.008 + self.t * (0.7 + i * 0.15)) * 42)
                   for x in range(0, W + 1, 36)]
            pygame.draw.lines(s, col, False, pts, 4)
        for i in range(48):
            x = (i * 89 + self.t * (28 + (i % 4) * 14)) % W
            y = (i * 173 + self.t * 90) % H
            pygame.draw.circle(s, (190, 220, 235), (int(x), int(y)), 2)
        for side in (0, 1):
            x0 = 28 if side == 0 else W - 148
            for c in range(4):
                y0 = 330 + c * 230
                pygame.draw.rect(s, INK, (x0, y0, 120, 190), border_radius=18)
                pygame.draw.rect(s, COLS[c], (x0, y0, 120, 190), 4, border_radius=18)
                fill = min(160, self.banked[c] * 18)
                pygame.draw.rect(s, COLS[c], (x0 + 14, y0 + 168 - fill, 92, fill), border_radius=8)
                lab = self.small.render(NAMES[c], True, CREAM)
                s.blit(lab, lab.get_rect(center=(x0 + 60, y0 + 24)))
        pygame.draw.line(s, (48, 82, 118), (200, 280), (200, 1630), 4)
        pygame.draw.line(s, (48, 82, 118), (880, 280), (880, 1630), 4)
        for g in self.gems:
            self.draw_gem(g)
        px, py = self.plow, 1460
        body = [(px - 118, py + 30), (px + 118, py + 30), (px + 96, py - 6), (px - 96, py - 6)]
        pygame.draw.polygon(s, COPPER, body)
        pygame.draw.polygon(s, CREAM, body, 3)
        tip = px + self.ramp * 78
        pygame.draw.polygon(s, TEAL if self.ramp > 0 else AMBER,
                            [(px - 24, py - 6), (px + 24, py - 6), (tip, py - 52)])
        pygame.draw.circle(s, CREAM, (int(px - 48), int(py + 30)), 12)
        pygame.draw.circle(s, CREAM, (int(px + 48), int(py + 30)), 12)
        for b in self.bits:
            pygame.draw.circle(s, b[5], (int(b[0]), int(b[1])), 5)
        title = self.font.render("AZURITE AVALANCHE", True, CREAM)
        s.blit(title, title.get_rect(center=(W // 2, 86)))
        sub = self.small.render("SWEEP  ·  FLIP  ·  BANK", True, TEAL)
        s.blit(sub, sub.get_rect(center=(W // 2, 142)))
        sc = self.mid.render(f"SCORE  {self.score}", True, AMBER)
        s.blit(sc, sc.get_rect(center=(W // 2, 204)))
        lv = self.small.render("LIVES  " + "◆" * max(1, self.lives), True, COLS[2])
        s.blit(lv, lv.get_rect(center=(W // 2, 1696)))
        hint = self.small.render("ARROWS SWEEP    SPACE FLIPS RAMP", True, (170, 196, 214))
        s.blit(hint, hint.get_rect(center=(W // 2, 1764)))
        tag = self.mid.render("x.com/ElbowOS", True, TEAL)
        s.blit(tag, tag.get_rect(center=(W // 2, 1844)))
        if self.flash > 0:
            glow = pygame.Surface((W, H), pygame.SRCALPHA)
            glow.fill((90, 230, 210, int(80 * self.flash / 0.16)))
            s.blit(glow, (0, 0))
        self.screen.blit(s, (0, 0))
        pygame.display.flip()

    def play(self):
        running = True
        while running:
            dt = min(0.05, self.clock.tick(FPS) / 1000)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    self.keys.add(ev.key)
                    if ev.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                        self.ramp *= -1
                    if ev.key == pygame.K_r:
                        self.reset()
                    if ev.key == pygame.K_ESCAPE:
                        running = False
                elif ev.type == pygame.KEYUP:
                    self.keys.discard(ev.key)
            self.update(dt, False)
            self.draw()
        pygame.quit()

    def record(self):
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0", "-an",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            "-preset", "veryfast", "-movflags", "+faststart", OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        frames, dt = FPS * SECS, 1 / FPS
        try:
            for _ in range(frames):
                pygame.event.pump()
                self.update(dt, True)
                self.draw()
                proc.stdin.write(pygame.image.tobytes(self.surf, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1500:]}")
        print("wrote", OUT, "frames", frames)
        pygame.quit()


def main():
    g = Game()
    g.play() if PLAY and not RECORD else g.record()


if __name__ == "__main__":
    main()
