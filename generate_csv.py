import csv
import random
from datetime import datetime, timedelta

# Define headers
headers = ["PatientID", "Date", "Time", "BloodSugar_mg_dL"]

# Generate sample data
num_entries = 30  # You can change this
start_date = datetime(2025, 5, 1)

rows = []
for i in range(num_entries):
    patient_id = random.randint(1000, 1005)
    date = (start_date + timedelta(days=i // 3)).strftime("%Y-%m-%d")
    time = f"{8 + (i % 3)}:{random.choice(['00', '15', '30'])}"
    blood_sugar = random.randint(80, 180)

    rows.append([patient_id, date, time, blood_sugar])

# Save to CSV
with open("blood_sugar_report.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(rows)

print("✅ 'blood_sugar_report.csv' generated successfully!")
