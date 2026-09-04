import { useEffect, useRef, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

function formatINR(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value || 0);
}

function App() {
  const [metrics, setMetrics] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);

  const [recovering, setRecovering] = useState(false);
  const [recoveryResult, setRecoveryResult] = useState(null);
  const [recoveryError, setRecoveryError] = useState(null);

  // ============================================================
  // AUTONOMOUS AGENT EXECUTION STAGE
  // ============================================================

  const [agentStage, setAgentStage] = useState("idle");
  const [agentTransactionId, setAgentTransactionId] = useState("");

  // ============================================================
  // LIVE DEMO TRANSACTION COUNTER
  // ============================================================

  const demoCounter = useRef(1);

  // ============================================================
  // REFRESH DASHBOARD
  // ============================================================

  const refreshDashboard = async () => {
    try {
      console.log("Refreshing dashboard...");

      // ----------------------------------------------------------
      // GET UPDATED METRICS
      // ----------------------------------------------------------

      const metricsResponse = await fetch(
        `${API}/metrics?t=${Date.now()}`,
        {
          method: "GET",
          cache: "no-store",
          headers: {
            "Cache-Control": "no-cache",
            Pragma: "no-cache",
          },
        }
      );

      if (!metricsResponse.ok) {
        throw new Error(
          `Metrics error: ${metricsResponse.status}`
        );
      }

      const metricsData = await metricsResponse.json();

      console.log(
        "NEW METRICS FROM BACKEND:",
        metricsData
      );

      // Force React to receive a fresh object
      setMetrics({ ...metricsData });

      // ----------------------------------------------------------
      // GET UPDATED TRANSACTIONS
      // ----------------------------------------------------------

      const transactionsResponse = await fetch(
        `${API}/transactions?t=${Date.now()}`,
        {
          method: "GET",
          cache: "no-store",
          headers: {
            "Cache-Control": "no-cache",
            Pragma: "no-cache",
          },
        }
      );

      if (!transactionsResponse.ok) {
        throw new Error(
          `Transactions error: ${transactionsResponse.status}`
        );
      }

      const transactionsData =
        await transactionsResponse.json();

      console.log(
        "NEW TRANSACTIONS FROM BACKEND:",
        transactionsData
      );

      setTransactions([...transactionsData]);

      // ----------------------------------------------------------
      // FIND NEXT LIVE DEMO NUMBER
      // ----------------------------------------------------------

      let highestDemoNumber = 0;

      transactionsData.forEach((tx) => {
        if (
          tx.transaction_id &&
          tx.transaction_id.startsWith("LIVE-DEMO-")
        ) {
          const number = parseInt(
            tx.transaction_id.replace("LIVE-DEMO-", ""),
            10
          );

          if (!isNaN(number)) {
            highestDemoNumber = Math.max(
              highestDemoNumber,
              number
            );
          }
        }
      });

      demoCounter.current = highestDemoNumber + 1;

      console.log(
        "NEXT LIVE DEMO:",
        `LIVE-DEMO-${String(
          demoCounter.current
        ).padStart(3, "0")}`
      );

    } catch (error) {
      console.error(
        "Dashboard refresh failed:",
        error
      );

      throw error;
    }
  };

  // ============================================================
  // RUN RECOVERAI
  // ============================================================

  const runRecoverAI = async () => {
    setRecovering(true);
    setRecoveryError(null);
    setRecoveryResult(null);

    try {
      console.log("========================================");
      console.log("RUNNING RECOVERAI");
      console.log("========================================");

      // ----------------------------------------------------------
      // CREATE UNIQUE LIVE DEMO TRANSACTION
      // ----------------------------------------------------------

      const demoNumber = demoCounter.current;

      const demoTransaction = {
        transaction_id: `LIVE-DEMO-${String(
          demoNumber
        ).padStart(3, "0")}`,

        amount: 1800,

        payment_method: "card",

        failure_reason: "bank_timeout",

        previous_failures: 1,

        retry_count: 0,

        customer_age_days: 500,

        hour: new Date().getHours(),

        device_change: 0,

        location_change: 0,
      };

      demoCounter.current = demoNumber + 1;
      setAgentTransactionId(demoTransaction.transaction_id);

      console.log("Demo transaction:", demoTransaction);

      // ----------------------------------------------------------
      // AUTONOMOUS AGENT PIPELINE
      // ----------------------------------------------------------

      // Stage 1 — Analyze
      setAgentStage("analyzing");

      await new Promise((resolve) =>
        setTimeout(resolve, 650)
      );

      // Stage 2 — Predict
      setAgentStage("predicting");

      await new Promise((resolve) =>
        setTimeout(resolve, 700)
      );

      // Stage 3 — Policy validation
      setAgentStage("validating");

      await new Promise((resolve) =>
        setTimeout(resolve, 500)
      );

      // Stage 4 — Execute actual backend recovery
      setAgentStage("executing");

      const response = await fetch(
        `${API}/recover?t=${Date.now()}`,
        {
          method: "POST",
          cache: "no-store",

          headers: {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
          },

          body: JSON.stringify(demoTransaction),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Backend error: ${response.status}`
        );
      }

      const data = await response.json();

      console.log("RECOVERAI RESPONSE:", data);

      // Give the execution state a moment to be visible.
      await new Promise((resolve) =>
        setTimeout(resolve, 700)
      );

      if (data.status === "BLOCKED") {
        setAgentStage("blocked");
      } else {
        setAgentStage(
          data.status === "SUCCESS"
            ? "success"
            : "failed"
        );
      }

      // ----------------------------------------------------------
      // SHOW RESULT POPUP
      // ----------------------------------------------------------

      setRecoveryResult({
        ...data,
        transaction: demoTransaction,
      });

      // ----------------------------------------------------------
      // WAIT FOR BACKEND TO FINISH WRITING CSV
      // THEN FETCH METRICS AGAIN
      // ----------------------------------------------------------

      await new Promise((resolve) =>
        setTimeout(resolve, 300)
      );

      console.log(
        "Fetching updated dashboard numbers..."
      );

      await refreshDashboard();

      console.log(
        "Dashboard successfully refreshed."
      );

    } catch (error) {
      console.error(
        "RecoverAI error:",
        error
      );

      setAgentStage("error");

      setRecoveryError(
        error.message || "Recovery failed"
      );

    } finally {
      setRecovering(false);

      // Keep the last stage in state so the result popup
      // can be inspected without affecting the dashboard.
    }
  };

  // ============================================================
  // INITIAL DATA LOAD
  // ============================================================

  useEffect(() => {
    async function loadData() {
      try {
        console.log(
          "Loading RecoverAI dashboard..."
        );

        await refreshDashboard();

      } catch (error) {
        console.error(
          "Failed to connect to RecoverAI:",
          error
        );

      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  // ============================================================
  // LOADING SCREEN
  // ============================================================

  if (loading) {
    return (
      <div className="loading">

        <div className="loader"></div>

        <h2>
          Loading RecoverAI...
        </h2>

        <p>
          Connecting to AI recovery engine
        </p>

      </div>
    );
  }

  // ============================================================
  // OFFLINE SCREEN
  // ============================================================

  if (!metrics) {
    return (
      <div className="loading">

        <h2>
          RecoverAI is offline
        </h2>

        <p>
          Make sure the FastAPI backend is running
          on port 8000.
        </p>

      </div>
    );
  }

  // ============================================================
  // MAIN UI
  // ============================================================

  return (
    <div className="app">

      {/* ================================================= */}
      {/* HEADER */}
      {/* ================================================= */}

      <header className="header">

        <div className="brand">

          <div className="logo">
            R
          </div>

          <div>

            <h1>
              RecoverAI
            </h1>

            <span>
              Autonomous Revenue Recovery
            </span>

          </div>

        </div>

        <div className="status">

          <span className="status-dot"></span>

          AI ENGINE LIVE

        </div>

      </header>


      {/* ================================================= */}
      {/* HERO */}
      {/* ================================================= */}

      <section className="hero">

        <div>

          <p className="eyebrow">
            AI-POWERED PAYMENT RECOVERY
          </p>

          <h2>
            Recover lost revenue
            <br />

            <span>
              autonomously.
            </span>

          </h2>

          <p className="hero-text">
            RecoverAI analyzes failed payments,
            predicts recovery probability, chooses
            the best action, and validates every
            action through a safety policy.
          </p>

        </div>


        <div className="hero-badge">

          <div className="brain">
            ✦
          </div>

          <div>

            <strong>
              AI Agent
            </strong>

            <p>
              Observe → Decide → Validate → Recover
            </p>

          </div>

        </div>


        {/* ================================================= */}
        {/* RUN BUTTON */}
        {/* ================================================= */}

        <button
          className="run-recovery-btn"
          onClick={runRecoverAI}
          disabled={recovering}
        >

          {recovering
            ? "⟳ AI RECOVERING..."
            : "▶ RUN RECOVERAI"}

        </button>

      </section>


      {/* ================================================= */}
      {/* KPI CARDS */}
      {/* ================================================= */}

      <section className="metrics-grid">

        {/* REVENUE AT RISK */}

        <div className="metric-card">

          <p>
            REVENUE AT RISK
          </p>

          <h3>
            {formatINR(
              metrics.revenue_at_risk
            )}
          </h3>

          <span className="metric-sub">
            Across{" "}
            {metrics.total_transactions.toLocaleString(
              "en-IN"
            )}{" "}
            failed payments
          </span>

        </div>


        {/* RECOVERED REVENUE */}

        <div className="metric-card highlight">

          <p>
            RECOVERED REVENUE
          </p>

          <h3>
            {formatINR(
              metrics.recovered_revenue
            )}
          </h3>

          <span className="metric-sub">
            Simulated successful recoveries
          </span>

        </div>


        {/* RECOVERY RATE */}

        <div className="metric-card">

          <p>
            RECOVERY RATE
          </p>

          <h3>
            {metrics.recovery_rate}%
          </h3>

          <span className="metric-sub">
            Successful / attempted
          </span>

        </div>


        {/* BLOCKED ACTIONS */}

        <div className="metric-card">

          <p>
            BLOCKED ACTIONS
          </p>

          <h3>
            {metrics.blocked_actions.toLocaleString(
              "en-IN"
            )}
          </h3>

          <span className="metric-sub">
            Safety policy interventions
          </span>

        </div>

      </section>


      {/* ================================================= */}
      {/* ACTIONS */}
      {/* ================================================= */}

      <section className="panel">

        <div className="panel-header">

          <div>

            <p className="eyebrow">
              AGENT DECISIONS
            </p>

            <h2>
              Recovery strategy
            </h2>

          </div>

          <div className="attempts">

            {metrics.recovery_attempts.toLocaleString(
              "en-IN"
            )}

            <span>
              {" "}attempts
            </span>

          </div>

        </div>


        <div className="actions">

          <Action
            icon="↻"
            name="Retry"
            value={metrics.actions.retry}
            total={metrics.total_transactions}
          />

          <Action
            icon="◷"
            name="Retry Later"
            value={metrics.actions.retry_later}
            total={metrics.total_transactions}
          />

          <Action
            icon="▣"
            name="Update Payment"
            value={metrics.actions.update_payment}
            total={metrics.total_transactions}
          />

          <Action
            icon="⊘"
            name="Stop"
            value={metrics.actions.stop}
            total={metrics.total_transactions}
          />

        </div>

      </section>


      {/* ================================================= */}
      {/* TRANSACTIONS */}
      {/* ================================================= */}

      <section className="panel">

        <div className="panel-header">

          <div>

            <p className="eyebrow">
              LIVE RECOVERY LOG
            </p>

            <h2>
              Recent transactions
            </h2>

          </div>

          <span className="count">
            {transactions.length} records
          </span>

        </div>


        <div className="table-wrapper">

          <table>

            <thead>

              <tr>

                <th>
                  Transaction
                </th>

                <th>
                  Amount
                </th>

                <th>
                  Failure
                </th>

                <th>
                  Recovery probability
                </th>

                <th>
                  AI action
                </th>

                <th>
                  Status
                </th>

              </tr>

            </thead>


            <tbody>

              {transactions
                .slice()
                .reverse()
                .slice(0, 12)
                .map((tx, index) => (

                  <tr
                    key={`${tx.transaction_id}-${index}`}
                    onClick={() =>
                      setSelected(tx)
                    }
                  >

                    <td className="transaction-id">
                      {tx.transaction_id}
                    </td>


                    <td>
                      {formatINR(tx.amount)}
                    </td>


                    <td>

                      <span className="failure">

                        {tx.failure_reason
                          ? tx.failure_reason.replaceAll(
                              "_",
                              " "
                            )
                          : "N/A"}

                      </span>

                    </td>


                    <td>

                      <div className="probability">

                        <div className="probability-bar">

                          <div
                            style={{
                              width: `${tx.recovery_probability}%`,
                            }}
                          ></div>

                        </div>

                        <span>
                          {tx.recovery_probability}%
                        </span>

                      </div>

                    </td>


                    <td>

                      <ActionBadge
                        action={
                          tx.action || "N/A"
                        }
                      />

                    </td>


                    <td>

                      <StatusBadge
                        status={
                          tx.status || "N/A"
                        }
                      />

                    </td>

                  </tr>

                ))}

            </tbody>

          </table>

        </div>

      </section>


      {/* ================================================= */}
      {/* TRANSACTION DETAIL MODAL */}
      {/* ================================================= */}

      {selected && (
        <DecisionTrace
          transaction={selected}
          onClose={() => setSelected(null)}
        />
      )}


      {/* ================================================= */}
      {/* AUTONOMOUS AGENT EXECUTION */}
      {/* ================================================= */}

      {recovering && (
        <AgentExecution
          stage={agentStage}
          transactionId={agentTransactionId}
        />
      )}


      {/* ================================================= */}
      {/* RECOVERAI RESULT MODAL */}
      {/* ================================================= */}

      {recoveryResult && (

        <div
          className="modal-background"
          onClick={() =>
            setRecoveryResult(null)
          }
        >

          <div
            className="transaction-modal recovery-result-modal"
            onClick={(e) =>
              e.stopPropagation()
            }
          >

            <button
              className="close"
              onClick={() =>
                setRecoveryResult(null)
              }
            >
              ×
            </button>


            <p className="eyebrow">
              RECOVERAI EXECUTION COMPLETE
            </p>


            <h2>
              {recoveryResult.transaction?.transaction_id ||
                "LIVE-DEMO-001"}
            </h2>


            <div className="detail-amount">

              {formatINR(
                recoveryResult.recovered_amount || 0
              )}

            </div>


            <div className="detail-grid">

              <Detail
                label="Status"
                value={
                  recoveryResult.status ||
                  "N/A"
                }
              />


              <Detail
                label="AI Decision"
                value={
                  recoveryResult.decision
                    ?.recommended_action ||
                  recoveryResult.decision ||
                  "N/A"
                }
              />


              <Detail
                label="Policy"
                value={
                  recoveryResult.policy?.allowed
                    ? "APPROVED"
                    : "BLOCKED"
                }
              />


              <Detail
                label="Recovered"
                value={formatINR(
                  recoveryResult.recovered_amount || 0
                )}
              />

            </div>


            <div className="reason-box">

              <p>
                RECOVERAI AGENT
              </p>

              <span>
                {recoveryResult.decision?.reason ||
                  "Recovery workflow completed."}
              </span>

            </div>

          </div>

        </div>

      )}


      {/* ================================================= */}
      {/* ERROR */}
      {/* ================================================= */}

      {recoveryError && (

        <div className="error-message">

          RecoverAI error: {recoveryError}

        </div>

      )}

    </div>
  );
}


// ============================================================
// AI DECISION TRACE COMPONENT
// ============================================================

function DecisionTrace({
  transaction,
  onClose,
}) {
  const probability = Number(
    transaction.recovery_probability || 0
  );

  const action = transaction.action
    ? transaction.action.replaceAll("_", " ")
    : "N/A";

  const failure = transaction.failure_reason
    ? transaction.failure_reason.replaceAll("_", " ")
    : "N/A";

  const policy =
    String(transaction.policy || "N/A").toUpperCase();

  const status =
    String(transaction.status || "N/A").toUpperCase();

  const isApproved =
    policy === "APPROVED";

  const isSuccess =
    status === "SUCCESS";

  const actionLabel =
    action.charAt(0).toUpperCase() + action.slice(1);

  return (
    <div
      className="modal-background"
      onClick={onClose}
      style={{ zIndex: 1800 }}
    >
      <div
        className="transaction-modal"
        onClick={(e) => e.stopPropagation()}
        style={{
          width: "min(720px, 94vw)",
          maxHeight: "88vh",
          overflowY: "auto",
        }}
      >
        <button
          className="close"
          onClick={onClose}
        >
          ×
        </button>

        <p className="eyebrow">
          AI DECISION TRACE
        </p>

        <div
          style={{
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
            gap: "20px",
            marginBottom: "22px",
          }}
        >
          <div>
            <h2 style={{ marginBottom: "6px" }}>
              {transaction.transaction_id}
            </h2>

            <p
              style={{
                margin: 0,
                opacity: 0.55,
                fontSize: "13px",
              }}
            >
              Autonomous recovery decision
            </p>
          </div>

          <div
            style={{
              padding: "8px 12px",
              borderRadius: "999px",
              fontSize: "11px",
              fontWeight: 700,
              letterSpacing: "0.06em",
              background: isSuccess
                ? "rgba(34,197,94,0.12)"
                : isApproved
                ? "rgba(139,92,246,0.12)"
                : "rgba(245,158,11,0.12)",
              color: isSuccess
                ? "#22c55e"
                : isApproved
                ? "#a78bfa"
                : "#f59e0b",
            }}
          >
            {isSuccess
              ? "RECOVERED"
              : isApproved
              ? "APPROVED"
              : policy}
          </div>
        </div>

        {/* -------------------------------------------------- */}
        {/* DECISION PIPELINE */}
        {/* -------------------------------------------------- */}

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(5, minmax(0, 1fr))",
            gap: "6px",
            marginBottom: "28px",
          }}
        >
          {[
            ["01", "Payment failed"],
            ["02", "AI analyzed"],
            ["03", "Action selected"],
            ["04", "Policy checked"],
            ["05", "Recovery executed"],
          ].map(([number, label], index) => (
            <div key={number}>
              <div
                style={{
                  height: "4px",
                  borderRadius: "4px",
                  background:
                    "rgba(139,92,246,0.75)",
                  marginBottom: "8px",
                }}
              />

              <div
                style={{
                  fontSize: "9px",
                  fontWeight: 700,
                  opacity: 0.45,
                  letterSpacing: "0.05em",
                }}
              >
                {number}
              </div>

              <div
                style={{
                  fontSize: "10px",
                  lineHeight: 1.3,
                  opacity: index === 4 && !isSuccess
                    ? 0.45
                    : 0.75,
                }}
              >
                {label}
              </div>
            </div>
          ))}
        </div>

        {/* -------------------------------------------------- */}
        {/* AI PROBABILITY */}
        {/* -------------------------------------------------- */}

        <div
          style={{
            padding: "18px",
            borderRadius: "14px",
            background:
              "rgba(139,92,246,0.07)",
            border:
              "1px solid rgba(139,92,246,0.18)",
            marginBottom: "20px",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "10px",
            }}
          >
            <div>
              <p
                style={{
                  margin: 0,
                  fontSize: "11px",
                  fontWeight: 700,
                  letterSpacing: "0.06em",
                  opacity: 0.55,
                }}
              >
                AI RECOVERY PROBABILITY
              </p>

              <strong
                style={{
                  display: "block",
                  marginTop: "5px",
                  fontSize: "14px",
                }}
              >
                Model confidence
              </strong>
            </div>

            <strong
              style={{
                fontSize: "30px",
                lineHeight: 1,
              }}
            >
              {probability}%
            </strong>
          </div>

          <div
            style={{
              height: "8px",
              borderRadius: "99px",
              background:
                "rgba(255,255,255,0.08)",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${Math.min(
                  Math.max(probability, 0),
                  100
                )}%`,
                height: "100%",
                borderRadius: "99px",
                background:
                  "linear-gradient(90deg, #8b5cf6, #22c55e)",
                transition: "width 0.5s ease",
              }}
            />
          </div>
        </div>

        {/* -------------------------------------------------- */}
        {/* DECISION DETAILS */}
        {/* -------------------------------------------------- */}

        <div className="detail-grid">
          <Detail
            label="Failure reason"
            value={failure}
          />

          <Detail
            label="AI action"
            value={actionLabel}
          />

          <Detail
            label="Safety policy"
            value={policy}
          />

          <Detail
            label="Execution"
            value={status}
          />

          <Detail
            label="Original amount"
            value={formatINR(
              transaction.amount
            )}
          />

          <Detail
            label="Recovered amount"
            value={formatINR(
              transaction.recovered_amount
            )}
          />
        </div>

        {/* -------------------------------------------------- */}
        {/* AGENT REASON */}
        {/* -------------------------------------------------- */}

        <div className="reason-box">
          <p>
            WHY DID THE AGENT CHOOSE THIS?
          </p>

          <span>
            {transaction.reason ||
              "No reason available."}
          </span>
        </div>

        {/* -------------------------------------------------- */}
        {/* HUMAN-READABLE SUMMARY */}
        {/* -------------------------------------------------- */}

        <div
          style={{
            marginTop: "16px",
            padding: "15px 16px",
            borderRadius: "12px",
            background:
              "rgba(255,255,255,0.035)",
            border:
              "1px solid rgba(255,255,255,0.07)",
            fontSize: "13px",
            lineHeight: 1.55,
          }}
        >
          <strong>Agent decision:</strong>{" "}
          The payment failed because of{" "}
          <strong>{failure}</strong>. RecoverAI
          estimated a <strong>{probability}%</strong>{" "}
          recovery probability and selected{" "}
          <strong>{actionLabel}</strong>. The safety
          policy was <strong>{policy}</strong>, and
          execution finished with{" "}
          <strong>{status}</strong>.
        </div>
      </div>
    </div>
  );
}


