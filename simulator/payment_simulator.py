import random


# ============================================================
# POLICY SETTINGS
# ============================================================

MAX_AUTO_RETRY_AMOUNT = 10000
MAX_RETRIES = 2
MIN_RECOVERY_PROBABILITY = 70


# ============================================================
# POLICY GATE
# ============================================================

def policy_check(transaction, decision):

    amount = transaction["amount"]
    retry_count = transaction["retry_count"]
    probability = decision["recovery_probability"]
    action = decision["recommended_action"]

    # --------------------------------------------------------
    # Rule 1: Suspicious transactions
    # --------------------------------------------------------

    if transaction["failure_reason"] == "suspicious_transaction":

        return {
            "allowed": False,
            "reason": "Suspicious transaction requires manual review."
        }

    # --------------------------------------------------------
    # Rule 2: Maximum retries
    # --------------------------------------------------------

    if retry_count >= MAX_RETRIES:

        return {
            "allowed": False,
            "reason": "Maximum retry limit exceeded."
        }

    # --------------------------------------------------------
    # Rule 3: Amount limit
    # --------------------------------------------------------

    if action == "RETRY" and amount > MAX_AUTO_RETRY_AMOUNT:

        return {
            "allowed": False,
            "reason": "Transaction exceeds automatic retry amount limit."
        }

    # --------------------------------------------------------
    # Rule 4: Recovery probability
    # --------------------------------------------------------

    if action == "RETRY" and probability < MIN_RECOVERY_PROBABILITY:

        return {
            "allowed": False,
            "reason": "Recovery probability below safety threshold."
        }

    # --------------------------------------------------------
    # Action approved
    # --------------------------------------------------------

    return {
        "allowed": True,
        "reason": "Action passed all safety policies."
    }


# ============================================================
# PAYMENT SIMULATOR
# ============================================================

def execute_payment(
    transaction,
    action,
    recovery_probability,
    verbose=False
):

    # --------------------------------------------------------
    # Optional terminal output
    # --------------------------------------------------------

    if verbose:

        print("\n----------------------------------------------")
        print("PAYMENT SIMULATOR")
        print("----------------------------------------------")

        print(
            f"Transaction: "
            f"{transaction['transaction_id']}"
        )

        print(
            f"Action: "
            f"{action}"
        )

    # --------------------------------------------------------
    # Actions that don't execute a payment
    # --------------------------------------------------------

    if action not in ["RETRY", "RETRY_LATER"]:

        if verbose:
            print("Payment not executed.")

        return {
            "status": "NOT_EXECUTED",
            "recovered_amount": 0
        }

   # --------------------------------------------------------
# Simulate payment result
# --------------------------------------------------------

    if str(transaction["transaction_id"]).startswith("LIVE-DEMO-"):
        # Deterministic success for live dashboard demo transactions.
        # This keeps the presentation reliable without changing normal simulation behavior.
        success = True
    else:
        # Realistic probabilistic simulation for other transactions.
        success = random.random() < (
            recovery_probability / 100
        )
    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    if success:

        if verbose:
            print("Payment result: SUCCESS")

        return {
            "status": "SUCCESS",
            "recovered_amount": transaction["amount"]
        }

    # --------------------------------------------------------
    # FAILURE
    # --------------------------------------------------------

    else:

        if verbose:
            print("Payment result: FAILED")

        return {
            "status": "FAILED",
            "recovered_amount": 0
        }