import csv
import random
import string

# File name
file_name = "sample_10million.csv"

# Number of rows
num_rows = 10_000_000

# Example columns: id, name, age, city
cities = ["New York", "London", "Tokyo", "Paris", "Berlin"]

def random_name():
    return ''.join(random.choices(string.ascii_letters, k=8))

with open(file_name, mode='w', newline='') as f:
    writer = csv.writer(f)
    # Write header
    writer.writerow(["id", "name", "age", "city"])
    
    for i in range(1, num_rows + 1):
        writer.writerow([i, random_name(), random.randint(18, 80), random.choice(cities)])
        
print("CSV file generated successfully!")
