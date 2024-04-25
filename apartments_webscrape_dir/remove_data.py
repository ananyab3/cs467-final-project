import csv
import re

input_path = 'apartments.csv'
output_path = 'only_url_data.csv'

with open(input_path, mode='r', encoding='utf-8') as infile, open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    writer.writerow(['URL'])

    for row in reader:
        full_row = ','.join(row)
        match = re.search(r'http[s]?://\S+', full_row)
        if match:
            url = match.group(0)
            writer.writerow([url])

print("Processing completed. The cleaned dataset is saved.")
