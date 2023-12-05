# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 16:24:09 2023

@author: cariefrantz

This code reads in an abundance table of different species (could also use an
ASV table, but this example uses Minion output), calculates a Bray-Curtis
distance matrix, and displays a 3D PCOA plot. Code generated with help from
ChatGPT.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial.distance import braycurtis, pdist, squareform
from mpl_toolkits.mplot3d import Axes3D
from sklearn.manifold import MDS


filepath = 'abundance_table_species.tsv'
samples = ['A1-T','A1-B','A2-T','B2-T'] # Samples to include in the analysis (nseqs>50)

# Load abundance table (replace 'abundance_table.csv' with your file)
abundance_df = pd.read_csv(filepath, index_col=0, sep='\t', header=0)


# Normalize abundance data
normalized_abundance = abundance_df[samples].div(abundance_df[samples].sum())

# Calculate Bray-Curtis distance matrix
distance_matrix = pdist(normalized_abundance.T,'braycurtis')
distance_matrix = squareform(distance_matrix)


# Display and save the distance matrix
print(distance_matrix)
pd.DataFrame(distance_matrix).to_csv('braycurtis.csv')

# Do PCOA
# Perform MDS (Multidimensional Scaling, a common method for PCoA)
mds = MDS(n_components=3, dissimilarity='precomputed')
coordinates = mds.fit_transform(distance_matrix)

# Plot 3D visualization
fig = plt.figure(figsize=(6,6))
ax = fig.add_subplot(111, projection='3d')

# Scatter plot the coordinates and label the points
for i, (x, y, z) in enumerate(coordinates):
    ax.scatter(x, y, z, label=samples[i])
    ax.text(x, y, z, samples[i], color='black')  # Adding text labels

# Set labels for axes
ax.set_xlabel('PC1')
ax.set_ylabel('PC2')
ax.set_zlabel('PC3')

plt.title('PCoA Visualization in 3D')
plt.show()

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Get the shape of the distance matrix
n = distance_matrix.shape[0]

# Generate x, y, z coordinates for the plot
x = []
y = []
z = []
for i in range(n):
    for j in range(i + 1, n):  # Adjusted the range to avoid duplicate pairs
        x.append(i)
        y.append(j)
        z.append(distance_matrix[i, j])

# Plot the points
ax.scatter(x, y, z)

# Set labels for axes
ax.set_xlabel('Point A')
ax.set_ylabel('Point B')
ax.set_zlabel('Distance')

plt.title('3D Visualization of Distance Matrix')
plt.show()