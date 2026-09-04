# RecoverAI

### Autonomous AI Revenue Recovery Agent for Failed Payments

RecoverAI is an AI-powered revenue recovery system designed to intelligently handle failed payment transactions.

Instead of blindly retrying every failed payment, RecoverAI analyzes transaction characteristics, predicts the probability of successful recovery, selects an appropriate recovery action, validates that action through a safety policy, and executes the recovery workflow.

The system combines a machine-learning model, autonomous decision logic, a safety layer, a FastAPI backend, and an interactive React dashboard.

---

## 🚀 Problem

Failed payments create significant revenue leakage for businesses.

A traditional payment recovery system may repeatedly retry failed payments without considering:

- Why the payment failed
- The probability of successful recovery
- Previous payment failures
- Customer history
- Retry count
- Device or location changes
- Appropriate timing for another attempt
- Whether the action should be blocked for safety reasons

RecoverAI addresses this problem by making recovery decisions dynamically for every failed transaction.

---

## 💡 Solution

RecoverAI follows an autonomous recovery workflow:

```text
Failed Payment
      ↓
   Observe
      ↓
 Predict Recovery Probability
      ↓
    Decide
      ↓
 Select Recovery Action
      ↓
 Validate Through Safety Policy
      ↓
     Recover
      ↓
 Update Metrics & Recovery Log
```

The agent follows the principle:

> **Observe → Decide → Validate → Recover**

---

## 🤖 AI Agent Workflow

### 1. Observe

The system receives information about a failed payment, including:

- Transaction amount
- Payment method
- Failure reason
- Previous failures
- Retry count
- Customer age
- Transaction hour
- Device changes
- Location changes

### 2. Predict

The machine-learning model estimates the probability that the payment can be successfully recovered.

### 3. Decide

Based on the transaction characteristics and predicted recovery probability, RecoverAI selects a recovery strategy.

Possible actions include:

- Retry
- Retry Later
- Update Payment
- Stop

### 4. Validate

Before execution, the selected action passes through the safety-policy layer.

The policy can:

- Approve safe actions
- Block unsafe actions
- Prevent unnecessary recovery attempts

### 5. Recover

If the action is approved, the recovery workflow is executed through the simulated payment recovery environment.

The result is then recorded and reflected in the dashboard.

---

## ✨ Key Features

### Autonomous Recovery Agent

Automatically analyzes failed transactions and selects a recovery strategy.

### Machine Learning Prediction

Uses transaction-level features to estimate recovery probability.

### Safety Policy

Every proposed action is validated before execution.

### Interactive Dashboard

Provides a real-time view of:

- Revenue at risk
- Recovered revenue
- Recovery rate
- Blocked actions
- Recovery attempts
- Recovery strategies
- Recent transactions

### Decision Trace

Clicking a transaction displays the reasoning behind the AI decision, including:

- Failure reason
- Recovery probability
- AI action
- Policy decision
- Execution status
- Recovered amount
- Agent reasoning

### Live Demo

The dashboard includes a **RUN RECOVERAI** button that sends a live demo transaction through the complete recovery pipeline.

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │   Failed Payment    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Feature Analysis  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   ML Prediction     │
                    │ Recovery Probability│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Recovery Decision  │
                    │ Retry / Later /     │
                    │ Update / Stop       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Safety Policy     │
                    │ Approve / Block     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Recovery Simulator  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Metrics + Log       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ React Dashboard     │
                    └─────────────────────┘
