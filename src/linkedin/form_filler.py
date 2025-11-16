from utils.qna_manager import get_text_answer, get_select_answer
from .constants import timeout_1s, timeout_2s, timeout_5s


def fill_all_fields(page, input_fields, has_errors: bool = False):
    """Fills out all fields in the application form.

    If has_errors is True, only fields marked with an error are filled.
    """
    if has_errors:
        print("Filling only error fields... ")
        input_fields = [f for f in input_fields if f.get("hasError", False)]
    for input_field in input_fields:
        field_type = input_field["type"]
        if field_type == "text":
            enter_text_field(page, input_field)
        elif field_type in ["select", "radio"]:
            select_option(page, input_field)
        elif field_type == "combobox":
            fill_combobox(page, input_field)


def enter_text_field(page, input_field):
    """Enters text into a text field based on the provided input_field."""
    print("Filling text field:", input_field["label"])
    selector = input_field["selector"]
    current_value = input_field["value"]
    error = input_field.get("error", None)
    if error and not current_value:
        print(f"Field has error '{error}' but no current value. Skipping...")
        return
    new_value = get_text_answer(input_field["label"], error)
    if new_value and new_value != current_value:
        if current_value:
            page.fill(selector, "")
            page.wait_for_timeout(200)
        page.type(selector, new_value, delay=10)
        page.wait_for_timeout(timeout_1s)


def select_option(page, field_info):
    """Select an option for dropdown or radio group based on the provided field_info."""
    print("Selecting option for field:", field_info["label"])
    selector = field_info["selector"]
    options = field_info.get("options", [])
    label = field_info.get("label", "")
    current_value = field_info["value"]
    temp_options = [
        opt["label"] for opt in options if opt["label"].lower() != "select an option"
    ]
    answer = get_select_answer(label, temp_options)

    if current_value != answer:
        selected_option = next(
            (
                opt
                for opt in options
                if opt["label"].strip().lower() == answer.strip().lower()
            ),
            options[0] if options else None,
        )
        if not selected_option:
            print(f"No options available for field '{label}'")
            return
        print(f"Selecting option '{selected_option['label']}' for field '{label}'")
        select_control(
            page,
            selected_option["selector"],
            selector,
            selected_option.get("value"),
        )
        page.wait_for_timeout(timeout_1s)


def select_control(page, option_selector, field_selector, option_value=None):
    """Try multiple strategies to select an option (dropdown, radio, checkbox)."""
    if option_value is not None:
        try:
            page.select_option(field_selector, option_value, timeout=timeout_2s)
            print(f"select_option used for {field_selector} with value {option_value}")
            return
        except Exception as e:
            print(f"select_option failed for {field_selector}: {e}")
    # Try check (for radio/checkbox)
    try:
        page.check(option_selector, timeout=timeout_2s)
        print(f"Checked selector: {option_selector}")
        return
    except Exception as e:
        print(f"check failed for {option_selector}: {e}")
    # Try clicking the input
    try:
        page.click(option_selector, timeout=timeout_2s)
        print(f"Clicked selector: {option_selector}")
        return
    except Exception as e:
        print(f"click failed for {option_selector}: {e}")
    # Try clicking the label associated with the input
    try:
        label_selector = f'label[for="{option_selector.lstrip("#")}"]'
        page.click(label_selector, timeout=timeout_2s)
        print(f"Clicked label selector: {label_selector}")
        return
    except Exception as e:
        print(f"click label failed for {option_selector}: {e}")


def fill_combobox(page, field_info):
    """Fills out a combobox (autocomplete) field based on the provided field_info."""
    print("Filling combobox field:", field_info["label"])
    selector = field_info["selector"]
    label = field_info.get("label", "")
    current_value = field_info.get("value", "")
    new_value = get_text_answer(label)

    if current_value != new_value:
        try:
            page.fill(selector, "")
            page.type(selector, new_value, delay=50)
            page.wait_for_timeout(timeout_2s)
            option_query = '[role="option"]'
            page.wait_for_selector(option_query, timeout=timeout_5s)
            candidates = page.query_selector_all(option_query)
            if not candidates:
                print(f"No combobox candidates found for {label}")
                return
            candidates[0].click(timeout=timeout_2s)
            page.wait_for_timeout(1000)
        except Exception as e:
            print(f"Failed to select combobox option for {label}: {e}")
