import csv
import glob
import os
import sys

# Usage: python extract.py [year]   (default 2027)
# Combines every Statbotics export in {yy}data/*_team_insights.csv into {yy}data.csv
year = int(sys.argv[1]) if len(sys.argv) > 1 else 2027
yy = year - 2000
input_files = sorted(glob.glob(os.path.join(f'{yy}data', f'{year}*_team_insights.csv')))
if not input_files:
    sys.exit(f'No {year}*_team_insights.csv files found in {yy}data/')

# Statbotics exports (2024-2025) use norm_epa; FSM exports (2026) use fsm
with open(input_files[0], mode='r', encoding='utf-8-sig') as f:
    metric = 'norm_epa' if 'norm_epa' in next(csv.reader(f)) else 'fsm'

with open(f'{yy}data.csv', mode='w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['event', 'team_num', metric])
    for input_filename in input_files:
        event_name = os.path.basename(input_filename).split('_')[0]
        with open(input_filename, mode='r', encoding='utf-8-sig') as infile:
            for row in csv.DictReader(infile):
                writer.writerow([event_name, row['num'].strip('"'), row[metric]])

print(f'Wrote {len(input_files)} events ({metric}) to {yy}data.csv')
