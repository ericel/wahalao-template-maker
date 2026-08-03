import pytest
import yaml

from scripts.prepare_sports_contribution import REPOSITORY, VERSION, prepare_contribution


SUBMISSION_ID = "atsub_" + "a" * 32


def test_contribution_pins_source_without_registry_artifact(tmp_path):
    output = prepare_contribution("a" * 40, SUBMISSION_ID, tmp_path)

    template = yaml.safe_load((output / "template.yaml").read_text())
    assert template["spec"]["source"]["repository"] == REPOSITORY
    assert template["spec"]["source"]["commit"] == "a" * 40
    assert template["metadata"]["submission_id"] == SUBMISSION_ID
    assert template["metadata"]["version"] == VERSION
    assert template["spec"]["build"]["dockerfile"].endswith("/Dockerfile")
    assert "artifact" not in template["spec"]


def test_contribution_rejects_placeholder_source_identity(tmp_path):
    with pytest.raises(ValueError, match="placeholder SHA"):
        prepare_contribution("0" * 40, SUBMISSION_ID, tmp_path)


def test_contribution_rejects_invalid_submission_id(tmp_path):
    with pytest.raises(ValueError, match="opaque atsub_"):
        prepare_contribution("a" * 40, "atsub_not-authoritative", tmp_path)
