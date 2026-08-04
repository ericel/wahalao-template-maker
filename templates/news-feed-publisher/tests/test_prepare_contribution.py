import yaml

from scripts.prepare_contribution import prepare_contribution


def test_generic_export_selects_news_recipe_and_pins_commit(tmp_path):
    output = prepare_contribution(
        "news-feed-publisher",
        "c" * 40,
        tmp_path,
    )

    template = yaml.safe_load((output / "template.yaml").read_text())
    assert output.name == "1.0.0"
    assert template["metadata"]["name"] == "news-feed-publisher"
    assert template["metadata"]["submission_id"].startswith("atsub_")
    assert template["spec"]["source"]["commit"] == "c" * 40
    assert "artifact" not in template["spec"]
