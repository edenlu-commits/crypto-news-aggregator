import json
import pandas as pd
from pathlib import Path


def save_results(results, json_path: str, csv_path: str | None = None) -> None:
    """
    Save results to a JSON file and optionally a CSV file.

    :param results: List of dictionaries representing scraped items.
    :param json_path: File path to write JSON data.
    :param csv_path: Optional file path to write CSV data.
    """
    path = Path(json_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    if csv_path:
        df = pd.DataFrame(results)
        csv_p = Path(csv_path)
        csv_p.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_p, index=False)
