import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)

# ============================================================
# 1. LOAD DATA
# ============================================================

DATA_PATH = "data/failed_payments.csv"

df = pd.read_csv(DATA_PATH)

print("\n==============================================")
print("        RECOVERAI MODEL TRAINING")
print("==============================================")

print(f"\nDataset size: {len(df):,} transactions")


# ============================================================
# 2. FEATURES
# ============================================================

features = [
    "amount",
    "payment_method",
    "failure_reason",
    "previous_failures",
    "retry_count",
    "customer_age_days",
    "hour",
    "device_change",
    "location_change"
]

target = "recovered"

X = df[features]
y = df[target]


# ============================================================
# 3. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print(f"Training samples: {len(X_train):,}")
print(f"Testing samples:  {len(X_test):,}")


# ============================================================
# 4. CATEGORICAL + NUMERICAL FEATURES
# ============================================================

categorical_features = [
    "payment_method",
    "failure_reason"
]

numerical_features = [
    "amount",
    "previous_failures",
    "retry_count",
    "customer_age_days",
    "hour",
    "device_change",
    "location_change"
]


# ============================================================
# 5. PREPROCESSING
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        )
    ],
    remainder="passthrough"
)


# ============================================================
# 6. RANDOM FOREST MODEL
# ============================================================

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=12,
    random_state=42,
    class_weight="balanced"
)


# ============================================================
# 7. COMPLETE PIPELINE
# ============================================================

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# ============================================================
# 8. TRAIN
# ============================================================

print("\nTraining model...")

pipeline.fit(X_train, y_train)

print("Training complete!")


# ============================================================
# 9. PREDICTIONS
# ============================================================

y_pred = pipeline.predict(X_test)

y_probability = pipeline.predict_proba(X_test)[:, 1]


# ============================================================
# 10. MODEL METRICS
# ============================================================

accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    y_probability
)


print("\n==============================================")
print("              MODEL PERFORMANCE")
print("==============================================")

print(f"\nAccuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"ROC-AUC   : {roc_auc:.4f}")


# ============================================================
# 11. CLASSIFICATION REPORT
# ============================================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Not Recovered",
            "Recovered"
        ],
        zero_division=0
    )
)


# ============================================================
# 12. CONFUSION MATRIX
# ============================================================

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ============================================================
# 13. SAVE MODEL
# ============================================================

MODEL_PATH = "models/recovery_model.pkl"

joblib.dump(
    pipeline,
    MODEL_PATH
)

print("\n==============================================")
print(f"Model saved to: {MODEL_PATH}")
print("==============================================")