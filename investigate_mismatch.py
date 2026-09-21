"""
Mismatch Investigation Script
Investigates why SQL FLOAT gives 45001100.0 but Pandas gives 45001122.55490576
"""
import pandas as pd
import struct

df = pd.read_csv('AISHE_Enrollment_Trend_2019_2024.csv')
row = df[(df['State_UT'] == 'All India') & (df['Year'] == '2023-24')]

grand_total = row['Grand_Total'].values[0]
print("=== MISMATCH INVESTIGATION ===")
print(f"Grand_Total dtype in pandas: {df['Grand_Total'].dtype}")
print(f"Grand_Total (Pandas):        {grand_total}")
print(f"Has fractional part:         {grand_total != int(grand_total)}")
print()

# Demonstrate MySQL FLOAT precision loss
as_float32 = struct.unpack('f', struct.pack('f', grand_total))[0]
print("=== PRECISION ANALYSIS ===")
print(f"Original 64-bit double value:  {grand_total:.8f}")
print(f"After 32-bit FLOAT cast:       {as_float32:.8f}")
print(f"Precision loss:                {grand_total - as_float32:.8f}")
print()
print("FLOAT (32-bit): ~7 significant digits. For a value of ~45 million, this")
print("means rounding to the nearest 4-8 (i.e., integers are imprecise at this scale).")
print()
print("=== ROOT CAUSE ===")
print("The setup_db.py script maps pandas float64 columns to MySQL FLOAT (4 bytes).")
print("MySQL FLOAT stores only 7 significant decimal digits.")
print("45001122.55 has 10 significant digits — exceeds FLOAT precision.")
print("MySQL rounds 45001122.55490576 to approximately 45001100.0 (7 sig digits).")
print()
print("=== FIX ===")
print("Change MySQL column type from FLOAT to DOUBLE (8 bytes, 15-16 sig digits).")
print("No changes to source CSV or Excel file required.")
print("Re-run setup_db.py with DOUBLE dtype mapping.")
print()

# Also check how many other rows have fractional values
frac_count = sum(1 for v in df['Grand_Total'].dropna() if v != int(v))
print(f"=== SCOPE ===")
print(f"Rows with fractional Grand_Total: {frac_count} / {len(df['Grand_Total'].dropna())}")
print("(Fractional values occur because state enrollment figures from")
print(" some years use weighted/estimated counts, not exact integers.)")
