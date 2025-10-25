#!/usr/bin/env python3
"""
Debug script to investigate why SMPC computation is producing extremely large values
"""

import sqlite3
import json
import base64
from decimal import Decimal

def analyze_data_values(computation_id):
    """Analyze the actual data values being processed"""
    print(f"=== Analyzing Data Values for: {computation_id} ===")
    
    # Connect to database
    conn = sqlite3.connect('health_data.db')
    cursor = conn.cursor()
    
    try:
        # Get submissions
        cursor.execute("""
            SELECT org_id, data_points 
            FROM computation_results 
            WHERE computation_id = ?
        """, (computation_id,))
        
        submissions = cursor.fetchall()
        print(f"\n📤 Analyzing {len(submissions)} submissions:")
        
        all_decoded_values = []
        
        for org_id, data_points_json in submissions:
            print(f"\n  Org {org_id}:")
            
            if not data_points_json:
                continue
                
            data_points = json.loads(data_points_json)
            
            if isinstance(data_points, dict) and "smpc_shares" in data_points:
                shares = data_points["smpc_shares"]
                print(f"    📊 SMPC shares count: {len(shares)}")
                
                # Analyze the first few shares to understand the structure
                for i, share_list in enumerate(shares[:3]):  # Look at first 3 shares
                    print(f"    Share {i+1}:")
                    print(f"      Type: {type(share_list)}")
                    print(f"      Length: {len(share_list) if hasattr(share_list, '__len__') else 'N/A'}")
                    
                    if isinstance(share_list, list) and len(share_list) > 0:
                        first_share = share_list[0]
                        print(f"      First share type: {type(first_share)}")
                        print(f"      First share: {first_share}")
                        
                        # Try to extract the value
                        if isinstance(first_share, dict) and "value" in first_share:
                            value = first_share["value"]
                            print(f"      Extracted value: {value} (type: {type(value)})")
                            all_decoded_values.append(float(value))
                        elif isinstance(first_share, (int, float)):
                            print(f"      Direct numeric value: {first_share}")
                            all_decoded_values.append(float(first_share))
                
                # Also check the original homomorphic data for comparison
                if "homomorphic" in data_points:
                    homo_data = data_points["homomorphic"]
                    print(f"    🔒 Homomorphic data count: {len(homo_data)}")
                    
                    # Try to decode a few homomorphic values to see original data
                    for i, encoded_val in enumerate(homo_data[:3]):
                        try:
                            decoded_bytes = base64.b64decode(encoded_val)
                            value_str = decoded_bytes.decode('utf-8')
                            original_value = float(value_str)
                            print(f"      Original value {i+1}: {original_value}")
                        except Exception as e:
                            print(f"      Could not decode value {i+1}: {e}")
        
        # Analyze the decoded values
        if all_decoded_values:
            print(f"\n📈 Analysis of decoded values:")
            print(f"    Count: {len(all_decoded_values)}")
            print(f"    Min: {min(all_decoded_values)}")
            print(f"    Max: {max(all_decoded_values)}")
            print(f"    Average: {sum(all_decoded_values) / len(all_decoded_values)}")
            print(f"    Sample values: {all_decoded_values[:10]}")
            
            # Check for extremely large values
            large_values = [v for v in all_decoded_values if abs(v) > 1e10]
            if large_values:
                print(f"    ⚠️ Found {len(large_values)} extremely large values!")
                print(f"    Large values sample: {large_values[:5]}")
        
    finally:
        conn.close()

def main():
    """Main function to debug large values"""
    print("🔍 Large Values Debug Tool")
    print("=" * 50)
    
    # Analyze the specific computation
    computation_id = "be3e65fc-ec67-4daa-bb75-8f84f1565148"
    analyze_data_values(computation_id)
    
    print("\n" + "=" * 50)
    print("🔍 Analysis complete!")

if __name__ == "__main__":
    main()
