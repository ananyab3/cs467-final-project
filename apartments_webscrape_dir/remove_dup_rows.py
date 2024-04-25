import csv

input_path = 'apartments_clean7_dataset.csv'
output_path = 'apartments_dataset.csv'

seen = set() 
with open(input_path, mode='r', encoding='utf-8') as infile, \
     open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    for row in reader:
        row_tuple = tuple(row)
        if row_tuple not in seen:
            writer.writerow(row)
            seen.add(row_tuple)

print("Duplicates removed and new dataset saved.")
