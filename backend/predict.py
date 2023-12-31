import os

from transformers import pipeline
from typing import Optional, List


def _get_path_to_model() -> str:
    path = os.path.join(os.path.dirname(__file__), 'model')
    return path if os.path.isdir(path) else os.path.join(os.path.dirname(__file__), 'release', 'model')


def predict(text: str) -> Optional[List]:
    try:
        classifier = pipeline(
            "text-classification",
            model=_get_path_to_model(),
            tokenizer="distilbert-base-uncased",
            framework="pt",
            top_k=2
        )
    except OSError:
        classifier = None

    if classifier is not None:
        # split text to batches of 512 tokens
        batch_size = 512
        batches = [text[i:i + batch_size] for i in range(0, len(text), batch_size)]

        # predict
        predictions = {}
        for batch in batches:
            result = classifier(batch, padding=True)
            for res in result[0]:
                predictions[res['label']] = predictions.get(res['label'], 0) + res['score']

        best_predictions = sorted(predictions.items(), key=lambda item: item[1], reverse=True)
        best_predictions_list = []
        score = 0.
        for prediction in best_predictions:
            score += prediction[1]

        for prediction in best_predictions:
            best_predictions_list.append({'label': str(prediction[0]),
                                          'percent': f"{round((prediction[1] / score) * 100, 1)}%"})

        return best_predictions_list
    else:
        return None
