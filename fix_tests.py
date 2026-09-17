import re

with open("backend/tests/test_ai.py", "r") as f:
    content = f.read()

# Replace model_grounded with grounding_status
content = content.replace("model_grounded is False", "grounding_status == 'CONTRADICTORY_CLAIM'")
content = content.replace("model_grounded is True", "grounding_status != 'CONTRADICTORY_CLAIM'")
content = content.replace("model_grounded", "grounding_status")
content = content.replace('body["grounded"] is True', 'body["grounding_status"] != "CONTRADICTORY_CLAIM"')
content = content.replace('body["grounded"] is False', 'body["grounding_status"] == "CONTRADICTORY_CLAIM"')
content = content.replace('"grounded": true', '"grounding_status": "TRADITIONAL_INTERPRETATION"')

with open("backend/tests/test_ai.py", "w") as f:
    f.write(content)

with open("backend/tests/test_cache.py", "r") as f:
    content = f.read()
content = content.replace("model_grounded is False", "grounding_status == 'CONTRADICTORY_CLAIM'")
content = content.replace("model_grounded is True", "grounding_status != 'CONTRADICTORY_CLAIM'")
content = content.replace("model_grounded", "grounding_status")
with open("backend/tests/test_cache.py", "w") as f:
    f.write(content)

with open("backend/tests/test_tarot.py", "r") as f:
    content = f.read()
content = content.replace("not result.model_grounded", "result.grounding_status == 'CONTRADICTORY_CLAIM'")
content = content.replace("result.model_grounded", "result.grounding_status != 'CONTRADICTORY_CLAIM'")
with open("backend/tests/test_tarot.py", "w") as f:
    f.write(content)