// ============================================================
// AUTONOMOUS AGENT EXECUTION COMPONENT
// ============================================================

function AgentExecution({
  stage,
  transactionId,
}) {
  const stages = [
    {
      id: "analyzing",
      icon: "⌕",
      title: "Analyzing payment",
      description:
        "Reading payment context and failure signals",
    },
    {
      id: "predicting",
      icon: "✦",
      title: "Predicting recovery",
      description:
        "AI model estimates the probability of successful recovery",
    },
    {
      id: "validating",
      icon: "✓",
      title: "Validating safety policy",
      description:
        "Checking whether the recommended action is allowed",
    },
    {
      id: "executing",
      icon: "↻",
      title: "Executing recovery",
      description:
        "Sending the approved recovery action to the payment simulator",
    },
  ];

  const stageIndex = stages.findIndex(
    (item) => item.id === stage
  );

  const isFinished =
    stage === "success" ||
    stage === "failed" ||
    stage === "blocked";

  const isError = stage === "error";

  return (
    <div
      className="modal-background"
      style={{
        zIndex: 2000,
        background: "rgba(5, 8, 20, 0.82)",
        backdropFilter: "blur(8px)",
      }}
    >
      <div
        className="transaction-modal"
        style={{
          width: "min(620px, 92vw)",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: "3px",
            background:
              "linear-gradient(90deg, transparent, #8b5cf6, #22c55e, transparent)",
            animation: "recoverAIProgress 1.6s linear infinite",
          }}
        />

        <p className="eyebrow">
          AUTONOMOUS AI AGENT
        </p>

        <h2 style={{ marginBottom: "8px" }}>
          RecoverAI is working
        </h2>

        <p
          style={{
            marginTop: 0,
            opacity: 0.65,
            fontSize: "14px",
          }}
        >
          Transaction:{" "}
          <strong>{transactionId}</strong>
        </p>

        <div
          style={{
            marginTop: "28px",
            display: "flex",
            flexDirection: "column",
            gap: "12px",
          }}
        >
          {stages.map((item, index) => {
            const completed =
              isFinished ||
              index < stageIndex;

            const active =
              !isFinished &&
              !isError &&
              index === stageIndex;

            const blockedAtValidation =
              stage === "blocked" &&
              item.id === "validating";

            return (
              <div
                key={item.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "14px",
                  padding: "13px 15px",
                  borderRadius: "12px",
                  border: active
                    ? "1px solid rgba(139,92,246,0.55)"
                    : "1px solid rgba(255,255,255,0.07)",
                  background: active
                    ? "rgba(139,92,246,0.10)"
                    : "rgba(255,255,255,0.025)",
                  transition:
                    "all 0.3s ease",
                }}
              >
                <div
                  style={{
                    width: "38px",
                    height: "38px",
                    minWidth: "38px",
                    borderRadius: "50%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "17px",
                    fontWeight: 700,
                    background:
                      completed
                        ? "rgba(34,197,94,0.14)"
                        : active
                        ? "rgba(139,92,246,0.16)"
                        : "rgba(255,255,255,0.06)",
                    color:
                      completed
                        ? "#22c55e"
                        : active
                        ? "#a78bfa"
                        : "rgba(255,255,255,0.4)",
                  }}
                >
                  {completed
                    ? "✓"
                    : active
                    ? "⟳"
                    : item.icon}
                </div>

                <div style={{ flex: 1 }}>
                  <div
                    style={{
                      fontWeight: 650,
                      fontSize: "14px",
                    }}
                  >
                    {item.title}
                  </div>

                  <div
                    style={{
                      marginTop: "3px",
                      fontSize: "12px",
                      opacity: 0.55,
                    }}
                  >
                    {item.description}
                  </div>
                </div>

                <div
                  style={{
                    fontSize: "11px",
                    fontWeight: 700,
                    letterSpacing: "0.06em",
                    color:
                      blockedAtValidation
                        ? "#f59e0b"
                        : completed
                        ? "#22c55e"
                        : active
                        ? "#a78bfa"
                        : "rgba(255,255,255,0.3)",
                  }}
                >
                  {blockedAtValidation
                    ? "BLOCKED"
                    : completed
                    ? "DONE"
                    : active
                    ? "RUNNING"
                    : "WAITING"}
                </div>
              </div>
            );
          })}
        </div>

        <div
          style={{
            marginTop: "22px",
            padding: "14px 16px",
            borderRadius: "12px",
            background:
              "rgba(255,255,255,0.035)",
            border:
              "1px solid rgba(255,255,255,0.07)",
            textAlign: "center",
            fontSize: "13px",
            opacity: 0.75,
          }}
        >
          {isError
            ? "Agent encountered an error."
            : stage === "blocked"
            ? "Safety policy stopped the recovery action."
            : stage === "executing"
            ? "Recovery action is being executed..."
            : stage === "predicting"
            ? "AI is evaluating the best recovery strategy..."
            : stage === "validating"
            ? "Checking recovery action against policy..."
            : "Agent is analyzing the failed payment..."}
        </div>

        <style>
          {`
            @keyframes recoverAIProgress {
              0% {
                transform: translateX(-100%);
              }
              100% {
                transform: translateX(100%);
              }
            }
          `}
        </style>
      </div>
    </div>
  );
}


