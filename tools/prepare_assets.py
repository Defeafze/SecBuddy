"""
Einmaliges Script: Hintergrund aus dem Logo-Bild entfernen,
PNG + ICO in assets/ speichern.
"""

import pathlib
from PIL import Image
import numpy as np

SRC  = pathlib.Path(__file__).parent.parent / "picture" / "ChatGPT Image 22. Juni 2025, 20_45_57.png"
OUT  = pathlib.Path(__file__).parent.parent / "assets"
OUT.mkdir(exist_ok=True)

img = Image.open(SRC).convert("RGBA")
data = np.array(img, dtype=np.float32)

# Hintergrundfarbe vom Eckpixel nehmen (oben links)
bg_r, bg_g, bg_b = data[0, 0, :3]

# Alle Pixel die nahe am Hintergrund sind → transparent
dist = np.sqrt(
    (data[:, :, 0] - bg_r) ** 2 +
    (data[:, :, 1] - bg_g) ** 2 +
    (data[:, :, 2] - bg_b) ** 2
)
threshold = 40
mask = dist < threshold

# Weiche Kanten: Alpha graduell setzen
alpha = np.where(mask, 0, 255).astype(np.uint8)
# Zweite Runde: etwas größerer Threshold → halbtransparent (Anti-Aliasing)
soft_mask = (dist >= threshold) & (dist < threshold + 25)
alpha[soft_mask] = ((dist[soft_mask] - threshold) / 25 * 255).astype(np.uint8)

result = np.array(img)
result[:, :, 3] = alpha
out_img = Image.fromarray(result, "RGBA")

# PNG für Sidebar (64×64)
logo_path = OUT / "logo.png"
out_img.resize((64, 64), Image.LANCZOS).save(logo_path)
print(f"Gespeichert: {logo_path}")

# Größere PNG für Window-Icon
logo_big_path = OUT / "logo_256.png"
out_img.resize((256, 256), Image.LANCZOS).save(logo_big_path)
print(f"Gespeichert: {logo_big_path}")

# ICO mit mehreren Größen für Taskleiste
ico_path = OUT / "icon.ico"
sizes = [(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]
icons = [out_img.resize(s, Image.LANCZOS) for s in sizes]
icons[0].save(ico_path, format="ICO", sizes=[(s[0], s[1]) for s in sizes],
              append_images=icons[1:])
print(f"Gespeichert: {ico_path}")
print("Fertig!")
