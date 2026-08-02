import pytest
import yaml

from scripts.prepare_sports_contribution import REPOSITORY, prepare_contribution


def test_contribution_pins_source_without_registry_artifact(tmp_path):
    output = prepare_contribution("a" * 40, tmp_path)

    template = yaml.safe_load((output / "template.yaml").read_text())
    assert template["spec"]["source"]["repository"] == REPOSITORY
    assert template["spec"]["source"]["commit"] == "a" * 40
    assert template["spec"]["build"]["dockerfile"].endswith("/Dockerfile")
    assert "artifact" not in template["spec"]


def test_contribution_rejects_placeholder_source_identity(tmp_path):
    with pytest.raises(ValueError, match="placeholder SHA"):
        prepare_contribution("0" * 40, tmp_path)
