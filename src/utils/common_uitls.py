import json
import re

def minify_html(html):
    """
    Minifies the given HTML content by removing unnecessary whitespace, newlines, and spaces between tags.
    """
    # Remove newlines and tabs
    html = re.sub(r'[\n\r\t]+', '', html)
    # Remove spaces between tags
    html = re.sub(r'>\s+<', '><', html)
    # Remove multiple spaces
    html = re.sub(r'\s{2,}', ' ', html)
    return html.strip()

def minify_json(json):
    """
    Minifies the given JSON content by removing whitespace outside of string values.
    """
    try:
        obj = json.loads(json)
        return json.dumps(obj, separators=(',', ':'))
    except Exception as e:
        print("Error minifying JSON:", e)
        return json.strip()

def extract_valid_json(text):
    """
    Extracts and returns the first JSON array or object from a string,
    removing any surrounding markdown, explanations, or extra text.
    Returns the JSON string, or None if not found.
    """
    # Try to find a JSON code block
    match = re.search(r"```json\s*([\s\S]+?)\s*```", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Try to find the first [...] block (array) before {...} (object)
    match = re.search(r"(\[[\s\S]+\])", text)
    if match:
        return match.group(1).strip()
    match = re.search(r"({[\s\S]+})", text)
    if match:
        return match.group(1).strip()
    # Fallback: return the whole text (may fail if not valid JSON)
    return text.strip()

def transform_to_object(json_text):
    """
    Converts a JSON string to a Python object (dict or list).
    Handles both single objects and arrays.
    """
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return None

def test():
    text1 = '{"key1": "value1", "key2": "value2", "key3": [{"key4": "value4"}]}'
    obj1 = transform_to_object(text1)
    print("Transformed object1:", obj1)

    text2 = '[{"key1": "value1", "key2": "value2"}, {"key3": [{"key4": "value4"}]}]'
    obj2 = transform_to_object(text2)
    print("Transformed object2:", obj2)

    text3 = '[\n  {\n    "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094578-multipleChoice",\n    "type": "select",\n    "label": "Email address",\n    "options": [\n      {\n        "label": "Select an option",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094578-multipleChoice option[value=\'Select an option\']"\n      },\n      {\n        "label": "premranjandev@live.com",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094578-multipleChoice option[value=\'premranjandev@live.com\']"\n      },\n      {\n        "label": "premranjandev@gmail.com",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094578-multipleChoice option[value=\'premranjandev@gmail.com\']"\n      }\n    ]\n  },\n  {\n    "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country",\n    "type": "select",\n    "label": "Phone country code",\n    "options": [\n      {\n        "label": "Select an option",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Select an option\']"\n      },\n      {\n        "label": "Singapore (+65)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Singapore (+65)\']"\n      },\n      {\n        "label": "Afghanistan (+93)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Afghanistan (+93)\']"\n      },\n      {\n        "label": "Aland Islands (+358)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Aland Islands (+358)\']"\n      },\n      {\n        "label": "Albania (+355)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Albania (+355)\']"\n      },\n      {\n        "label": "Algeria (+213)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Algeria (+213)\']"\n      },\n      {\n        "label": "American Samoa (+1)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'American Samoa (+1)\']"\n      },\n      {\n        "label": "Andorra (+376)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Andorra (+376)\']"\n      },\n      {\n        "label": "Angola (+244)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Angola (+244)\']"\n      },\n      {\n        "label": "Anguilla (+1)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Anguilla (+1)\']"\n      }\n    ]\n  },\n  {\n    "selector": "#single-line-text-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-nationalNumber",\n    "type": "text",\n    "label": "Mobile phone number",\n    "options": []\n  }\n]'
    obj3 = transform_to_object(text3)
    print("Transformed object3:", obj3)

def test_extract_valid_json():
    text1 = '{"key1": "value1", "key2": "value2", "key3": [{"key4": "value4"}]}'
    json_text1 = extract_valid_json(text1)
    print("Transformed json_text1:", json_text1)

    text2 = '[{"key1": "value1", "key2": "value2"}, {"key3": [{"key4": "value4"}]}]'
    json_text2 = extract_valid_json(text2)
    print("Transformed json_text2:", json_text2)

    text3 = '[\n  {\n    "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094578-multipleChoice",\n    "type": "select",\n    "label": "Email address",\n    "options": [\n      {\n        "label": "Select an option",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094578-multipleChoice option[value=\'Select an option\']"\n      },\n      {\n        "label": "premranjandev@live.com",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094578-multipleChoice option[value=\'premranjandev@live.com\']"\n      },\n      {\n        "label": "premranjandev@gmail.com",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094578-multipleChoice option[value=\'premranjandev@gmail.com\']"\n      }\n    ]\n  },\n  {\n    "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country",\n    "type": "select",\n    "label": "Phone country code",\n    "options": [\n      {\n        "label": "Select an option",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Select an option\']"\n      },\n      {\n        "label": "Singapore (+65)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Singapore (+65)\']"\n      },\n      {\n        "label": "Afghanistan (+93)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Afghanistan (+93)\']"\n      },\n      {\n        "label": "Aland Islands (+358)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Aland Islands (+358)\']"\n      },\n      {\n        "label": "Albania (+355)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Albania (+355)\']"\n      },\n      {\n        "label": "Algeria (+213)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Algeria (+213)\']"\n      },\n      {\n        "label": "American Samoa (+1)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'American Samoa (+1)\']"\n      },\n      {\n        "label": "Andorra (+376)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Andorra (+376)\']"\n      },\n      {\n        "label": "Angola (+244)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Angola (+244)\']"\n      },\n      {\n        "label": "Anguilla (+1)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Anguilla (+1)\']"\n      }\n    ]\n  },\n  {\n    "selector": "#single-line-text-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-nationalNumber",\n    "type": "text",\n    "label": "Mobile phone number",\n    "options": []\n  }\n]'
    json_text3 = extract_valid_json(text3)
    print("Transformed json_text3:", json_text3)

# test_extract_valid_json()