// ============================================================
// ACTION COMPONENT
// ============================================================

function Action({
  icon,
  name,
  value,
  total,
}) {

  const percentage =
    total > 0
      ? ((value / total) * 100).toFixed(1)
      : 0;

  return (

    <div className="action">

      <div className="action-top">

        <div className="action-name">

          <span className="action-icon">
            {icon}
          </span>

          {name}

        </div>


        <strong>
          {value.toLocaleString("en-IN")}
        </strong>

      </div>


      <div className="action-bar">

        <div
          style={{
            width: `${percentage}%`,
          }}
        ></div>

      </div>


      <span className="action-percent">
        {percentage}% of transactions
      </span>

    </div>
  );
}


// ============================================================
// ACTION BADGE
// ============================================================

function ActionBadge({ action }) {

  const label =
    action.replaceAll("_", " ");

  return (

    <span
      className={`action-badge ${action.toLowerCase()}`}
    >
      {label}
    </span>

  );
}


// ============================================================
// STATUS BADGE
// ============================================================

function StatusBadge({ status }) {

  const success =
    status === "SUCCESS";

  return (

    <span
      className={
        success
          ? "status-badge success"
          : "status-badge"
      }
    >

      {success ? "✓ " : ""}

      {status.replaceAll(
        "_",
        " "
      )}

    </span>

  );
}


// ============================================================
// DETAIL
// ============================================================

function Detail({
  label,
  value,
}) {

  return (

    <div className="detail">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>

  );
}


export default App;