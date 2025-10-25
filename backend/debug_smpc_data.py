#!/usr/bin/env python3
"""
Debug script to analyze SMPC data submissions and identify the root cause
of "No valid SMPC shares found in submissions" error.
"""

import sqlite3
import json
from datetime import datetime

def analyze_computation_data(computation_id):
    """Analyze the data for a specific computation"""
    print(f"=== Analyzing Computation: {computation_id} ===")
    
    # Connect to database
    conn = sqlite3.connect('health_data.db')
    cursor = conn.cursor()
    
    try:
        # Get computation details
        cursor.execute("""
            SELECT computation_id, type, status, created_at, error_message 
            FROM secure_computations 
            WHERE computation_id = ?
        """, (computation_id,))
        
        comp_result = cursor.fetchone()
        if not comp_result:
            print(f"❌ Computation {computation_id} not found")
            return
            
        comp_id, comp_type, status, created_at, error_msg = comp_result
        print(f"📊 Type: {comp_type}")
        print(f"📈 Status: {status}")
        print(f"📅 Created: {created_at}")
        if error_msg:
            print(f"❌ Error: {error_msg}")
        
        # Get participants
        cursor.execute("""
            SELECT org_id FROM computation_participants 
            WHERE computation_id = ?
        """, (computation_id,))
        
        participants = cursor.fetchall()
        print(f"\n👥 Participants ({len(participants)}):")
        for (org_id,) in participants:
            print(f"  - Organization {org_id}")
        
        # Get submissions
        cursor.execute("""
            SELECT org_id, data_points, created_at 
            FROM computation_results 
            WHERE computation_id = ?
        """, (computation_id,))
        
        submissions = cursor.fetchall()
        print(f"\n📤 Submissions ({len(submissions)}):")
        
        for i, (org_id, data_points_json, created_at) in enumerate(submissions):
            print(f"\n  Submission {i+1} (Org {org_id}):")
            print(f"    📅 Submitted: {created_at}")
            
            try:
                # Parse the data_points JSON
                if data_points_json:
                    data_points = json.loads(data_points_json)
                    print(f"    📋 Data structure: {type(data_points)}")
                    
                    if isinstance(data_points, dict):
                        print(f"    🔑 Keys: {list(data_points.keys())}")
                        
                        # Check for SMPC shares
                        if "smpc_shares" in data_points:
                            shares = data_points["smpc_shares"]
                            print(f"    🔐 SMPC shares type: {type(shares)}")
                            print(f"    🔐 SMPC shares length: {len(shares) if hasattr(shares, '__len__') else 'N/A'}")
                            
                            if isinstance(shares, list) and len(shares) > 0:
                                print(f"    🔐 First share type: {type(shares[0])}")
                                print(f"    🔐 First share sample: {shares[0] if len(str(shares[0])) < 200 else str(shares[0])[:200] + '...'}")
                            else:
                                print(f"    ❌ SMPC shares is empty or not a list")
                        else:
                            print(f"    ❌ No 'smpc_shares' key found")
                        
                        # Check for homomorphic data
                        if "homomorphic" in data_points:
                            homo_data = data_points["homomorphic"]
                            print(f"    🔒 Homomorphic data type: {type(homo_data)}")
                            print(f"    🔒 Homomorphic data length: {len(homo_data) if hasattr(homo_data, '__len__') else 'N/A'}")
                        
                        # Check for original count
                        if "original_count" in data_points:
                            print(f"    📊 Original count: {data_points['original_count']}")
                    
                    elif isinstance(data_points, list):
                        print(f"    📋 List length: {len(data_points)}")
                        if len(data_points) > 0:
                            print(f"    📋 First item type: {type(data_points[0])}")
                            print(f"    📋 First item sample: {data_points[0] if len(str(data_points[0])) < 100 else str(data_points[0])[:100] + '...'}")
                    
                    else:
                        print(f"    📋 Raw data: {data_points}")
                        
                else:
                    print(f"    ❌ No data_points found")
                    
            except json.JSONDecodeError as e:
                print(f"    ❌ JSON decode error: {e}")
            except Exception as e:
                print(f"    ❌ Error analyzing data: {e}")
        
        # Determine what computation type should use
        print(f"\n🔍 Analysis for computation type '{comp_type}':")
        if comp_type.lower() in ["secure_sum", "secure_mean", "secure_variance", "secure_average"]:
            print(f"  ✅ Should use HYBRID method (homomorphic + SMPC)")
            print(f"  🔍 Looking for 'smpc_shares' in submissions...")
            
            # Check if any submission has valid SMPC shares
            has_valid_smpc = False
            for org_id, data_points_json, _ in submissions:
                if data_points_json:
                    try:
                        data_points = json.loads(data_points_json)
                        if isinstance(data_points, dict) and "smpc_shares" in data_points:
                            shares = data_points["smpc_shares"]
                            if shares and isinstance(shares, list) and len(shares) > 0:
                                has_valid_smpc = True
                                break
                    except:
                        pass
            
            if has_valid_smpc:
                print(f"  ✅ Found valid SMPC shares")
            else:
                print(f"  ❌ No valid SMPC shares found - this is the problem!")
        else:
            print(f"  ✅ Should use HOMOMORPHIC method only")
    
    finally:
        conn.close()

def main():
    """Main function to debug SMPC data"""
    print("🔍 SMPC Data Analysis Tool")
    print("=" * 50)
    
    # Analyze the specific computation from the error
    computation_id = "be3e65fc-ec67-4daa-bb75-8f84f1565148"
    analyze_computation_data(computation_id)
    
    print("\n" + "=" * 50)
    print("🔍 Analysis complete!")

if __name__ == "__main__":
    main()
