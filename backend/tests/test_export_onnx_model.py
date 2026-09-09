import pytest

from backend.scripts.export_onnx_model import validate_export_artifacts


def test_validate_export_artifacts_accepts_required_files(tmp_path):
    (tmp_path / "model.onnx").write_bytes(b"onnx")
    (tmp_path / "tokenizer.json").write_text("{}", encoding="utf-8")

    validate_export_artifacts(tmp_path)


def test_validate_export_artifacts_reports_missing_files(tmp_path):
    (tmp_path / "model.onnx").write_bytes(b"onnx")

    with pytest.raises(RuntimeError, match="tokenizer.json"):
        validate_export_artifacts(tmp_path)
