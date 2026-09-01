# Published with the data package for 'Understanding Noise Pollution in Boulder'
# (The Quiet Enjoyment Project, September 2026). Run from the package root:
# inputs are read from ./data, outputs written to ./data and ./figures.
# Health impacts by volume: WHO Night Noise Guidelines dose bands + legal limits
# + the party range. v2 layout: headers inside bands, staggered annotations.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ASSETS = "./figures"
INK = "#1C2B39"; MUTE = "#6B6353"; DARKBROWN = "#6b2d0e"

fig, ax = plt.subplots(figsize=(10.2, 5.2), dpi=200)
ax.set_xlim(24, 96); ax.set_ylim(-4.6, 4.2); ax.axis("off")

# ---- the dose bar (y in data coords: -0.5 .. 0.5) ----
BANDS = [
    (24, 30, "#E9F0E4", "<30", INK),
    (30, 40, "#F3E9CE", "30–40 dB", INK),
    (40, 55, "#E5C99B", "40–55 dB", INK),
    (55, 96, "#BE8449", "55+ dB", "white"),
]
for a, b, col, lab, tc in BANDS:
    ax.add_patch(Rectangle((a, -0.5), b - a, 1.0, color=col, zorder=1))
    ax.text((a + b)/2, 0, lab, ha="center", va="center", fontsize=11.5,
            fontweight="bold", color=tc, zorder=3)
for x in (30, 40, 55):
    ax.plot([x, x], [-0.5, 0.5], color="white", lw=1.4, zorder=2)

# ---- effect descriptions, two staggered rows with leader lines ----
EFF = [
    (27,   2.55, "no observed effect on sleep"),
    (35,   1.30, "body movements, awakenings begin;\nvulnerable groups affected"),
    (47.5, 2.55, "adverse health effects: sleep structure\naltered, environmental insomnia (WHO)"),
    (73,   1.30, "increasingly dangerous: cardiovascular risk\nrises; much of the population highly disturbed"),
]
for x, y, txt in EFF:
    ax.text(x, y + 0.18, txt, ha="center", va="bottom", fontsize=8.8, color=INK)
    ax.plot([x, x], [0.55, y + 0.08], color="#C9BFA8", lw=0.9, zorder=0)

# ---- reference sounds below ----
REFS = [(30, "whisper"), (40, "quiet\nlibrary"), (50, "quiet\noffice"),
        (60, "conversation"), (70, "vacuum\ncleaner"), (85, "loud party\ncore")]
for x, lab in REFS:
    ax.plot(x, -0.66, marker="|", ms=8, color=MUTE)
    ax.text(x, -0.88, lab, ha="center", va="top", fontsize=8, color=MUTE)

# ---- legal limits, fanned labels ----
LEGAL = [(45, 35.5, "State night limit,\namplified bass (7 p.m.)"),
         (50, 50.0, "State & Boulder\nnight limit (11 p.m.)"),
         (55, 64.5, "State & Boulder\nday limit")]
for x, lx, lab in LEGAL:
    ax.annotate("", xy=(x, -0.62), xytext=(lx, -2.7),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2,
                                connectionstyle="arc3,rad=0"))
    ax.text(lx, -2.85, lab, ha="center", va="top", fontsize=8.8,
            color=INK, fontweight="bold")

# ---- the party range ----
ax.annotate("", xy=(70, 3.62), xytext=(90, 3.62),
            arrowprops=dict(arrowstyle="<->", color=DARKBROWN, lw=1.6))
ax.text(80, 3.78, "a loud house party at the property line: typically 70–90 dB",
        ha="center", va="bottom", fontsize=10.5, color=DARKBROWN,
        fontweight="bold", style="italic")

ax.set_title("What the volume does — the WHO night-noise dose bands",
             fontsize=13.5, color=INK, fontweight="bold", loc="left", pad=8)
ax.text(24, -4.5, "Bands: WHO Night Noise Guidelines (nighttime outdoor levels). Party range illustrative — Boulder deploys no noise monitoring, so no measured record exists.",
        fontsize=7.8, color=MUTE, style="italic")
plt.tight_layout()
plt.savefig(f"{ASSETS}/chart_volume_health.png", facecolor="white")
print("volume-health chart v2 saved")
