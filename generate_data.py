import sqlite3
import json
import os
from datetime import datetime, timedelta

DB_PATH = "/home/ubuntu/.openclaw/workspace/poe2_prices.db"
OUTPUT_DIR = "/home/ubuntu/.openclaw/workspace/ecdtracker/data"

def generate_data():
    if not os.path.exists(DB_PATH):
        print(f"Database not found: {DB_PATH}")
        return False
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get all prices from last 24 hours
    cutoff = (datetime.now() - timedelta(hours=24)).timestamp()
    
    c.execute("""
        SELECT item, price, divine_price, timestamp, datetime 
        FROM prices 
        WHERE timestamp > ? 
        ORDER BY timestamp
    """, (cutoff,))
    
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        print("No data in DB yet")
        return False
    
    # Organize by currency - include ALL currencies with volume
    data = {
        "Divine": [],
        "Exalt": [],
        "Chaos": [],
        "Annulment": [],
        "Omen_Abyssal_Echoes": [],
        "Omen_Whittling": [],
        "Omen_Light": [],
        "Hinekoras_Lock": [],
        "Mirror_Kalandra": []
    }
    
    for item, price, divine_price, timestamp, dt in rows:
        if item in data:
            data[item].append({
                "x": dt,
                "y": price,
                "divine_price": divine_price,
                "volume": 0
            })
    
    # Calculate pairs for ALL currencies
    pairs = {}
    all_currencies = ["Divine", "Exalt", "Chaos", "Annulment", "Omen_Abyssal_Echoes", "Omen_Whittling", "Omen_Light", "Hinekoras_Lock", "Mirror_Kalandra"]
    
    for base in all_currencies:
        for quote in all_currencies:
            if base != quote:
                pair_key = f"{base}/{quote}"
                pairs[pair_key] = []
                
                base_data = data.get(base, [])
                quote_data = data.get(quote, [])
                
                # Match timestamps
                for b_point in base_data:
                    for q_point in quote_data:
                        if b_point["x"] == q_point["x"] and q_point["y"] > 0:
                            pairs[pair_key].append({
                                "x": b_point["x"],
                                "y": b_point["y"] / q_point["y"]
                            })
                            break
    
    # Save all data
    with open(f"{OUTPUT_DIR}/prices.json", "w") as f:
        json.dump(data, f, indent=2)
    
    with open(f"{OUTPUT_DIR}/pairs.json", "w") as f:
        json.dump(pairs, f, indent=2)
    
    # Save latest snapshot
    latest = {}
    all_currencies = ["Divine", "Exalt", "Chaos", "Annulment", "Omen_Abyssal_Echoes", "Omen_Whittling", "Omen_Light", "Hinekoras_Lock", "Mirror_Kalandra"]
    for currency in all_currencies:
        if data[currency]:
            latest[currency] = data[currency][-1]["y"]
    
    with open(f"{OUTPUT_DIR}/latest.json", "w") as f:
        json.dump(latest, f, indent=2)
    
    print(f"Generated data files in {OUTPUT_DIR}")
    print(f"Prices: {len(data.get('Divine', []))} Divine points")
    print(f"Pairs: {len(pairs)} pairs calculated")
    
    return True

if __name__ == "__main__":
    generate_data()
