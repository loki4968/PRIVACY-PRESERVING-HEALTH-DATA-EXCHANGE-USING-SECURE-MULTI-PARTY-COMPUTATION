#!/usr/bin/env python3
"""
Fix existing computation data to include SMPC shares for secure_average computations
"""

import sqlite3
import json
import base64
from decimal import Decimal
from smpc_protocols import smpc_protocol

def fix_computation_data(computation_id):
    """Fix the data for a specific computation by adding SMPC shares"""
    print(f"=== Fixing Computation: {computation_id} ===")
    
    # Connect to database
    conn = sqlite3.connect('health_data.db')
    cursor = conn.cursor()
    
    try:
        # Get computation details
        cursor.execute("""
            SELECT computation_id, type, status 
            FROM secure_computations 
            WHERE computation_id = ?
        """, (computation_id,))
        
        comp_result = cursor.fetchone()
        if not comp_result:
            print(f"❌ Computation {computation_id} not found")
            return False
            
        comp_id, comp_type, status = comp_result
        print(f"📊 Type: {comp_type}")
        print(f"📈 Status: {status}")
        
        # Check if this computation type needs SMPC shares
        if comp_type.lower() not in ["secure_sum", "secure_mean", "secure_variance", "secure_average"]:
            print(f"ℹ️ Computation type '{comp_type}' doesn't need SMPC shares")
            return True
        
        # Get submissions that need fixing
        cursor.execute("""
            SELECT id, org_id, data_points 
            FROM computation_results 
            WHERE computation_id = ?
        """, (computation_id,))
        
        submissions = cursor.fetchall()
        print(f"\n📤 Found {len(submissions)} submissions to fix")
        
        fixed_count = 0
        for result_id, org_id, data_points_json in submissions:
            try:
                if not data_points_json:
                    continue
                    
                data_points = json.loads(data_points_json)
                
                # Check if it's already in the correct format
                if isinstance(data_points, dict) and "smpc_shares" in data_points:
                    print(f"  ✅ Org {org_id} already has SMPC shares")
                    continue
                
                # If it's a list of base64 strings, we need to convert them
                if isinstance(data_points, list):
                    print(f"  🔧 Fixing Org {org_id} submission...")
                    
                    # Decode the base64 values to get original numeric values
                    numeric_values = []
                    for encoded_val in data_points:
                        try:
                            # Decode base64 to get the original value
                            decoded_bytes = base64.b64decode(encoded_val)
                            # Convert bytes back to string then to float
                            value_str = decoded_bytes.decode('utf-8')
                            value = Decimal(str(float(value_str)))
                            numeric_values.append(value)
                        except Exception as e:
                            print(f"    ⚠️ Could not decode value {encoded_val}: {e}")
                            continue
                    
                    if not numeric_values:
                        print(f"    ❌ No valid numeric values found for Org {org_id}")
                        continue
                    
                    # Generate SMPC shares for each value
                    smpc_shares = []
                    for value in numeric_values:
                        try:
                            shares = smpc_protocol.generate_shares(value, 3, 2)  # t=2, n=3
                            smpc_shares.append(shares)
                        except Exception as e:
                            print(f"    ❌ Error generating SMPC shares: {e}")
                            return False
                    
                    # Create the new data structure
                    new_data_points = {
                        "homomorphic": data_points,  # Keep original encrypted data
                        "smpc_shares": smpc_shares,
                        "original_count": len(numeric_values)
                    }
                    
                    # Update the database
                    cursor.execute("""
                        UPDATE computation_results 
                        SET data_points = ? 
                        WHERE id = ?
                    """, (json.dumps(new_data_points), result_id))
                    
                    print(f"    ✅ Fixed Org {org_id} - added {len(smpc_shares)} SMPC shares")
                    fixed_count += 1
                
            except Exception as e:
                print(f"    ❌ Error fixing Org {org_id}: {e}")
                continue
        
        if fixed_count > 0:
            # Reset computation status to allow reprocessing
            cursor.execute("""
                UPDATE secure_computations 
                SET status = 'waiting_for_data', error_message = NULL, error_code = NULL
                WHERE computation_id = ?
            """, (computation_id,))
            
            conn.commit()
            print(f"\n✅ Fixed {fixed_count} submissions and reset computation status")
            return True
        else:
            print(f"\n ℹ️ No submissions needed fixing")
            return True
            
    except Exception as e:
        print(f"❌ Error fixing computation: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    """Main function to fix SMPC data"""
    print("🔧 SMPC Data Fix Tool")
    print("=" * 50)
    
    # Fix the specific computation from the error
    computation_id = "be3e65fc-ec67-4daa-bb75-8f84f1565148"
    success = fix_computation_data(computation_id)
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Fix completed successfully!")
        print("💡 You can now trigger the computation again")
    else:
        print("❌ Fix failed!")

if __name__ == "__main__":
    main()
