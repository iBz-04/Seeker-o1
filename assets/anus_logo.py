import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Ellipse
from matplotlib.colors import LinearSegmentedColormap

# Set up the figure
fig, ax = plt.subplots(figsize=(10, 10))
ax.set_aspect('equal')
ax.axis('off')

# Create a custom colormap for the gradient background
colors = [(0.8, 0.4, 0.6), (0.6, 0.2, 0.5)]  # Pink to purple gradient
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors, N=100)

# Create a circular background with gradient
circle_bg = Circle((0.5, 0.5), 0.45, transform=ax.transAxes, 
                  color='white', zorder=0)
ax.add_patch(circle_bg)

# Create the main shape (stylized "A" that resembles a peach)
# First half of the "A"
ellipse1 = Ellipse((0.4, 0.5), 0.4, 0.7, angle=-20, 
                  color=colors[0], alpha=0.9, zorder=1)
ax.add_patch(ellipse1)

# Second half of the "A"
ellipse2 = Ellipse((0.6, 0.5), 0.4, 0.7, angle=20, 
                  color=colors[1], alpha=0.9, zorder=1)
ax.add_patch(ellipse2)

# Add a small circle at the top to complete the "A"
circle_top = Circle((0.5, 0.8), 0.08, color=(0.7, 0.3, 0.5), zorder=2)
ax.add_patch(circle_top)

# Add a horizontal line to represent the crossbar of the "A"
ax.plot([0.35, 0.65], [0.5, 0.5], color='white', linewidth=8, zorder=3)

# Add AI-themed elements (circuit-like lines)
for i in range(5):
    angle = np.pi * 2 * i / 5
    x = 0.5 + 0.5 * np.cos(angle)
    y = 0.5 + 0.5 * np.sin(angle)
    ax.plot([0.5, x], [0.5, y], color='white', linewidth=1, alpha=0.5, zorder=4)

# Set the limits
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

# Save the logo
plt.savefig('/home/ubuntu/anus-ai-project/assets/anus_logo.png', 
           dpi=300, bbox_inches='tight', transparent=True)
plt.savefig('/home/ubuntu/anus-ai-project/assets/anus_logo_small.png', 
           dpi=100, bbox_inches='tight', transparent=True)

print("Logo created and saved to assets directory")
