import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# ============================================================
# SETTINGS
# ============================================================

NUM_TRANSACTIONS = 10000

random.seed(42)
np.random.seed(42)

# ============================================================
# OPTIONS
# ============================================================

PAYMENT_METHODS = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking",
    "Wallet"
]

FAILURE_REASONS = [
    "bank_timeout",
    "issuer_declined",
    "insufficient_funds",
    "expired_card",
    "network_error",
    "authentication_failed",
    "suspicious_transaction"
]

# ============================================================
# GENERATE TRANSACTIONS
# ============================================================

transactions = []

start_date = datetime(2026, 8, 1)

for i in range(NUM_TRANSACTIONS):

    transaction_id = f"TX{i+1:06d}"
    customer_id = f"CUST{random.randint(1, 3000):05d}"

    # Payment amount
    amount = round(
        np.random.lognormal(mean=7.0, sigma=1.0),
        2
    )

    # Keep amounts reasonable
    amount = max(100, min(amount, 100000))

    payment_method = random.choice(PAYMENT_METHODS)

    failure_reason = random.choices(
        FAILURE_REASONS,
        weights=[
            22,  # bank timeout
            18,  # issuer declined
            20,  # insufficient funds
            10,  # expired card
            12,  # network error
            10,  # authentication failed
            8    # suspicious
        ]
    )[0]

    previous_failures = random.choices(
        [0, 1, 2, 3, 4, 5],
        weights=[45, 25, 14, 8, 5, 3]
    )[0]

    retry_count = random.randint(0, min(previous_failures + 1, 3))

    customer_age_days = random.randint(1, 1500)

    hour = random.randint(0, 23)

    device_change = random.random() < 0.12

    location_change = random.random() < 0.10

    # ========================================================
    # RECOVERY PROBABILITY
    # ========================================================

    probability = 0.50

    # Failure-specific behavior
    if failure_reason == "bank_timeout":
        probability += 0.25

    elif failure_reason == "network_error":
        probability += 0.20

    elif failure_reason == "insufficient_funds":
        probability += 0.08

    elif failure_reason == "expired_card":
        probability += 0.05

    elif failure_reason == "issuer_declined":
        probability -= 0.05

    elif failure_reason == "authentication_failed":
        probability -= 0.10

    elif failure_reason == "suspicious_transaction":
        probability -= 0.35

    # Previous failures reduce recovery chance
    probability -= previous_failures * 0.06

    # Multiple retries reduce recovery chance
    probability -= retry_count * 0.08

    # New device/location increases risk
    if device_change:
        probability -= 0.10

    if location_change:
        probability -= 0.08

    # Very large transactions are harder to recover automatically
    if amount > 50000:
        probability -= 0.10

    # Very old customers are slightly easier to recover
    if customer_age_days > 365:
        probability += 0.05

    # Keep probability within realistic range
    probability = max(0.02, min(probability, 0.97))

    # ========================================================
    # ACTUAL RECOVERY RESULT
    # ========================================================

    recovered = int(random.random() < probability)

    # ========================================================
    # DATE
    # ========================================================

    transaction_date = start_date + timedelta(
        minutes=random.randint(0, 60 * 24 * 30)
    )

    transactions.append({
        "transaction_id": transaction_id,
        "customer_id": customer_id,
        "amount": round(amount, 2),
        "payment_method": payment_method,
        "failure_reason": failure_reason,
        "previous_failures": previous_failures,
        "retry_count": retry_count,
        "customer_age_days": customer_age_days,
        "hour": hour,
        "device_change": int(device_change),
        "location_change": int(location_change),
        "true_recovery_probability": round(probability, 4),
        "recovered": recovered,
        "transaction_date": transaction_date
    })


# ============================================================
# CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(transactions)

# ============================================================
# SAVE DATASET
# ============================================================

output_file = "data/failed_payments.csv"

df.to_csv(output_file, index=False)

# ============================================================
# DISPLAY SUMMARY
# ============================================================

print("\n==============================================")
print("        RECOVERAI DATASET CREATED")
print("==============================================")

print(f"\nTotal transactions: {len(df):,}")

print(f"Total revenue at risk: ₹{df['amount'].sum():,.2f}")

print(
    f"Potentially recovered historically: "
    f"₹{df.loc[df['recovered'] == 1, 'amount'].sum():,.2f}"
)

print(
    f"Historical recovery rate: "
    f"{df['recovered'].mean() * 100:.2f}%"
)

print("\nFailure distribution:")
print(df["failure_reason"].value_counts())

print("\nDataset saved to:")
print(output_file)

print("\nFirst 5 transactions:")
print(df.head())