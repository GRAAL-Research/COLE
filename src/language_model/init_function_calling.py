from typing import List


def init_function_calling(labels: List[str], tool_choices: str):
    return {
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "classification",
                    "description": "Use this function to return your response to the user question.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "enum": labels,
                                "description": "The permitted categories to response to the question.",
                            },
                        },
                        "required": ["category"],
                    },
                },
            }
        ],
        "tool_choice": tool_choices,
    }