```

---

## 🧠 Technology Stack

### Frontend

- React
- JavaScript
- HTML
- CSS
- Vite

### Backend

- Python
- FastAPI

### Machine Learning

- Python
- Scikit-learn
- Pickle model

### Data

- CSV
- Synthetic / simulated failed-payment dataset

### Development

- Git
- GitHub
- VS Code

---

## 📁 Project Structure

```text
RecoverAI/
│
├── agent/
│   ├── recovery_agent.py
│   └── run_recovery.py
│
├── backend/
│   └── main.py
│
├── data/
│   ├── failed_payments.csv
│   ├── generate_dataset.py
│   └── recovery_results.csv
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── models/
│   ├── recovery_model.pkl
│   └── train_model.py
│
├── simulator/
│   └── payment_simulator.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/ARYAN-2710/RecoverAI.git
cd RecoverAI
```

### 2. Create a Python virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install frontend dependencies

Open a terminal inside the frontend directory:

```bash
cd frontend
npm install
```

---

## ▶️ Running RecoverAI

RecoverAI requires both the backend and frontend to be running.

### Start the Backend

From the project root:

```bash
uvicorn backend.main:app --reload --port 8000
```

The backend will run at:

```text
http://127.0.0.1:8000
```

### Start the Frontend

Open another terminal:

```bash
cd frontend
npm run dev
```

Vite will provide the local development URL.

Open the displayed URL in your browser.

---

## 🖥️ Dashboard

The RecoverAI dashboard provides a centralized view of the autonomous recovery system.

### Key Metrics

The dashboard displays:

**Revenue at Risk**

Total value associated with failed payments.

**Recovered Revenue**

Revenue successfully recovered by the simulated recovery workflow.

**Recovery Rate**

Percentage of attempted recoveries that were successful.

**Blocked Actions**

Number of actions prevented by the safety policy.

---

## 📊 Recovery Strategies

RecoverAI can select between multiple strategies:

| Strategy | Purpose |
|---|---|
| Retry | Immediately retry the failed payment |
| Retry Later | Delay the next recovery attempt |
| Update Payment | Request/update payment information |
| Stop | Stop further recovery attempts |

The dashboard also shows the distribution of these decisions across transactions.

---

## 🔐 Safety Layer

A key component of RecoverAI is the safety-policy layer.

The AI does not directly execute every action it recommends.

Instead:

```text
AI Recommendation
       ↓
 Safety Validation
       ↓
 ┌─────┴─────┐
 │           │
 ▼           ▼
APPROVED   BLOCKED
 │           │
 ▼           ▼
Execute    Prevent
Action     Action
```

This provides an additional control layer between AI decision-making and action execution.

---

## 🔎 Decision Trace

Users can select transactions from the recovery log to inspect the AI's decision.

The decision trace provides information such as:

```text
Transaction
     ↓
Failure Reason
     ↓
Recovery Probability
     ↓
AI Action
     ↓
Safety Policy
     ↓
Execution Status
     ↓
Recovered Amount
     ↓
AI Reasoning
```

This makes the system more transparent and allows users to understand why a particular recovery action was selected.

---

## 🧪 Live Demonstration

The dashboard includes a **RUN RECOVERAI** button.

When triggered, RecoverAI creates a demo failed-payment transaction and sends it to the backend.

The transaction then passes through:

```text
Demo Transaction
      ↓
AI Recovery Agent
      ↓
Prediction
      ↓
Decision
      ↓
Safety Policy
      ↓
Recovery Simulation
      ↓
Result
      ↓
Dashboard Refresh
```

The resulting transaction is added to the recovery log and the dashboard metrics are refreshed.

---

## 📈 Example Transaction

A demo transaction can contain features such as:

```text
Transaction ID: LIVE-DEMO-001
Amount: ₹1,800
Payment Method: Card
Failure Reason: Bank Timeout
Previous Failures: 1
Retry Count: 0
Customer Age: 500 days
Device Change: No
Location Change: No
```

RecoverAI evaluates these features before selecting the appropriate recovery strategy.

---

## 🎯 Design Goals

RecoverAI was designed around four principles:

### 1. Autonomous

Minimize manual decision-making during payment recovery.

### 2. Intelligent

Use machine-learning predictions rather than relying only on fixed retry rules.

### 3. Safe

Validate AI actions before execution.

### 4. Explainable

Expose the reasoning and execution result behind every recovery decision.

---

## ⚠️ Current Limitations

This project is a prototype and demonstration system.

The current implementation uses:

- Simulated payment transactions
- Synthetic / prepared transaction data
- Simulated recovery execution
- A locally hosted backend
- A locally hosted React dashboard

It is not connected to a production payment gateway.

---

## 🔮 Future Improvements

Potential production improvements include:

- Integration with Stripe/Razorpay/payment gateway APIs
- Real-time payment webhooks
- More advanced ML models
- Customer-level personalization
- Reinforcement learning for recovery strategy optimization
- Automated email/SMS recovery campaigns
- Real-time monitoring and alerting
- A/B testing of recovery strategies
- Production database integration
- Authentication and role-based access
- Cloud deployment
- Model monitoring and drift detection

---

## 🏆 Project Objective

RecoverAI demonstrates how an autonomous AI agent can be used to make revenue-recovery decisions while maintaining a safety and explainability layer.

The goal is not simply to retry failed payments.

The goal is to:

> **Predict → Decide → Validate → Recover**

while minimizing unnecessary actions and making every decision understandable.

---

## 👨‍💻 Author

**ARYAN-2710**

GitHub:  
https://github.com/ARYAN-2710/RecoverAI

---

## 📜 License

This project is intended for educational, research, and demonstration purposes.
