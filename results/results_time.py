import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Read the CSV file into a pandas DataFrame
df = pd.read_csv('results_all.csv', header=None, delimiter='\t')

# Assign column names
df.columns = ['Run', 'DimHD', 'NumFs', 'Time', 'Rule 1', 'Rule 2', 'Rule 3']

# Get unique dimensions
dimensions = sorted(df['DimHD'].unique())

# Initialize a figure and axis
fig, ax = plt.subplots(figsize=(10, 6))

# Create a secondary y-axis for the third column
ax2 = ax.twinx()

# Iterate over unique dimensions and plot the whisker plot for each
for i,dim in enumerate(dimensions):
    pos = i*2
    # Times
    data_time = df[df['DimHD'] == dim]['Time']
    ax.boxplot(data_time, positions=[pos-0.25], widths=0.4, showfliers=False, patch_artist=True, boxprops=dict(facecolor='blue', color='blue'))
    # NumFs
    data_numf = df[df['DimHD'] == dim]['NumFs']
    ax2.boxplot(data_numf, positions=[pos+0.25], widths=0.4, showfliers=False, patch_artist=True, boxprops=dict(facecolor='red', color='red'))

# Set labels and title
ax.set_xlabel('HD dimension')
ax.set_ylabel('Time (s) (log scale)')
ax.set_title('Time distribution of 100 random walks from f_infimum to f_supremum')

# Set labels and title for secondary y-axis
ax2.set_ylabel('Trace size (# functions) (log scale)')
ax2.grid(False)

# Set logarithmic scale for the y-axis
ax.set_yscale('log')
ax2.set_yscale('log')

# Adjust x-axis ticks and labels
ax.set_xticks(range(0, len(dimensions) * 2, 2))
ax.set_xticklabels(dimensions)

# Show legend
plt.legend([Patch(facecolor='blue', edgecolor='blue'), Patch(facecolor='red', edgecolor='red')],\
        ['Time', 'Trace size'], loc='lower right')

# Show the plot
plt.grid(True)
#plt.xticks(dimensions)
plt.tight_layout()

# Save the plot in PDF format
plt.savefig('results_time.pdf')

#plt.show()

