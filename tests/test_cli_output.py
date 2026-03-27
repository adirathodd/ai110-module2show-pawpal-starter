from cli_output import (
    format_priority,
    format_section_heading,
    format_status,
    format_title,
    render_kv_summary,
    render_table,
)


def test_format_priority_returns_plain_uppercase_label_when_color_disabled() -> None:
    assert format_priority("high", use_color=False) == "HIGH"


def test_format_status_returns_plain_pending_label_when_color_disabled() -> None:
    assert format_status(False, use_color=False) == "PENDING"


def test_format_title_prefixes_category_emoji() -> None:
    assert format_title("Breakfast", "feeding") == "🥣 Breakfast"


def test_render_table_includes_headers_and_row_content() -> None:
    table = render_table(["Pet", "Task"], [["Mochi", "Morning walk"]], use_color=False)

    assert "Pet" in table
    assert "Task" in table
    assert "Mochi" in table
    assert "Morning walk" in table


def test_render_kv_summary_includes_labels_when_color_disabled() -> None:
    summary = render_kv_summary([("Owner", "Jordan"), ("Pets", "Mochi, Luna")], use_color=False)

    assert "Owner:" in summary
    assert "Jordan" in summary
    assert "Pets:" in summary


def test_format_section_heading_returns_plain_heading_when_color_disabled() -> None:
    assert format_section_heading("Today's Schedule", icon="🗓️", use_color=False) == "🗓️ Today's Schedule"
