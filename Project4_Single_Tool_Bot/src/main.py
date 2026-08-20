import argparse
import math
import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

TOOLS = [
    {
        "name": "calculator",
        "description": "Performs a math calculation: add, subtract, multiply, divide, power, or log. Use this instead of computing numeric answers yourself.",
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide", "power", "log"]},
                "a": {"type": "number", "description": "First number, or the value to take the log of."},
                "b": {"type": "number", "description": "Second number; for 'log' this is the base (defaults to 10 if omitted)."},
            },
            "required": ["operation", "a"],
        },
    }
]


def run_calculator(operation, a, b=None):
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            return "Error: division by zero"
        return a / b
    elif operation == "power":
        return a ** b
    elif operation == "log":
        return math.log(a, b if b is not None else 10)


def chat(user_message):
    first_response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        tools=TOOLS,
        messages=[{"role": "user", "content": user_message}],
    )
    print(f"[DEBUG] stop_reason: {first_response.stop_reason}") 
    if first_response.stop_reason != "tool_use":
        return "".join(block.text for block in first_response.content if block.type == "text")

    tool_use_block = next(block for block in first_response.content if block.type == "tool_use")
    result = run_calculator(**tool_use_block.input)


    second_response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        tools=TOOLS,
        messages=[
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": first_response.content},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_block.id,
                        "content": str(result),
                    }
                ],
            },
        ],
    )

    return "".join(block.text for block in second_response.content if block.type == "text")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ask a question; the bot can use a calculator tool.")
    parser.add_argument("question", help="The question to ask the bot.")
    args = parser.parse_args()

    print(chat(args.question))
