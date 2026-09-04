import os
import sys

import pandas as pd

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# PROJECT ROOT
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
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="RecoverAI API",
    description="Autonomous Revenue Recovery Agent",
    version="1.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATA
# ============================================================

DATA_PATH = os.path.join(
    ROOT_DIR,
    "data",
    "failed_payments.csv"
)

RESULTS_PATH = os.path.join(
    ROOT_DIR,
    "data",
    "recovery_results.csv"
)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "RecoverAI API is running",
        "status": "online"
    }


# ============================================================
# DASHBOARD METRICS
# ============================================================

@app.get("/metrics")
def get_metrics():

    df = pd.read_csv(DATA_PATH)

    total_transactions = len(df)

    revenue_at_risk = df["amount"].sum()

    # --------------------------------------------------------
    # Read recovery results
    # --------------------------------------------------------

    if os.path.exists(RESULTS_PATH):

        results = pd.read_csv(RESULTS_PATH)

        print("========================================")
        print("METRICS READING FILE:", RESULTS_PATH)
        print("ROWS IN RESULTS:", len(results))

        recovered_revenue = pd.to_numeric(
            results["recovered_amount"],
            errors="coerce"
        ).fillna(0).sum()

        print(
            "RECOVERED REVENUE:",
            recovered_revenue
        )

        print("LAST 5 ROWS:")
        print(
            results.tail(5).to_string()
        )

        # ----------------------------------------------------
        # Recovery attempts
        # ----------------------------------------------------

        recovery_attempts = (
            results["action"]
            .astype(str)
            .str.upper()
            .isin([
                "RETRY",
                "RETRY_LATER"
            ])
            .sum()
        )

        # ----------------------------------------------------
        # Successful recoveries
        # ----------------------------------------------------

        successful_recoveries = (
            results["status"]
            .astype(str)
            .str.upper()
            .eq("SUCCESS")
            .sum()
        )

        # ----------------------------------------------------
        # Blocked actions
        # ----------------------------------------------------

        blocked_actions = (
            results["policy"]
            .astype(str)
            .str.upper()
            .eq("BLOCKED")
            .sum()
        )

        # ----------------------------------------------------
        # Action counts
        # ----------------------------------------------------

        retry_actions = (
            results["action"]
            .astype(str)
            .str.upper()
            .eq("RETRY")
            .sum()
        )

        retry_later_actions = (
            results["action"]
            .astype(str)
            .str.upper()
            .eq("RETRY_LATER")
            .sum()
        )

        update_actions = (
            results["action"]
            .astype(str)
            .str.upper()
            .eq("UPDATE_PAYMENT_METHOD")
            .sum()
        )

        stop_actions = (
            results["action"]
            .astype(str)
            .str.upper()
            .eq("STOP")
            .sum()
        )

    else:

        recovery_attempts = 0
        successful_recoveries = 0
        recovered_revenue = 0
        blocked_actions = 0

        retry_actions = 0
        retry_later_actions = 0
        update_actions = 0
        stop_actions = 0


    # ========================================================
    # RECOVERY RATE
    # ========================================================

    if recovery_attempts > 0:

        recovery_rate = (
            successful_recoveries /
            recovery_attempts
        ) * 100

    else:

        recovery_rate = 0


    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "total_transactions":
            int(total_transactions),

        "revenue_at_risk":
            round(
                float(revenue_at_risk),
                2
            ),

        "recovery_attempts":
            int(recovery_attempts),

        "successful_recoveries":
            int(successful_recoveries),

        "recovery_rate":
            round(
                float(recovery_rate),
                2
            ),

        "recovered_revenue":
            round(
                float(recovered_revenue),
                2
            ),

        "blocked_actions":
            int(blocked_actions),

        "actions": {

            "retry":
                int(retry_actions),

            "retry_later":
                int(retry_later_actions),

            "update_payment":
                int(update_actions),

            "stop":
                int(stop_actions)
        }
    }


# ============================================================
# TRANSACTIONS
# ============================================================

