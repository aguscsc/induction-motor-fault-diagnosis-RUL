"""
Broken rotor bar / rotor asymmetry -- field decomposition visualization
-------------------------------------------------------------------------
Decomposes the resultant rotor field into a forward-rotating component
(the healthy field) and a smaller backward-rotating component (induced
by rotor asymmetry, e.g. a broken bar). Their vector sum traces an
ellipse instead of a circle.

Drag the slider to change the backward-to-forward magnitude ratio:
  0%   -> perfect circle   (symmetric, healthy rotor)
  mid  -> ellipse          (mild asymmetry -- the broken-bar case)
  100% -> straight line    (pure pulsation -- the single-phase motor limit)

Run as a plain .py file (not inside a notebook cell) so the slider
responds -- it needs an interactive backend (TkAgg, QtAgg, etc.), which
matplotlib picks automatically on most desktop Python installs. If you
get a static window with no response, try:
    pip install PyQt5
and re-run.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.animation import FuncAnimation

# ----- parameters -----
R_F = 1.0  # forward field magnitude (fixed reference)
OMEGA = np.pi  # angular speed, rad/s -> one revolution per second
FPS = 30

# ----- figure setup -----
fig, ax = plt.subplots(figsize=(6, 6))
plt.subplots_adjust(bottom=0.18)
ax.set_xlim(-2.2, 2.2)
ax.set_ylim(-2.2, 2.2)
ax.set_aspect("equal")
ax.axhline(0, color="0.85", lw=0.8, zorder=0)
ax.axvline(0, color="0.85", lw=0.8, zorder=0)
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)

# locus of the resultant vector's tip (redrawn whenever the slider moves)
theta = np.linspace(0, 2 * np.pi, 300)
(locus_line,) = ax.plot([], [], "--", color="0.6", lw=1)

# the three vectors: forward (teal), backward (coral), resultant (purple)
(forward_arrow,) = ax.plot([], [], color="#1D9E75", lw=2, solid_capstyle="round")
(backward_arrow,) = ax.plot([], [], color="#D85A30", lw=2, solid_capstyle="round")
(resultant_arrow,) = ax.plot([], [], color="#534AB7", lw=2.5, solid_capstyle="round")

ax.plot([], [], color="#1D9E75", lw=2, label="Forward (healthy) field")
ax.plot([], [], color="#D85A30", lw=2, label="Backward field (fault-induced)")
ax.plot([], [], color="#534AB7", lw=2.5, label="Resultant (measured) field")
ax.legend(
    loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=1, frameon=False, fontsize=9
)

title = ax.set_title("")

ax_slider = plt.axes([0.25, 0.05, 0.5, 0.03])
ratio_slider = Slider(ax_slider, "Backward / Forward", 0.0, 1.0, valinit=0.25)


def update_locus(ratio):
    """Redraw the dashed ellipse (or line, or circle) for the given ratio."""
    Rb = ratio * R_F
    a = R_F + Rb  # semi-major axis, along x
    b = max(R_F - Rb, 1e-3)  # semi-minor axis, along y
    locus_line.set_data(a * np.cos(theta), b * np.sin(theta))

    if ratio < 0.03:
        msg = "Perfect circle -- healthy, symmetric rotor"
    elif ratio > 0.95:
        msg = "Collapsed to a line -- pure pulsation (single-phase limit)"
    else:
        msg = f"Ellipse -- rotating, non-uniform field ({ratio * 100:.0f}% backward)"
    title.set_text(msg)


def animate(frame):
    """Advance both vectors by one time step and redraw."""
    ratio = ratio_slider.val
    Rb = ratio * R_F
    t = frame / FPS
    w = OMEGA * t

    # forward vector: origin -> tip, rotating counter-clockwise
    fx, fy = R_F * np.cos(w), R_F * np.sin(w)
    # backward vector: tacked onto the forward tip, rotating the other way
    bx, by = fx + Rb * np.cos(-w), fy + Rb * np.sin(-w)

    forward_arrow.set_data([0, fx], [0, fy])
    backward_arrow.set_data([fx, bx], [fy, by])
    resultant_arrow.set_data([0, bx], [0, by])
    return forward_arrow, backward_arrow, resultant_arrow


ratio_slider.on_changed(update_locus)
update_locus(ratio_slider.val)

anim = FuncAnimation(
    fig, animate, interval=1000 / FPS, blit=False, cache_frame_data=False
)

if __name__ == "__main__":
    plt.show()
