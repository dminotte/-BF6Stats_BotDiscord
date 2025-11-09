import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import os

# --- CONFIGURATION ---
PLAYER_NAME = "Doud0u"
PLATFORM = "pc"

# --- APPEL API ---
url = f"https://api.gametools.network/bf6/stats/"
params = {
    "name": PLAYER_NAME,
    "platform": PLATFORM,
    "categories": ["multiplayer"]
}

response = requests.get(url, params=params)
if response.status_code != 200:
    raise Exception(f"Erreur API : code {response.status_code}")

data = response.json()
if not data.get("hasResults", False):
    raise Exception(f"Erreur API : Stats introuvables pour ce joueur.")

stats = {
    "K/D": data.get("killDeath", "N/A"),
    "Kills": data.get("kills", "N/A"),
    "Deaths": data.get("deaths", "N/A"),
    "Wins": data.get("wins", "N/A"),
    "Loses": data.get("loses", "N/A"),
    "Accuracy": data.get("accuracy", "N/A"),
    "Class": data.get("bestClass", "N/A"),
    "Revives": data.get("revives", "N/A"),
    "Kill Assists": data.get("killAssists", "N/A"),
    "Time Played": data.get("timePlayed", "N/A")
}

# --- DIMENSIONS BANNIÈRE ---
banner_width = 800
banner_height = 200

# --- CHARGER IMAGE DE FOND ---
try:
    background = Image.open("bannerBackgroundImage.webp").convert("RGBA")
    background = background.resize((banner_width, banner_height))
except Exception as e:
    raise Exception(f"Impossible de charger l'image de fond : {e}")

# --- AJOUTER UN VOILE SOMBRE GLOBAL POUR LISIBILITÉ ---
overlay = Image.new("RGBA", (banner_width, banner_height), (0, 0, 0, 120))
banner = Image.alpha_composite(background, overlay)
draw = ImageDraw.Draw(banner)

# --- FONCTIONS UTILES ---
def load_font(font_list, size):
    """Charge la première police trouvée dans la liste."""
    for font_name in font_list:
        if os.path.exists(font_name):
            return ImageFont.truetype(font_name, size)
    return ImageFont.truetype("arial.ttf", size)

def draw_text_with_shadow(draw, position, text, font, fill, shadow):
    x, y = position
    draw.text((x+2, y+2), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)

# --- POLICES ---
# Police pour les statistiques — complète, lisible, un peu technique
stats_font = load_font(
    ["squada-One.ttf", "impact.ttf", "Russo_One.ttf"],
    24
)

# Police pour le joueur — plus lisible, casse respectée
player_font = ImageFont.truetype("arial.ttf", 28)

text_color = (240, 240, 240, 255)
shadow_color = (0, 0, 0, 200)

# --- LOGO ---
try:
    logo = Image.open("logo_bf6.webp").convert("RGBA")
    logo_width = 150
    logo_height = int(logo.height * (logo_width / logo.width))
    logo = logo.resize((logo_width, logo_height))
    banner.paste(logo, (20, 20), logo)
except Exception as e:
    print(f"Impossible de charger le logo : {e}")
    logo_width = 0

# --- COORDONNÉES DE BASE ---
stats_x = 20 + logo_width + 20
stats_y = 20
stats_width = banner_width - stats_x - 20
stats_height = 120

# --- EFFET FROSTED GLASS DERRIÈRE LES STATS ---
blurred_bg = banner.filter(ImageFilter.GaussianBlur(6))
frosted = blurred_bg.crop((stats_x, stats_y, stats_x + stats_width, stats_y + stats_height))
mask = Image.new("L", (stats_width, stats_height), 90)
banner.paste(frosted, (stats_x, stats_y), mask)

draw = ImageDraw.Draw(banner)

# --- DESSINER LES STATS ---
col_width = stats_width // 3
line_spacing = 5
stats_list = [(k, v) for k, v in stats.items() if k != "Time Played"]

for col in range(3):
    x = stats_x + col * col_width
    y = stats_y + 10
    for i in range(col, len(stats_list), 3):
        key, value = stats_list[i]
        text = f"{key}: {value}"  # les ":" s’afficheront maintenant
        draw_text_with_shadow(draw, (x, y), text, stats_font, text_color, shadow_color)
        y += stats_font.size + line_spacing

# --- TIME PLAYED (bas droite) ---
time_played_text = f"Time Played: {stats['Time Played']}"
bbox = draw.textbbox((0, 0), time_played_text, font=stats_font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x_tp = banner_width - text_width - 20
y_tp = banner_height - text_height - 10

# petit flou local
blurred_bg = banner.filter(ImageFilter.GaussianBlur(6))
frosted = blurred_bg.crop((x_tp - 10, y_tp - 5, x_tp + text_width + 10, y_tp + text_height + 5))
mask = Image.new("L", (text_width + 20, text_height + 10), 90)
banner.paste(frosted, (x_tp - 10, y_tp - 5), mask)

draw_text_with_shadow(draw, (x_tp, y_tp), time_played_text, stats_font, text_color, shadow_color)

# --- NOM DU JOUEUR (bas gauche) ---
player_name_text = PLAYER_NAME  # garde la casse originale
bbox = draw.textbbox((0, 0), player_name_text, font=player_font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x_pn = 20
y_pn = y_tp

# flou local
blurred_bg = banner.filter(ImageFilter.GaussianBlur(6))
frosted = blurred_bg.crop((x_pn - 10, y_pn - 5, x_pn + text_width + 10, y_pn + text_height + 5))
mask = Image.new("L", (text_width + 20, text_height + 10), 90)
banner.paste(frosted, (x_pn - 10, y_pn - 5), mask)

player_color = (200, 220, 255, 255)
draw_text_with_shadow(draw, (x_pn, y_pn), player_name_text, player_font, player_color, shadow_color)

# --- ENREGISTRER ---
banner.save("bf6_banner.png")
print("✅ Bannière générée avec succès : bf6_banner.png")
print("Police utilisée pour les stats :", stats_font.path)
print("Police utilisée pour le joueur :", player_font.path)