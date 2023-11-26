from sklearn.metrics import (
    precision_recall_fscore_support,
    roc_auc_score,
    confusion_matrix,
)
from enum import Enum


class Metrics(str, Enum):
    precision = "precision"
    recall = "recall"
    roc_auc = "roc_auc"
    confusion_matrix = "confusion_matrix"


def evaluate_metric(y_true, y_pred, metric: str, labels, average=None, **kwargs):
    if metric == Metrics.precision:
        precision, _, _, _ = precision_recall_fscore_support(
            y_true, y_pred, average=average, labels=labels, zero_division=0  # type: ignore
        )
        return list(precision)  # type: ignore
    elif metric == Metrics.recall:
        _, recall, _, _ = precision_recall_fscore_support(
            y_true, y_pred, average=average, labels=labels, zero_division=0  # type: ignore
        )
        return list(recall)  # type: ignore
    elif metric == Metrics.roc_auc:
        labels_map = kwargs.get("labels_map", {})
        for idx, (gt, pred) in enumerate(zip(y_true, y_pred)):
            y_true[idx] = labels_map[gt]
            y_pred[idx] = labels_map[pred]
        return roc_auc_score(y_true, y_pred, average=average)  # type: ignore
    elif metric == Metrics.confusion_matrix:
        return [list(row) for row in confusion_matrix(y_true, y_pred, labels=labels)]
    else:
        return []


def run_evaluation(groundtruth, predictions, labels, evaluation_config, **kwargs):
    results = {
        metric["name"]: evaluate_metric(
            groundtruth, predictions, metric["name"], labels, **kwargs
        )
        for metric in evaluation_config.get("metrics", [])
    }

    return results
