import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Usage: python viz.py [year ...]   (default: every year from 2024-2027 with a {yy}data.csv)
# Years are grouped by metric: Statbotics norm_epa years share one graph, FSM years get their own
# (FSM's scale is season-specific, so it can't share an axis with other years).
YEAR_COLORS = {2024: '#d62728', 2025: '#1f77b4', 2026: '#2ca02c', 2027: '#ff7f0e'}
LABEL_COLORS = {2024: 'pink', 2025: 'lightblue', 2026: 'lightgreen', 2027: 'moccasin'}
EXCLUDED_EVENTS = {'2024capt'}
EVENT_ORDER = ['caoc','caph','camb','cave','casf','cala','cada','capt','cabe','caav','cafr']
METRICS = {'norm_epa': ('Normalized EPA', 'norm_epa_comparison_combined.png'),
           'fsm': ('FSM', 'fsm_comparison_combined.png')}

years = [int(y) for y in sys.argv[1:]] or [y for y in YEAR_COLORS if os.path.exists(f'{y-2000}data.csv')]
for y in [y for y in years if not os.path.exists(f'{y-2000}data.csv')]:
    print(f'Skipping {y}: {y-2000}data.csv not found (run extract.py {y} first)')
    years.remove(y)
if not years:
    sys.exit('No data files found')

def load(year):
    df = pd.read_csv(f'{year-2000}data.csv')
    metric = df.columns[2]
    df = df.assign(value=pd.to_numeric(df[metric], errors='coerce'), event_name=df['event'].str[4:])
    return metric, df.query('value > 0 and value.notna() and event not in @EXCLUDED_EVENTS')

def plot(dfs, metric):
    label, outfile = METRICS[metric]
    all_events = set().union(*(df['event_name'] for df in dfs.values()))
    events = [e for e in EVENT_ORDER if e in all_events] + sorted(all_events - set(EVENT_ORDER))

    plot_data = [(dfs[year][dfs[year]['event_name'] == event], f'{event}\n{year}', YEAR_COLORS[year], year)
                 for event in events for year in dfs
                 if len(dfs[year][dfs[year]['event_name'] == event]) > 0]

    fig, ax = plt.subplots(figsize=(max(18, len(plot_data) * 0.8), 10))
    plt.style.use('seaborn-v0_8')

    bp = ax.boxplot([data['value'] for data, _, _, _ in plot_data], patch_artist=True,
                    showfliers=True, flierprops=dict(marker='o', markersize=6, alpha=0.7))

    for i, (patch, (data, _, color, year)) in enumerate(zip(bp['boxes'], plot_data)):
        patch.set_facecolor(color), patch.set_alpha(0.7)
        q1, q3 = data['value'].quantile([0.25, 0.75])
        outliers = data[(data['value'] < q1-1.5*(q3-q1)) | (data['value'] > q3+1.5*(q3-q1))]
        for _, row in outliers.iterrows():
            ax.annotate(f"Team {row['team_num']}", (i+1, row['value']), xytext=(5,5),
                       textcoords='offset points', fontsize=8, ha='left', va='bottom',
                       bbox=dict(boxstyle='round,pad=0.2', fc=LABEL_COLORS[year], alpha=0.7),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    ax.set_xticklabels([l for _, l, _, _ in plot_data], rotation=45, ha='right')
    ax.legend([Patch(facecolor=YEAR_COLORS[y], alpha=0.7) for y in dfs], [str(y) for y in dfs], loc='upper right')
    ax.set(xlabel='Event', ylabel=label, title=f'{label} Distribution')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(outfile, dpi=300, bbox_inches='tight')
    print(f'Saved {outfile}')

by_metric = {}
for y in years:
    metric, df = load(y)
    by_metric.setdefault(metric, {})[y] = df
for metric, dfs in by_metric.items():
    plot(dfs, metric)
plt.show()