@app.get("/transactions")
def get_transactions():

    if not os.path.exists(RESULTS_PATH):

        return []

    df = pd.read_csv(
        RESULTS_PATH
    )

    # --------------------------------------------------------
    # Latest 100 transactions
    # --------------------------------------------------------

    df = df.tail(100)

    return df.to_dict(
        orient="records"
    )


# ============================================================
# SINGLE TRANSACTION ANALYSIS
# ============================================================

@app.post("/analyze")
def analyze_transaction(
    transaction: dict
):

    decision = analyze_payment(
        transaction
    )

    policy = policy_check(
        transaction,
        decision
    )

    return {

        "transaction":
            transaction,

        "ai_decision":
            decision,

        "policy":
            policy
    }


# ============================================================
# RUN RECOVERY FOR ONE TRANSACTION
# ============================================================

@app.post("/recover")
def recover_transaction(
    transaction: dict
):

    # ========================================================
    # AI ANALYSIS
    # ========================================================

    decision = analyze_payment(
        transaction
    )


    # ========================================================
    # POLICY VALIDATION
    # ========================================================

    policy = policy_check(
        transaction,
        decision
    )


    # ========================================================
    # POLICY BLOCKED
    # ========================================================

    if not policy["allowed"]:

        return {

            "success":
                False,

            "status":
                "BLOCKED",

            "reason":
                policy["reason"],

            "decision":
                decision,

            "policy":
                policy
        }


    # ========================================================
    # EXECUTE PAYMENT
    # ========================================================

    execution = execute_payment(

        transaction,

        decision[
            "recommended_action"
        ],

        decision[
            "recovery_probability"
        ],

        verbose=False
    )


    # ========================================================
    # SAVE LIVE RECOVERY RESULT
    # ========================================================

    live_result = {

        "transaction_id":
            transaction[
                "transaction_id"
            ],

        "amount":
            transaction[
                "amount"
            ],

        "failure_reason":
            transaction[
                "failure_reason"
            ],

        "recovery_probability":
            decision[
                "recovery_probability"
            ],

        "action":
            decision[
                "recommended_action"
            ],

        "policy":
            "APPROVED"
            if policy["allowed"]
            else "BLOCKED",

        "status":
            execution[
                "status"
            ],

        "recovered_amount":
            execution[
                "recovered_amount"
            ],

        "reason":
            decision[
                "reason"
            ]
    }


    # ========================================================
    # APPEND RESULT TO CSV
    # ========================================================

    if os.path.exists(
        RESULTS_PATH
    ):

        results_df = pd.read_csv(
            RESULTS_PATH
        )

        # IMPORTANT:
        # Do NOT delete previous LIVE-DEMO rows.
        # Every recovery click creates a new event.

        results_df = pd.concat(
            [
                results_df,
                pd.DataFrame(
                    [live_result]
                )
            ],
            ignore_index=True
        )

    else:

        results_df = pd.DataFrame(
            [live_result]
        )


    # ========================================================
    # WRITE CSV
    # ========================================================

    results_df.to_csv(
        RESULTS_PATH,
        index=False
    )


    # ========================================================
    # DEBUG OUTPUT
    # ========================================================

    print("========================================")
    print("LIVE RECOVERY SAVED")
    print("TRANSACTION:", transaction["transaction_id"])
    print("ACTION:", decision["recommended_action"])
    print("POLICY:", policy["allowed"])
    print("STATUS:", execution["status"])
    print(
        "RECOVERED:",
        execution["recovered_amount"]
    )
    print(
        "TOTAL CSV ROWS:",
        len(results_df)
    )
    print("========================================")


    # ========================================================
    # RESPONSE TO FRONTEND
    # ========================================================

    return {

        "success":
            execution[
                "status"
            ] == "SUCCESS",

        "status":
            execution[
                "status"
            ],

        "recovered_amount":
            execution[
                "recovered_amount"
            ],

        "decision":
            decision,

        "policy":
            policy
    }