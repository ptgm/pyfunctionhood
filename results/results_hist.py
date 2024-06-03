import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read the TXT file into a pandas DataFrame
df = pd.read_csv('results_all.csv', header=None, delimiter='\t')

# Assign column names and rename columns
df.columns = ['Run', 'DimHD', 'NumFs', 'Time', 'Rule 1', 'Rule 2', 'Rule 3']

# Group by dimension and compute the average of the last three columns
avg_data = df.groupby('DimHD')[['Rule 1', 'Rule 2', 'Rule 3']].mean()
std_data = df.groupby('DimHD')[['Rule 1', 'Rule 2', 'Rule 3']].std()

# Get unique dimensions
dimensions = avg_data.index

# Initialize a figure and axis
fig, ax = plt.subplots(figsize=(10, 6))

# Plot stacked bar chart for each dimension with error bars
bar_width = 0.35
indices = np.arange(len(dimensions))
bottom = None

# Iterate over each column and plot stacked bars with error bars
for i, column in enumerate(['Rule 1', 'Rule 2', 'Rule 3']):
    values = avg_data[column]
    errors = std_data[column]
    if bottom is None:
        ax.bar(indices, values, bar_width, label=column, yerr=errors, capsize=3, capstyle='projecting', linewidth=0.5)
        bottom = values
    else:
        ax.bar(indices, values, bar_width, label=column, bottom=bottom, yerr=errors, capsize=3, capstyle='projecting', linewidth=0.5)
        bottom += values

# Set labels and title
ax.set_xlabel('HD dimension')
ax.set_ylabel('Number of parents per Rule')
ax.set_title('Number of generated parents per rule from f_infimum to f_supremum')
ax.set_xticks(indices)
ax.set_xticklabels(dimensions)

# Add horizontal gridlines
ax.yaxis.grid(True)

# Add legend
ax.legend()

# Show the plot
plt.tight_layout()

# Save the plot in PDF format
plt.savefig('results_hist.pdf')


