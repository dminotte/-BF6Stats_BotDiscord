import discord
from discord.ext import commands
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import os, json, datetime

# --- CONFIG ---
TOKEN = "TON_TOKEN_DISCORD_ICI"  # 🔒 Remplace par ton token
BANNER_BG = "bannerBackgroundImage.webp"
LOGO_BF6 = "logo_bf6.webp"
PLATFORMS = ["pc", "xboxone", "ps4", "xboxseries", "ps5", "xbox", "psn"]

# --- DISCORD SETUP ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- FONCTIONS UTILES ---
def load_font(font_list, size):
    for font_name in font_list:
        if os.path.exists(font_name):
            return ImageFont.truetype(font_name, size)
    return ImageFont.truetype("arial.ttf", size)

def draw_text_with_shadow(draw, position, text, font, fill, shadow):
    x, y = position
    draw.text((x+2, y+2), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)

def fetch_player_data(name: str, platform: str):
    url = "https://api.gametools.network/bf6/stats/"
    params = {"name": name, "platform": platform, "categories": ["multiplayer"]}
    cache_file = f"last_stats_{name}.json"

    data, api_ok = None, False
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("hasResults", False):
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                api_ok = True
            else:
                print(f"[WARN] Aucun résultat pour {name}.")
        else:
            print(f"[WARN] API {resp.status_code} pour {name}.")
    except Exception as e:
        print(f"[ERR] API erreur : {e}")

    if not api_ok and os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"[CACHE] Chargement depuis le cache : {cache_file}")
    elif not api_ok:
        print(f"[FATAL] Aucun cache disponible pour {name}")
        return None, False

    return data, api_ok

