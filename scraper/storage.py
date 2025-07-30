def save_results(results, json_path: str | None = None, csv_path: str | None = None, output_dir: str | None = None, output_format: str = "json") -> None:
    """
    Save results to JSON or CSV file(s).

    Either provide explicit file paths via json_path and/or csv_path, or specify
    output_dir and output_format to write to output_dir/latest.json or latest.csv.

    :param results: List of dictionaries representing scraped items.
    :param json_path: Explicit path to write JSON data.
    :param csv_path: Explicit path to write CSV data.
    :param output_dir: Directory to write the output file (if specified).
    :param output_format: Format for output when using output_dir ('json' or 'csv').
    :return: None
    """
    # Determine output paths based on output_dir and output_format
    if output_dir:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        fmt = output_format.lower()
        if fmt == "json":
            json_path = str(out_dir / "latest.json")
        elif fmt == "csv":
            csv_path = str(out_dir / "latest.csv")
        else:
            raise ValueError("Invalid output_format; must be 'json' or 'csv'")

    # Write JSON if json_path is provided
    if json_path:
        path = Path(json_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    # Write CSV if csv_path is provided
    if csv_path:
        df = pd.DataFrame(results)
        csv_p = Path(csv_path)
        csv_p.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_p, index=False)
