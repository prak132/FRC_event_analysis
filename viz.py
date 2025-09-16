import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

dfs = {y: pd.read_csv(f'{y-2000}data.csv').assign(
    norm_epa=lambda x: pd.to_numeric(x['norm_epa'], errors='coerce'),
    event_name=lambda x: x['event'].str[4:]
).query('norm_epa > 0 and norm_epa.notna()' + (' and event != "2024capt"' if y == 2024 else ''))
for y in [2024, 2025]}

events = [e for e in ['caoc','caph','camb','cave','casf','cala','cada','capt','cabe','caav','cafr'] 
          if e in set(dfs[2024]['event_name']).union(dfs[2025]['event_name'])]

plot_data = [(dfs[year][dfs[year]['event_name'] == event], f'{event}\n{year}', 
              '#d62728' if year == 2024 else '#1f77b4', year)
             for event in events for year in [2024, 2025] 
             if len(dfs[year][dfs[year]['event_name'] == event]) > 0]

fig, ax = plt.subplots(figsize=(18, 10))
plt.style.use('seaborn-v0_8')

bp = ax.boxplot([data['norm_epa'] for data, _, _, _ in plot_data], patch_artist=True, 
                showfliers=True, flierprops=dict(marker='o', markersize=6, alpha=0.7))

for i, (patch, (data, label, color, year)) in enumerate(zip(bp['boxes'], plot_data)):
    patch.set_facecolor(color), patch.set_alpha(0.7)
    q1, q3 = data['norm_epa'].quantile([0.25, 0.75])
    outliers = data[(data['norm_epa'] < q1-1.5*(q3-q1)) | (data['norm_epa'] > q3+1.5*(q3-q1))]
    for _, row in outliers.iterrows():
        ax.annotate(f"Team {row['team_num']}", (i+1, row['norm_epa']), xytext=(5,5), 
                   textcoords='offset points', fontsize=8, ha='left', va='bottom',
                   bbox=dict(boxstyle='round,pad=0.2', fc='pink' if year==2024 else 'lightblue', alpha=0.7),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

ax.set_xticklabels([label for _, label, _, _ in plot_data], rotation=45, ha='right')
ax.legend([Patch(facecolor=c, alpha=0.7) for c in ['#d62728', '#1f77b4']], ['2024', '2025'], loc='upper right')
ax.set(xlabel='Event', ylabel='Normalized EPA', title='Normalized EPA Distribution')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('norm_epa_comparison_combined.png', dpi=300, bbox_inches='tight')
plt.show()