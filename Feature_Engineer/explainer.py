# pyre-ignore-all-errors
"""
SHAP Explainability wrapper for the phishing detection ensemble.
Returns per-URL feature importance values for the React frontend.
"""

import os, warnings
warnings.filterwarnings("ignore")

import numpy as np

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False


_explainer = None

def get_shap_explanation(model, X_row: np.ndarray, feature_names: list) -> list:
    global _explainer
    """
    Returns a list of dicts sorted by absolute SHAP impact:
      [{"feature": str, "value": float, "shap_value": float}, ...]

    Falls back to RF feature importances if SHAP unavailable.
    """
    if not HAS_SHAP:
        # Fallback: use RF feature importances as proxy
        try:
            rf = model.named_estimators_.get("rf")
            if rf is None:
                return []
            imp = rf.feature_importances_
            results = [
                {"feature": fn, "value": float(X_row[0, i]),
                 "shap_value": float(imp[i])}
                for i, fn in enumerate(feature_names)
            ]
            return sorted(results, key=lambda x: abs(x["shap_value"]), reverse=True)
        except Exception:
            return []

    # ── True SHAP via RF sub-estimator ─────────────────────────────────────
    try:
        rf = model.named_estimators_.get("rf")
        if rf is None:
            return _shap_fallback(model, X_row, feature_names)

        if _explainer is None:
            _explainer = shap.TreeExplainer(rf)
            
        shap_values  = _explainer.shap_values(X_row)

        # shap_values shape: [2, n_samples, n_features]  (binary)
        if isinstance(shap_values, list):
            sv = shap_values[1][0]          # class=1 (phishing)
        else:
            sv = shap_values[0]

        results = [
            {"feature": fn, "value": float(X_row[0, i]),
             "shap_value": round(float(sv[i]), 5)}
            for i, fn in enumerate(feature_names)
        ]
        return sorted(results, key=lambda x: abs(x["shap_value"]), reverse=True)

    except Exception as e:
        print(f"[SHAP] Error: {e}")
        return []


def _shap_fallback(model, X_row, feature_names):
    return [{"feature": fn, "value": float(X_row[0, i]), "shap_value": 0.0}
            for i, fn in enumerate(feature_names)]