def generate_banner(data, api_ok: bool, player_name: str):
    cache_time_text = None
    cache_file = f"last_stats_{player_name}.json"
    if not api_ok and os.path.exists(cache_file):
        cache_time = datetime.datetime.fromtimestamp(os.path.getmtime(cache_file))
        cache_time_text = cache_time.strftime("Last update: %Y-%m-%d %H:%M:%S")

    stats = {
        "K/D": data.get("killDeath", "N/A"),
        "Kills": data.get("kills", "N/A"),
        "Deaths": data.get("deaths", "N/A"),
        "Wins": data.get("wins", "N/A"),
        "Loses": data.get("loses", "N/A"),
        "Accuracy": data.get("accuracy", "N/A"),
        "BestClass": data.get("bestClass", "N/A"),
        "Revives": data.get("revives", "N/A"),
        "Kill Assists": data.get("killAssists", "N/A"),
        "Time Played": data.get("timePlayed", "N/A")
    }

    best_class_index = data.get("bestClass")
    classes = data.get("classes", [])
    best_class_data = None

    if isinstance(best_class_index, int) and 0 <= best_class_index < len(classes):
        best_class_data = classes[best_class_index]
        kd_best = best_class_data.get("killDeath")
        if kd_best and kd_best > 0:
            stats["K/D"] = kd_best
            stats["Kills"] = best_class_data.get("kills", "N/A")
            stats["Deaths"] = best_class_data.get("deaths", "N/A")
            stats["BestClass"] = best_class_data.get("className", "N/A")

    # --- Création de la bannière ---
    banner_width, banner_height = 800, 200
    background = Image.open(BANNER_BG).convert("RGBA").resize((banner_width, banner_height))
    overlay = Image.new("RGBA", (banner_width, banner_height), (0, 0, 0, 120))
    banner = Image.alpha_composite(background, overlay)
    draw = ImageDraw.Draw(banner)

    stats_font = load_font(["squada-One.ttf", "impact.ttf", "Russo_One.ttf"], 24)
    player_font = ImageFont.truetype("arial.ttf", 28)
    text_color = (240, 240, 240, 255)
    shadow_color = (0, 0, 0, 200)

    # Logo
    try:
        logo = Image.open(LOGO_BF6).convert("RGBA")
        logo_w = 150
        logo_h = int(logo.height * (logo_w / logo.width))
        logo = logo.resize((logo_w, logo_h))
        banner.paste(logo, (20, 20), logo)
    except:
        logo_w = 0

    stats_x = 20 + logo_w + 20
    stats_y = 20
    stats_width = banner_width - stats_x - 20
    stats_height = 120

    blurred_bg = banner.filter(ImageFilter.GaussianBlur(6))
    frosted = blurred_bg.crop((stats_x, stats_y, stats_x + stats_width, stats_y + stats_height))
    mask = Image.new("L", (stats_width, stats_height), 90)
    banner.paste(frosted, (stats_x, stats_y), mask)
    draw = ImageDraw.Draw(banner)

    col_width = stats_width // 3
    line_spacing = 5
    stats_list = [(k, v) for k, v in stats.items() if k != "Time Played"]

    for col in range(3):
        x = stats_x + col * col_width
        y = stats_y + 10
        for i in range(col, len(stats_list), 3):
            key, value = stats_list[i]
            text = f"{key}: {value}"
            draw_text_with_shadow(draw, (x, y), text, stats_font, text_color, shadow_color)
            y += stats_font.size + line_spacing

    # Temps de jeu
    time_text = f"Time Played: {stats['Time Played']}"
    bbox = draw.textbbox((0, 0), time_text, font=stats_font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x_tp = banner_width - text_w - 20
    y_tp = banner_height - text_h - 10
    draw_text_with_shadow(draw, (x_tp, y_tp), time_text, stats_font, text_color, shadow_color)

    # Nom du joueur
    player_text = player_name + (" [OFFLINE]" if not api_ok else "")
    bbox = draw.textbbox((0, 0), player_text, font=player_font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x_pn = 20
    y_pn = y_tp
    player_color = (200, 220, 255, 255) if api_ok else (255, 120, 120, 255)
    draw_text_with_shadow(draw, (x_pn, y_pn), player_text, player_font, player_color, shadow_color)

    # Icône de la best class
    if best_class_data and best_class_data.get("image"):
        try:
            icon_url = best_class_data["image"]
            r = requests.get(icon_url, timeout=10)
            if r.status_code == 200:
                icon = Image.open(BytesIO(r.content)).convert("RGBA").resize((40, 40))
                banner.paste(icon, (x_pn + text_w + 10, y_pn - 5), icon)
        except:
            pass

    # Date du cache
    if cache_time_text:
        small_font = ImageFont.truetype("arial.ttf", 18)
        draw_text_with_shadow(draw, (x_pn, y_pn + text_h + 5), cache_time_text, small_font, (200,200,200,255), shadow_color)

    out_path = f"bf6_banner_{player_name}.png"
    banner.save(out_path)
    return out_path


# --- COMMANDE DISCORD ---
@bot.command(name="BF6Stat")
async def bf6stat(ctx, player_name: str = None, platform: str = "pc"):
    if not player_name:
        await ctx.send("⚠️ Utilisation : `!BF6Stat <pseudo> <plateforme>` (ex: `!BF6Stat Doud0u pc`)")
        return

    platform = platform.lower()
    if platform not in PLATFORMS:
        await ctx.send(f"❌ Plateforme invalide. Options : {', '.join(PLATFORMS)}")
        return

    msg = await ctx.send(f"🔍 Recherche des stats pour **{player_name}** sur `{platform}`...")

    data, api_ok = fetch_player_data(player_name, platform)
    if not data:
        await msg.edit(content=f"❌ Impossible de récupérer les stats de `{player_name}` sur `{platform}` (API indisponible et aucun cache trouvé).")
        return

    path = generate_banner(data, api_ok, player_name)
    file = discord.File(path, filename=os.path.basename(path))
    await msg.delete()
    await ctx.send(file=file)


# --- LANCEMENT ---
bot.run(TOKEN)
