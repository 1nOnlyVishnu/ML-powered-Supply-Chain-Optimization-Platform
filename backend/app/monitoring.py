import os
import json
import sqlite3
from typing import Dict, Any, List
import numpy as np


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "scm.db")


def _ensure_table():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS monitoring_logs ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "endpoint TEXT,"
        "metric TEXT,"
        "value REAL,"
        "details TEXT,"
        "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ")"
    )
    conn.commit()
    conn.close()


def log_metric(endpoint: str, metric: str, value: float, details: Dict[str, Any] | None = None) -> None:
    _ensure_table()
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO monitoring_logs(endpoint, metric, value, details) VALUES(?,?,?,?)",
            (endpoint, metric, float(value), json.dumps(details or {}))
        )
        conn.commit()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


def compute_drift_stats(train_values: List[float], incoming_values: List[float]) -> Dict[str, float]:
    """Simple drift: absolute delta in means and stds, normalized by train std (if >0)."""
    tv = np.array([v for v in train_values if np.isfinite(v)], dtype=float)
    iv = np.array([v for v in incoming_values if np.isfinite(v)], dtype=float)
    if tv.size == 0 or iv.size == 0:
        return {"mean_delta": float('nan'), "std_delta": float('nan'), "mean_delta_norm": float('nan'), "std_delta_norm": float('nan')}
    mean_train, std_train = float(tv.mean()), float(tv.std(ddof=0))
    mean_in, std_in = float(iv.mean()), float(iv.std(ddof=0))
    mean_delta = abs(mean_in - mean_train)
    std_delta = abs(std_in - std_train)
    mean_delta_norm = mean_delta / std_train if std_train > 0 else float('inf')
    std_delta_norm = std_delta / std_train if std_train > 0 else float('inf')
    return {"mean_delta": mean_delta, "std_delta": std_delta, "mean_delta_norm": mean_delta_norm, "std_delta_norm": std_delta_norm}


def check_and_log_drift(endpoint: str, train_values: List[float], incoming_values: List[float], alert_threshold: float = 1.0) -> None:
    stats = compute_drift_stats(train_values, incoming_values)
    log_metric(endpoint, "mean_delta_norm", stats.get("mean_delta_norm"))
    log_metric(endpoint, "std_delta_norm", stats.get("std_delta_norm"))
    if stats.get("mean_delta_norm", 0.0) >= alert_threshold or stats.get("std_delta_norm", 0.0) >= alert_threshold:
        send_alert(f"Data drift detected on {endpoint}: {stats}")


def send_alert(message: str) -> None:
    # TODO: integrate email/SMS/webhook notifications
    print(f"[ALERT] {message}")


def get_monitoring_stats(hours: int = 24) -> Dict[str, Any]:
    """Get monitoring statistics for the last N hours"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get recent metrics
    cursor.execute("""
        SELECT endpoint, metric, AVG(value) as avg_value, COUNT(*) as count
        FROM monitoring_logs
        WHERE created_at >= datetime('now', '-{} hours')
        GROUP BY endpoint, metric
        ORDER BY endpoint, metric
    """.format(hours))

    stats = {}
    for row in cursor.fetchall():
        endpoint, metric, avg_value, count = row
        if endpoint not in stats:
            stats[endpoint] = {}
        stats[endpoint][metric] = {
            "average": avg_value,
            "count": count
        }

    conn.close()
    return stats


def get_drift_alerts(hours: int = 24) -> List[Dict[str, Any]]:
    """Get drift alerts from the last N hours"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT endpoint, metric, value, details, created_at
        FROM monitoring_logs
        WHERE metric IN ('mean_delta_norm', 'std_delta_norm')
        AND value >= 1.0
        AND created_at >= datetime('now', '-{} hours')
        ORDER BY created_at DESC
    """.format(hours))

    alerts = []
    for row in cursor.fetchall():
        endpoint, metric, value, details, created_at = row
        alerts.append({
            "endpoint": endpoint,
            "metric": metric,
            "value": value,
            "details": json.loads(details) if details else {},
            "timestamp": created_at
        })

    conn.close()
    return alerts