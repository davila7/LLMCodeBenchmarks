import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Data configuration
theta = np.linspace(0, 2 * np.pi, 100)
z = np.linspace(-2, 2, 100)
r = z**2 + 1

# Parametric coordinates
x = r * np.sin(theta)
y = r * np.cos(theta)

# Create mesh for the plot
X, Z = np.meshgrid(x, z)
Y, _ = np.meshgrid(y, z)

# Create 3D figure
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Generate an amazing plot with colors
colors = np.sin(Z) * np.cos(X)
ax.plot_surface(X, Y, Z, facecolors=plt.cm.viridis(colors), rstride=1, cstride=1, alpha=0.9, edgecolor='none')

# Plot customization
ax.set_title("3D Plot", fontsize=16, fontweight='bold')
ax.set_xlabel("X Axis")
ax.set_ylabel("Y Axis")
ax.set_zlabel("Z Axis")
ax.view_init(elev=30, azim=45)

plt.show()