# pyre-ignore-all-errors
"""
Model Training Pipeline:
  - Random Forest + XGBoost + LightGBM -> Soft Voting Ensemble
  - Saves model/phishing_model.pkl and model/feature_names.pkl
  - Prints full evaluation report
"""

import os, sys, json, warnings
warnings.filterwarnings("ignore")

import numpy  as np
import pandas as pd
import joblib

from sklearn.ensemble          import RandomForestClassifier, VotingClassifier
from sklearn.model_selection   import train_test_split
from sklearn.preprocessing     import StandardScaler
from sklearn.metrics           import (accuracy_score, precision_score,
                                       recall_score, f1_score,
                                       confusion_matrix, classification_report)
from sklearn.pipeline          import Pipeline

try:
    from xgboost  import XGBClassifier
    HAS_XGB = True
except ImportError:
    print("[WARN] xgboost not installed — skipping"); HAS_XGB = False

try:
    from lightgbm import LGBMClassifier
    HAS_LGB = True
except ImportError:
    print("[WARN] lightgbm not installed — skipping"); HAS_LGB = False

# ── Local imports ─────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from features import FEATURE_NAMES
from dataset  import generate_dataset

MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")


def load_or_generate_data(csv_path: str = "dataset.csv") -> pd.DataFrame:
    backend_csv = os.path.join(os.path.dirname(__file__), csv_path)
    if os.path.exists(backend_csv):
        print(f"Loading existing dataset: {backend_csv}")
        return pd.read_csv(backend_csv)
    print("Dataset not found — generating …")
    return generate_dataset(output_path=backend_csv)


def evaluate(name: str, model, X_test, y_test) -> dict:
    y_pred = model.predict(X_test)
    acc  = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec  = recall_score(y_test, y_pred, zero_division=0)
    f1   = f1_score(y_test, y_pred, zero_division=0)
    cm   = confusion_matrix(y_test, y_pred).tolist()
    print(f"\n{'='*50}")
    print(f"  {name}")
    print(f"{'='*50}")
    print(f"  Accuracy : {acc:.4f}")
    print(f"  Precision: {prec:.4f}")
    print(f"  Recall   : {rec:.4f}  <-- most important")
    print(f"  F1 Score : {f1:.4f}")
    print(f"  Confusion Matrix:\n  {np.array(cm)}")
    return {"accuracy": round(acc,4), "precision": round(prec,4),
            "recall": round(rec,4), "f1": round(f1,4), "confusion_matrix": cm}


def get_feature_importances(model_name: str, clf, feature_names: list) -> list:
    """Extract feature importances from RF or XGB sub-estimators."""
    try:
        if model_name == "rf":
            imp = clf.named_estimators_["rf"].feature_importances_
        elif model_name == "xgb" and HAS_XGB:
            imp = clf.named_estimators_["xgb"].feature_importances_
        else:
            return []
        pairs = sorted(zip(feature_names, imp.tolist()),
                       key=lambda x: x[1], reverse=True)
        return [{"feature": f, "importance": round(v, 5)} for f, v in pairs]
    except Exception:
        return []


def train():
    os.makedirs(MODEL_DIR, exist_ok=True)

    # ── 1. Data ───────────────────────────────────────────────────────────────
    df = load_or_generate_data()
    X  = df[FEATURE_NAMES].values
    y  = df["label"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y)

    print(f"\nTrain size: {len(X_train)}  |  Test size: {len(X_test)}")
    print(f"Phishing in train: {y_train.sum()} / {len(y_train)}")

    # ── 2. Build estimators ───────────────────────────────────────────────────
    rf = RandomForestClassifier(
        n_estimators=300, max_depth=None,
        min_samples_split=2, class_weight="balanced",
        random_state=42, n_jobs=-1)

    estimators = [("rf", rf)]

    if HAS_XGB:
        xgb = XGBClassifier(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            use_label_encoder=False, eval_metric="logloss",
            random_state=42, n_jobs=-1)
        estimators.append(("xgb", xgb))

    if HAS_LGB:
        lgb = LGBMClassifier(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            class_weight="balanced",
            random_state=42, n_jobs=-1, verbose=-1)
        estimators.append(("lgb", lgb))

    voting = VotingClassifier(estimators=estimators, voting="soft", n_jobs=-1)

    # ── 3. Train ──────────────────────────────────────────────────────────────
    print(f"\nTraining {[n for n,_ in estimators]} …")
    voting.fit(X_train, y_train)

    # ── 4. Evaluate each base model + ensemble ────────────────────────────────
    metrics_dict = {}
    for name, clf in voting.named_estimators_.items():
        metrics_dict[name.upper()] = evaluate(name.upper(), clf, X_test, y_test)
    metrics_dict["Ensemble"] = evaluate("Voting Ensemble", voting, X_test, y_test)

    # ── 5. Feature importances ────────────────────────────────────────────────
    rf_imp  = get_feature_importances("rf",  voting, FEATURE_NAMES)
    xgb_imp = get_feature_importances("xgb", voting, FEATURE_NAMES) if HAS_XGB else []

    # ── 6. Save artefacts ─────────────────────────────────────────────────────
    joblib.dump(voting,       os.path.join(MODEL_DIR, "phishing_model.pkl"))
    joblib.dump(FEATURE_NAMES, os.path.join(MODEL_DIR, "feature_names.pkl"))

    meta = {
        "metrics":          metrics_dict,
        "rf_importances":   rf_imp,
        "xgb_importances":  xgb_imp,
        "feature_names":    FEATURE_NAMES,
        "n_features":       len(FEATURE_NAMES),
    }
    with open(os.path.join(MODEL_DIR, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print("\n[OK] Model saved ->", os.path.join(MODEL_DIR, "phishing_model.pkl"))
    print("[OK] Metadata  ->", os.path.join(MODEL_DIR, "metadata.json"))
    return voting, meta


if __name__ == "__main__":
    train()
