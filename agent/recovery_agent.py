import os
import sys

import pandas as pd
import joblib


# Add RecoverAI root directory to Python path
ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, ROOT_DIR)


from simulator.payment_simulator import (
    policy_check,
    execute_payment
)


# ============================================================
# LOAD MODEL
# ============================================================

MODEL_PATH = os.path.join(ROOT_DIR, "models", "recovery_model.pkl")

model = joblib.load(MODEL_PATH)


# ============================================================
# POLICY SETTINGS
# ============================================================

MIN_RECOVERY_PROBABILITY = 0.70

MAX_AUTO_RETRY_AMOUNT = 10000

MAX_RETRIES = 2


# ============================================================
# AGENT
# ============================================================

def analyze_payment(transaction):

    # --------------------------------------------------------
    # Convert transaction to DataFrame
    # --------------------------------------------------------

    df = pd.DataFrame([transaction])

    # --------------------------------------------------------
    # Predict recovery probability
    # --------------------------------------------------------

    probability = model.predict_proba(df)[0][1]

    probability_percent = round(probability * 100, 2)

    failure = transaction["failure_reason"]

    amount = transaction["amount"]

    retry_count = transaction["retry_count"]

    # --------------------------------------------------------
    # AGENT DECISION
    # --------------------------------------------------------

    if failure == "suspicious_transaction":

        action = "STOP"

        reason = (
            "Transaction has suspicious characteristics. "
            "Automatic recovery is not allowed."
        )

    elif failure == "expired_card":

        action = "UPDATE_PAYMENT_METHOD"

        reason = (
            "The payment method appears to be expired. "
            "Retrying the same method is unlikely to succeed."
        )

    elif retry_count >= MAX_RETRIES:

        action = "STOP"

        reason = (
            "Maximum automatic retry limit has been reached."
        )

    elif probability >= MIN_RECOVERY_PROBABILITY:

        if amount <= MAX_AUTO_RETRY_AMOUNT:

            action = "RETRY"

            reason = (
                "High recovery probability and transaction "
                "is within the automatic retry amount limit."
            )

        else:

            action = "RETRY_LATER"

            reason = (
                "Recovery probability is high, but the "
                "transaction amount exceeds the automatic "
                "retry limit."
            )

    elif probability >= 0.40:

        action = "RETRY_LATER"

        reason = (
            "Recovery probability is moderate. "
            "A delayed retry is safer than an immediate retry."
        )

    else:

        action = "STOP"

        reason = (
            "Recovery probability is too low for automatic "
            "recovery."
        )

    # --------------------------------------------------------
    # RETURN DECISION
    # --------------------------------------------------------

    return {
        "transaction_id": transaction["transaction_id"],
        "amount": amount,
        "failure_reason": failure,
        "recovery_probability": probability_percent,
        "recommended_action": action,
        "reason": reason
    }


# ============================================================
# TEST AGENT
# ============================================================

if __name__ == "__main__":

    data = pd.read_csv(
        "data/failed_payments.csv"
    )

    # Test first transaction

    transaction = data.iloc[0].to_dict()

    # --------------------------------------------------------
    # AI AGENT ANALYSIS
    # --------------------------------------------------------

    result = analyze_payment(transaction)

    print("\n==============================================")
    print("             RECOVERAI AGENT")
    print("==============================================")

    print(
        f"\nTransaction ID: "
        f"{result['transaction_id']}"
    )

    print(
        f"Amount: "
        f"₹{result['amount']:,.2f}"
    )

    print(
        f"Failure: "
        f"{result['failure_reason']}"
    )

    print(
        f"Recovery Probability: "
        f"{result['recovery_probability']}%"
    )

    print(
        f"\nAI Decision: "
        f"{result['recommended_action']}"
    )

    print(
        f"\nReason:\n"
        f"{result['reason']}"
    )

    # --------------------------------------------------------
    # POLICY CHECK
    # --------------------------------------------------------

    policy = policy_check(
        transaction,
        result
    )

    print("\n----------------------------------------------")
    print("POLICY GATE")
    print("----------------------------------------------")

    if policy["allowed"]:

        print("Policy status: APPROVED")
        print(f"Reason: {policy['reason']}")

        # ----------------------------------------------------
        # EXECUTE ACTION
        # ----------------------------------------------------

        execution = execute_payment(
            transaction,
            result["recommended_action"],
            result["recovery_probability"]
        )

        print(
            f"\nRecovered amount: "
            f"₹{execution['recovered_amount']:,.2f}"
        )

    else:

        print("Policy status: BLOCKED")
        print(f"Reason: {policy['reason']}")