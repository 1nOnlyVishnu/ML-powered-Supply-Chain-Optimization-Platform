import pandas as pd
import random
from datetime import datetime, timedelta

def generate_sample_supply_data(num_records=5):
    """Generate sample supply data for demonstration"""
    suppliers = ["Tata Steel", "JSW", "SAIL", "Jindal Steel", "Vedanta"]
    materials = ["Cold Rolled Steel", "HR Coils", "Galvanized Steel", "CRCA Sheets"]

    data = []
    today = datetime.now()

    for i in range(num_records):
        order_date = today - timedelta(days=random.randint(1, 30))
        delivery_days = random.randint(3, 14)
        delivery_date = order_date + timedelta(days=delivery_days)

        record = {
            'Batch_No': f"{random.randint(1000, 9999)}",
            'Supplier_Name': random.choice(suppliers),
            'Material': random.choice(materials),
            'Quality': random.choice(["High", "Medium", "Low"]),
            'Order_Date': order_date.strftime("%Y-%m-%d"),
            'Delivery_Date': delivery_date.strftime("%Y-%m-%d"),
            'Cost': round(random.uniform(4000, 6000), 2),
            'Rating': round(random.uniform(3.5, 5.0), 1)
        }
        data.append(record)

    return pd.DataFrame(data)

def create_sample_csv(filename="sample_supply_data.csv"):
    """Create a sample CSV file with supply data"""
    df = generate_sample_supply_data()
    df.to_csv(filename, index=False)
    return filename