import os
import sys

import pandas as pd


# ============================================================
# ADD PROJECT ROOT TO PYTHON PATH
# ============================================================

ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, ROOT_DIR)


# ============================================================
# IMPORT RECOVERAI
# ============================================================

from agent.recovery_agent import analyze_payment
from simulator.payment_simulator import (
    policy_check,
    execute_payment
)


# ============================================================
# LOAD DATA
# ============================================================

DATA_PATH = os.path.join(ROOT_DIR, "data", "failed_payments.csv")

df = pd.read_csv(DATA_PATH)


# ============================================================
# METRICS
# ============================================================

total_transactions = len(df)

total_revenue_at_risk = df["amount"].sum()

recovery_attempts = 0

successful_recoveries = 0

recovered_revenue = 0

blocked_actions = 0

retry_actions = 0

retry_later_actions = 0

update_actions = 0

stop_actions = 0


results = []


# ============================================================
# PROCESS TRANSACTIONS
# ============================================================

print("\n==============================================")
print("          RECOVERAI BATCH PROCESSING")
print("==============================================")

print(
    f"\nProcessing {total_transactions:,} transactions..."
)


for index, row in df.iterrows():

    transaction = row.to_dict()

    # --------------------------------------------------------
    # AI AGENT
    # --------------------------------------------------------

    decision = analyze_payment(transaction)

    action = decision["recommended_action"]

    probability = decision["recovery_probability"]

    # --------------------------------------------------------
    # COUNT ACTIONS
    # --------------------------------------------------------

    if action == "RETRY":
        retry_actions += 1

    elif action == "RETRY_LATER":
        retry_later_actions += 1

    elif action == "UPDATE_PAYMENT_METHOD":
        update_actions += 1

    elif action == "STOP":
        stop_actions += 1

    # --------------------------------------------------------
    # POLICY CHECK
    # --------------------------------------------------------

    policy = policy_check(
        transaction,
        decision
    )

    if not policy["allowed"]:

        blocked_actions += 1

        results.append({
            "transaction_id":
                transaction["transaction_id"],

            "amount":
                transaction["amount"],

            "failure_reason":
                transaction["failure_reason"],

            "recovery_probability":
                probability,

            "action":
                action,

            "policy":
                "BLOCKED",

            "status":
                "NOT_EXECUTED",

            "recovered_amount":
                0,

            "reason":
                policy["reason"]
        })

        continue

    # --------------------------------------------------------
    # EXECUTE
    # --------------------------------------------------------

    if action in ["RETRY", "RETRY_LATER"]:

        recovery_attempts += 1

        execution = execute_payment(
    transaction,
    action,
    probability,
    verbose=False
)

        status = execution["status"]

        recovered_amount = execution[
            "recovered_amount"
        ]

        if status == "SUCCESS":

            successful_recoveries += 1

            recovered_revenue += recovered_amount

    else:

        status = "NOT_EXECUTED"

        recovered_amount = 0

    # --------------------------------------------------------
    # SAVE RESULT
    # --------------------------------------------------------

    results.append({
        "transaction_id":
            transaction["transaction_id"],

        "amount":
            transaction["amount"],

        "failure_reason":
            transaction["failure_reason"],

        "recovery_probability":
            probability,

        "action":
            action,

        "policy":
            "APPROVED",

        "status":
            status,

        "recovered_amount":
            recovered_amount,

        "reason":
            decision["reason"]
    })


# ============================================================
# RESULTS DATAFRAME
# ============================================================

results_df = pd.DataFrame(results)


# ============================================================
# SAVE RESULTS
# ============================================================

output_file = os.path.join(ROOT_DIR, "data", "recovery_results.csv")

results_df.to_csv(
    output_file,
    index=False
)


# ============================================================
# FINAL METRICS
# ============================================================

recovery_rate = 0

if recovery_attempts > 0:

    recovery_rate = (
        successful_recoveries /
        recovery_attempts
    ) * 100


# ============================================================
# DISPLAY
# ============================================================

print("\n==============================================")
print("             RECOVERAI RESULTS")
print("==============================================")

print(
    f"\nTransactions analyzed: "
    f"{total_transactions:,}"
)

print(
    f"Revenue at risk: "
    f"₹{total_revenue_at_risk:,.2f}"
)

print(
    f"\nRecovery attempts: "
    f"{recovery_attempts:,}"
)

print(
    f"Successful recoveries: "
    f"{successful_recoveries:,}"
)

print(
    f"Recovery success rate: "
    f"{recovery_rate:.2f}%"
)

print(
    f"\nRecovered revenue: "
    f"₹{recovered_revenue:,.2f}"
)

print(
    f"\nBlocked actions: "
    f"{blocked_actions:,}"
)

print("\n----------------------------------------------")

print(
    f"RETRY actions: "
    f"{retry_actions:,}"
)

print(
    f"RETRY_LATER actions: "
    f"{retry_later_actions:,}"
)

print(
    f"UPDATE PAYMENT actions: "
    f"{update_actions:,}"
)

print(
    f"STOP actions: "
    f"{stop_actions:,}"
)

print("\n----------------------------------------------")

print(
    f"Results saved to: "
    f"{output_file}"
)

print("==============================================")