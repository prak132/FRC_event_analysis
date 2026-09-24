import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Usage: python viz.py [year ...]   (default: every year from 2024-2027 with a {yy}data.csv)
YEAR_COLORS = {2024: '#d62728', 2025: '#1f77b4', 2026: '#2ca02c', 2027: '#ff7f0e'}
LABEL_COLORS = {2024: 'pink', 2025: 'lightblue', 2026: 'lightgreen', 2027: 'moccasin'}
EXCLUDED_EVENTS = {'2024capt'}
EVENT_ORDER = ['caoc','caph','camb','cave','casf','cala','cada','capt','cabe','caav','cafr']

years = [int(y) for y in sys.argv[1:]] or [y for y in YEAR_COLORS if os.path.exists(f'{y-2000}data.csv')]
for y in [y for y in years if not os.path.exists(f'{y-2000}data.csv')]:
    print(f'Skipping {y}: {y-2000}data.csv not found (run extract.py {y} first)')
    years.remove(y)
if not years:
    sys.exit('No data files found')

dfs = {y: pd.read_csv(f'{y-2000}data.csv').assign(
    norm_epa=lambda x: pd.to_numeric(x['norm_epa'], errors='coerce'),
    event_name=lambda x: x['event'].str[4:]
).query('norm_epa > 0 and norm_epa.notna() and event not in @EXCLUDED_EVENTS')
for y in years}

all_events = set().union(*(df['event_name'] for df in dfs.values()))
events = [e for e in EVENT_ORDER if e in all_events] + sorted(all_events - set(EVENT_ORDER))

plot_data = [(dfs[year][dfs[year]['event_name'] == event], f'{event}\n{year}', YEAR_COLORS[year], year)
             for event in events for year in years
             if len(dfs[year][dfs[year]['event_name'] == event]) > 0]

fig, ax = plt.subplots(figsize=(max(18, len(plot_data) * 0.8), 10))
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
                   bbox=dict(boxstyle='round,pad=0.2', fc=LABEL_COLORS[year], alpha=0.7),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

ax.set_xticklabels([label for _, label, _, _ in plot_data], rotation=45, ha='right')
ax.legend([Patch(facecolor=YEAR_COLORS[y], alpha=0.7) for y in years], [str(y) for y in years], loc='upper right')
ax.set(xlabel='Event', ylabel='Normalized EPA', title='Normalized EPA Distribution')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('norm_epa_comparison_combined.png', dpi=300, bbox_inches='tight')
plt.show()
