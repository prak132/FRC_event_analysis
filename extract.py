import csv 
import os

input_filename = '2024cave_team_insights.csv'
event_name = input_filename.split('_')[0]
file_exists = os.path.exists('data24.csv')

with open(input_filename, mode='r') as infile, open('data24.csv', mode='a', newline='') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.writer(outfile)
    if not file_exists:
        writer.writerow(['event', 'team_num', 'norm_epa'])
    for row in reader:
        team_num = row['\ufeff"num"'].strip('"')
        norm_epa = row["norm_epa"]
        writer.writerow([event_name, team_num, norm_epa])