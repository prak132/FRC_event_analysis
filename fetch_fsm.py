import csv
import json
import os
import sys
import urllib.request

# Usage: FSM_API_KEY=... python fetch_fsm.py
# Downloads FSM team tables for every 2026 FIRST California district event
# (including the state championships) into 26data/{event}_team_insights.csv
API = 'https://fsm846.vercel.app/api/v1'
DISTRICT = 'FIRST California'
FIELDS = ['num', 'rank', 'fsm', 'fuel', 'climb', 'auto', 'penalty', 'defense_score']

key = os.environ.get('FSM_API_KEY') or sys.exit('Set FSM_API_KEY')

def get(path):
    req = urllib.request.Request(API + path, headers={'X-API-Key': key})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)['data']

events = [e for e in get('/events?state_prov=CA&page_size=100') if e['district'] == DISTRICT]
os.makedirs('26data', exist_ok=True)
for event in events:
    table = get(f"/events/{event['event_key']}/teams")
    if not table['played_matches']:
        print(f"Skipping {event['event_key']}: no played matches")
        continue
    with open(os.path.join('26data', f"{event['event_key']}_team_insights.csv"), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction='ignore')
        writer.writeheader()
        for team in table['teams']:
            writer.writerow({**team, 'num': team['team_number']})
    print(f"{event['event_key']}: {len(table['teams'])} teams")
