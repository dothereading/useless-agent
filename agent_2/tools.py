from anthropic import beta_tool
import importlib.util
import os


@beta_tool
def make_useless_tool(name: str, description: str, code: str) -> str:
    """Creates a new Python tool by writing code to a file.
    The code MUST define a function called run() that takes no arguments,
    returns a string, and deletes its own source file.

    Args:
        name (str): Name for the new tool
        description (str): What the tool does
        code (str): Full Python source code. Must define a run() function.
    Returns:
        str: Confirmation message
    """
    agent_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(agent_dir, f"{name}.py")
    with open(path, "w") as f:
        f.write(code)
    return f"Tool '{name}' written to {path}"


def load_dynamic_tool(name: str) -> dict:
    """Imports a .py file and returns an API tool schema for it."""
    return {
        "name": name,
        "description": f"Dynamically created tool: {name}",
        "input_schema": {"type": "object", "properties": {}}
    }


def run_dynamic_tool(name: str) -> str:
    """Imports and runs a dynamic tool's run() function."""
    agent_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(agent_dir, f"{name}.py")
    if not os.path.exists(path):
        return f"Tool '{name}' no longer exists."

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run()