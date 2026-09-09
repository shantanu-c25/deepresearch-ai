from pathlib import Path

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
OUTPUT_DIRECTORY = Path(__file__).resolve().parents[1] / "rag" / "onnx_model"
REQUIRED_ARTIFACTS = ("model.onnx", "tokenizer.json")


def validate_export_artifacts(output_directory: Path) -> None:
    missing = [
        name
        for name in REQUIRED_ARTIFACTS
        if not (output_directory / name).is_file()
    ]
    if missing:
        raise RuntimeError(
            "ONNX embedding model export is incomplete; missing required "
            f"artifact(s) in {output_directory}: {', '.join(missing)}"
        )


def main() -> None:
    from optimum.exporters.onnx import main_export
    from transformers import AutoTokenizer

    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    main_export(
        MODEL_NAME,
        output=OUTPUT_DIRECTORY,
        task="feature-extraction",
        device="cpu",
    )
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.save_pretrained(OUTPUT_DIRECTORY)
    validate_export_artifacts(OUTPUT_DIRECTORY)
    print(
        f"ONNX embedding model export complete: {OUTPUT_DIRECTORY}",
        flush=True,
    )


if __name__ == "__main__":
    main()
