import csv
import os

def validate_csv(file_path):
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}")
            return False
            
        # Read CSV file
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            
            # Get headers
            headers = next(reader)
            print("\nCSV File Headers:")
            print("-" * 80)
            for i, header in enumerate(headers):
                print(f"{i+1}. {header}")
            
            # Read and count rows
            rows = list(reader)
            print(f"\nNumber of data rows: {len(rows)}")
            
            # Print first row as sample
            if rows:
                print("\nSample row:")
                print("-" * 80)
                for header, value in zip(headers, rows[0]):
                    print(f"{header}: {value}")
            
            # Check file size
            file_size = os.path.getsize(file_path)
            print(f"\nFile size: {file_size} bytes")
            
            return True
            
    except Exception as e:
        print(f"Error validating CSV: {str(e)}")
        return False

if __name__ == "__main__":
    csv_path = "sample_health_data.csv"
    print(f"Validating CSV file: {csv_path}")
    if validate_csv(csv_path):
        print("\nCSV file is valid and ready for upload!")
    else:
        print("\nCSV file validation failed!") 