import typing as ty

from pydantic import BaseModel, RootModel

from ipyautoui.custom.edittsv import Changes
from ipyautoui.custom.edittsv_with_diff_and_key_mapping import (
    EditTsvWithDiffAndKeyMapping,
)


class ExampleModel(BaseModel):
    Id: int
    Site: ty.Optional[str] = None
    Meter: ty.Optional[str] = None
    reading: int
    nullable: ty.Optional[str] = None


class Example(RootModel):
    root: list[ExampleModel]


def _validate(widget: EditTsvWithDiffAndKeyMapping, data: list[dict]) -> list[dict]:
    """Run data through the widget's pydantic model for consistent structure."""
    return widget.model.model_validate(data).model_dump(mode="json", by_alias=True)


def _make_widget(initial_value: list[dict]) -> EditTsvWithDiffAndKeyMapping:
    widget = EditTsvWithDiffAndKeyMapping(
        value=initial_value,
        model=Example,
        primary_key_name="Id",
    )
    widget.unique_id_fields = ["Site", "Meter"]
    return widget


def test_bn_upload_text_builds_composite_key_maps():
    initial = [
        {"Id": 1, "Site": "A", "Meter": "001", "reading": 1, "nullable": None},
    ]
    updated = [
        {"Id": 1, "Site": "A", "Meter": "001", "reading": 2, "nullable": None},
        {"Id": 2, "Site": "B", "Meter": None, "reading": 3, "nullable": "x"},
    ]

    widget = _make_widget(initial)
    widget.prev_value = _validate(widget, initial)
    widget._value = _validate(widget, updated)

    widget._bn_upload_text(None)

    expected_prev = {
        "A-001": {
            "Id": 1,
            "Site": "A",
            "Meter": "001",
            "reading": 1,
            "nullable": "",
        }
    }
    expected_new = {
        "A-001": {
            "Id": 1,
            "Site": "A",
            "Meter": "001",
            "reading": 2,
            "nullable": "",
        },
        "B": {
            "Id": 2,
            "Site": "B",
            "Meter": "",
            "reading": 3,
            "nullable": "x",
        },
    }

    assert widget.ddiff.value == expected_prev
    assert widget.ddiff.new_value == expected_new
    assert widget.ddiff.diff is not None

    assert widget.bn_upload_text.layout.display == "None"
    assert widget.bn_confirmation.layout.display == ""
    assert widget.bn_cross.layout.display == ""
    assert widget.ddiff.layout.display == ""


def test_deepdiff_to_crud_handles_composite_keys():
    initial = [
        {"Id": 1, "Site": "A", "Meter": "001", "reading": 1, "nullable": None},
        {"Id": 3, "Site": "C", "Meter": "009", "reading": 4, "nullable": None},
    ]
    updated = [
        {"Id": 1, "Site": "A", "Meter": "001", "reading": 2, "nullable": None},
        {"Id": 2, "Site": "B", "Meter": None, "reading": 3, "nullable": "x"},
    ]

    widget = _make_widget(initial)
    widget.prev_value = _validate(widget, initial)
    widget._value = _validate(widget, updated)

    widget._bn_upload_text(None)
    changes = widget.deepdiff_to_crud(widget.ddiff.diff)

    assert changes.deletions == ["C-009"]
    assert changes.additions == [
        {"Id": 2, "Site": "B", "Meter": "", "reading": 3, "nullable": "x"}
    ]
    assert changes.edits == {"A-001": {"reading": 2}}


def test_resolve_composite_keys_to_real_ids():
    widget = _make_widget(
        [{"Id": 1, "Site": "A", "Meter": "001", "reading": 1, "nullable": None}]
    )

    dataset = [
        {"Id": 101, "Site": "A", "Meter": "001"},
        {"Id": 102, "Site": "B", "Meter": None},
        {"Id": 103, "Site": None, "Meter": None},
    ]
    mapping = widget._build_composite_key_to_id_map(dataset)

    assert mapping == {"A-001": 101, "B": 102}
    assert widget._composite_key_for_id(101, mapping) == "A-001"
    assert widget._composite_key_for_id("102", mapping) == "B"
    assert widget._composite_key_for_id("invalid", mapping) == ""

    raw_changes = Changes(
        deletions=["A-001", "missing"],
        edits={"A-001": {"reading": 9}, "missing": {"reading": 5}},
        additions=[{"Id": 200, "Site": "X"}],
    )

    resolved = widget._resolve_composite_to_ids(raw_changes, mapping)

    assert resolved.deletions == [101]
    assert resolved.edits == {101: {"reading": 9}}
    assert resolved.additions == [{"Id": 200, "Site": "X"}]
