from utils.common_utils import transform_to_object
import json

def demo1():
    # Example text containing a JSON code block
    text = """
    Here is the user data you requested:
    ```json
    {
    "user": {
        "name": "Alice",
        "details": {
        "age": 30,
        "skills": ["Python", "AI"],
        "address": {"city": "NY", "zip": "10001"}
        }
    },
    "active": true
    }
    ```
    Thank you!
    """

    result = transform_to_object(text)
    print("Parsed Python object:", result)
    print("User's city:", result["user"]["details"]["address"]["city"])

def demo2():
    json_str = '{\n    "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094578-multipleChoice",\n    "type": "select",\n    "label": "Email address",\n    "options": [\n      {\n        "label": "Select an option",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094578-multipleChoice option[value=\'Select an option\']"\n      },\n      {\n        "label": "premranjandev@live.com",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094578-multipleChoice option[value=\'premranjandev@live.com\']"\n      },\n      {\n        "label": "premranjandev@gmail.com",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094578-multipleChoice option[value=\'premranjandev@gmail.com\']"\n      }\n    ]\n  },\n  {\n    "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country",\n    "type": "select",\n    "label": "Phone country code",\n    "options": [\n      {\n        "label": "Select an option",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Select an option\']"\n      },\n      {\n        "label": "Singapore (+65)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Singapore (+65)\']"\n      },\n      {\n        "label": "Afghanistan (+93)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Afghanistan (+93)\']"\n      },\n      {\n        "label": "Aland Islands (+358)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Aland Islands (+358)\']"\n      },\n      {\n        "label": "Albania (+355)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Albania (+355)\']"\n      },\n      {\n        "label": "Algeria (+213)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Algeria (+213)\']"\n      },\n      {\n        "label": "American Samoa (+1)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'American Samoa (+1)\']"\n      },\n      {\n        "label": "Andorra (+376)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Andorra (+376)\']"\n      },\n      {\n        "label": "Angola (+244)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Angola (+244)\']"\n      },\n      {\n        "label": "Anguilla (+1)",\n        "selector": "#text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-country option[value=\'Anguilla (+1)\']"\n      }\n    ]\n  },\n  {\n    "selector": "#single-line-text-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4243548803-20107094570-phoneNumber-nationalNumber",\n    "type": "text",\n    "label": "Mobile phone number",\n    "options": []\n  }'
    print(json_str)
    print(json.loads(json_str))


if __name__ == "__main__":
    demo2()