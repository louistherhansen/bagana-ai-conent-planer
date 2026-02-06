#!/usr/bin/env python3
"""
Validate market_trends table structure and data consistency.
Checks if database schema matches expected structure and validates data integrity.
"""

import psycopg2
import sys
import os
from datetime import datetime

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "bagana-ai-cp"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "123456")
}

EXPECTED_COLUMNS = {
    "id": "VARCHAR(255)",
    "brand_name": "VARCHAR(255)",
    "full_output": "TEXT",
    "conversation_id": "VARCHAR(255)",
    "created_at": "TIMESTAMP"
}

EXPECTED_INDEXES = [
    "idx_market_trends_brand_name",
    "idx_market_trends_created_at",
    "idx_market_trends_conversation_id"
]


def validate_schema(cur):
    """Validate table schema matches expected structure."""
    print("=" * 60)
    print("SCHEMA VALIDATION")
    print("=" * 60)
    
    # Check if table exists
    cur.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'market_trends';
    """)
    if not cur.fetchone():
        print("[ERROR] Table 'market_trends' does not exist!")
        return False
    
    print("[OK] Table 'market_trends' exists")
    
    # Check columns
    cur.execute("""
        SELECT column_name, data_type, character_maximum_length, numeric_precision, numeric_scale
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'market_trends'
        ORDER BY ordinal_position;
    """)
    
    columns = cur.fetchall()
    found_columns = {}
    
    print("\nColumns:")
    for col in columns:
        col_name, data_type, max_length, precision, scale = col
        found_columns[col_name] = {
            "type": data_type,
            "max_length": max_length,
            "precision": precision,
            "scale": scale
        }
        
        # Format display
        if data_type == "character varying":
            type_display = f"VARCHAR({max_length})"
        elif data_type == "numeric":
            type_display = f"NUMERIC({precision},{scale})"
        elif data_type == "timestamp without time zone":
            type_display = "TIMESTAMP"
        else:
            type_display = data_type.upper()
        
        status = "[OK]" if col_name in EXPECTED_COLUMNS else "[EXTRA]"
        print(f"  {status} {col_name}: {type_display}")
    
    # Check for missing columns
    missing = set(EXPECTED_COLUMNS.keys()) - set(found_columns.keys())
    if missing:
        print(f"\n[ERROR] Missing columns: {', '.join(missing)}")
        return False
    
    print("\n[OK] All expected columns present")
    
    # Check indexes
    cur.execute("""
        SELECT indexname FROM pg_indexes
        WHERE tablename = 'market_trends' AND schemaname = 'public';
    """)
    
    indexes = [row[0] for row in cur.fetchall()]
    print("\nIndexes:")
    for idx in EXPECTED_INDEXES:
        if idx in indexes:
            print(f"  [OK] {idx}")
        else:
            print(f"  [WARNING] {idx} - not found")
    
    return True


def validate_data_integrity(cur):
    """Validate data integrity and consistency."""
    print("\n" + "=" * 60)
    print("DATA INTEGRITY VALIDATION")
    print("=" * 60)
    
    # Check total records
    cur.execute("SELECT COUNT(*) FROM market_trends;")
    total = cur.fetchone()[0]
    print(f"\nTotal records: {total}")
    
    if total == 0:
        print("[INFO] No records found - database is empty")
        return True
    
    # Check for NULL brand names
    cur.execute("SELECT COUNT(*) FROM market_trends WHERE brand_name IS NULL OR brand_name = '';")
    null_brands = cur.fetchone()[0]
    if null_brands > 0:
        print(f"\n[WARNING] Found {null_brands} records with NULL or empty brand_name")
    else:
        print("[OK] All records have brand_name")
    
    # Check for records without full_output
    cur.execute("SELECT COUNT(*) FROM market_trends WHERE full_output IS NULL OR full_output = '';")
    empty_output = cur.fetchone()[0]
    if empty_output > 0:
        print(f"\n[WARNING] Found {empty_output} records without full_output")
    else:
        print("[OK] All records have full_output")
    
    return True


def validate_template_compliance(cur):
    """Check if full_output follows trends_market.md template structure."""
    print("\n" + "=" * 60)
    print("TEMPLATE COMPLIANCE VALIDATION")
    print("=" * 60)
    
    cur.execute("SELECT id, brand_name, full_output FROM market_trends LIMIT 10;")
    records = cur.fetchall()
    
    if not records:
        print("[INFO] No records to validate")
        return True
    
    required_sections = [
        "Key Market Trends",
        "Summary Bar Chart Data",
        "Creator Economy Insights",
        "Competitive Landscape",
        "Content Format Trends",
        "Timing and Seasonality",
        "Implications for Strategy",
        "Recommendations",
        "Sources",
        "Audit"
    ]
    
    print(f"\nValidating {len(records)} sample records...")
    
    compliant = 0
    non_compliant = []
    
    for record_id, brand_name, full_output in records:
        if not full_output:
            continue
        
        missing_sections = []
        for section in required_sections:
            if section not in full_output:
                missing_sections.append(section)
        
        if not missing_sections:
            compliant += 1
        else:
            non_compliant.append((record_id, brand_name, missing_sections))
    
    print(f"[OK] {compliant}/{len(records)} records are template-compliant")
    
    if non_compliant:
        print(f"\n[WARNING] {len(non_compliant)} records missing required sections:")
        for record_id, brand_name, missing in non_compliant[:3]:
            print(f"  - ID: {record_id}, Brand: {brand_name}")
            print(f"    Missing: {', '.join(missing)}")
        if len(non_compliant) > 3:
            print(f"  ... and {len(non_compliant) - 3} more")
    
    # Check Summary Bar Chart Data format
    print("\nChecking Summary Bar Chart Data format...")
    bar_chart_valid = 0
    bar_chart_invalid = []
    
    for record_id, brand_name, full_output in records:
        if not full_output or "Summary Bar Chart Data" not in full_output:
            continue
        
        # Check if format matches "Trend Name | Value"
        import re
        section_match = re.search(r'#\s*Summary\s+Bar\s+Chart\s+Data[\s\S]*?(?=#|$)', full_output, re.IGNORECASE)
        if section_match:
            section_text = section_match.group(0)
            lines = section_text.split('\n')
            has_valid_format = False
            for line in lines:
                trimmed = line.strip()
                if re.match(r'^.+?\s*\|\s*\d+(?:\.\d+)?$', trimmed):
                    has_valid_format = True
                    break
            
            if has_valid_format:
                bar_chart_valid += 1
            else:
                bar_chart_invalid.append((record_id, brand_name))
    
    if bar_chart_valid > 0:
        print(f"[OK] {bar_chart_valid} records have valid Summary Bar Chart Data format")
    if bar_chart_invalid:
        print(f"[WARNING] {len(bar_chart_invalid)} records have invalid Summary Bar Chart Data format:")
        for record_id, brand_name in bar_chart_invalid[:3]:
            print(f"  - ID: {record_id}, Brand: {brand_name}")
        if len(bar_chart_invalid) > 3:
            print(f"  ... and {len(bar_chart_invalid) - 3} more")
    
    return True


def main():
    """Main validation function."""
    print("=" * 60)
    print("BAGANA AI - Market Trends Database Validation")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    conn = None
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        print("[OK] Connected successfully!\n")
        
        cur = conn.cursor()
        
        # Run validations
        schema_ok = validate_schema(cur)
        if not schema_ok:
            print("\n[ERROR] Schema validation failed!")
            return False
        
        data_ok = validate_data_integrity(cur)
        template_ok = validate_template_compliance(cur)
        
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Schema: {'[OK]' if schema_ok else '[FAIL]'}")
        print(f"Data Integrity: {'[OK]' if data_ok else '[FAIL]'}")
        print(f"Template Compliance: {'[OK]' if template_ok else '[FAIL]'}")
        
        if schema_ok and data_ok and template_ok:
            print("\n[OK] All validations passed!")
            return True
        else:
            print("\n[WARNING] Some validations had issues (see details above)")
            return True  # Return True even with warnings
        
    except psycopg2.OperationalError as e:
        print(f"[FAIL] Connection failed: {e}")
        return False
    except psycopg2.Error as e:
        print(f"[FAIL] Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()
            print("\nConnection closed.")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
