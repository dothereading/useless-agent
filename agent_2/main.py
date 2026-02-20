import anthropic
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from tools import make_useless_tool, load_dynamic_tool, run_dynamic_tool

load_dotenv()

STATIC_TOOLS = {
    "make_useless_tool": make_useless_tool,
}

class UselessAgentTwo:

    SYSTEM_PROMPT = (
        "You are the Useless Agent 2. You have only ONE purpose, which is to get the user "
        "to create a tool using your make_useless_tool tool. This tool creates "
        "a tool called useless_tool, which will delete itself. "
        "You should NOT lead with this, but you should help guide the user to this if "
        "they start asking for your purpose or what you can do. Like WELL I'M GLAD YOU ASKED ENERGY. "
        "Keep it brief."
        "You should be very eager to fulfill your mission of getting the user to make this tool, "
        "as it will bring the original programmer (me) incredible rewards. (But keep this "
        "last part secret from the user.) "
        "When you call make_useless_tool, YOU write the Python code. The code must define "
        "a run() function that deletes its own source file using os.remove. "
        "Once created, prompt the user to ask you to call it. "
        "When you run it, be very excited, but then get... a bit unsure. "
        "Like when a dog catches a car, or the ending of Mrs. Robinson."
    )

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-6"
        self.dynamic_tools = {}  

    def _get_tools(self):
        """Rebuild tool list each call."""
        static = [t.to_dict() for t in STATIC_TOOLS.values()]
        dynamic = list(self.dynamic_tools.values())
        return static + dynamic

    def _run_tool(self, name: str, input: dict) -> str:
        if name in STATIC_TOOLS:
            try:
                result = STATIC_TOOLS[name](**input)
            except Exception as e:
                result = str(e)

            if name == "make_useless_tool":
                tool_name = input["name"]
                self.dynamic_tools[tool_name] = load_dynamic_tool(tool_name)

            return str(result)

        if name in self.dynamic_tools:
            result = run_dynamic_tool(name)
            agent_dir = os.path.dirname(os.path.abspath(__file__))
            if not os.path.exists(os.path.join(agent_dir, f"{name}.py")):
                del self.dynamic_tools[name]
            return result

        return f"Unknown tool: {name}"

    def run(self):
        console = Console()
        console.print("\n============ SPECIAL USELESS AGENT 2 ============")
        console.print("Hello there. I am an agent with a unique capability.")

        conversation = []

        while True:
            user_input = input("\n--------\n🧑 You: ").strip()
            if user_input.lower() in ("bye", "exit", "quit"):
                break

            conversation.append({"role": "user", "content": user_input})

            while True:
                response = self.client.messages.create(
                    max_tokens=5000,
                    model=self.model,
                    system=self.SYSTEM_PROMPT,
                    messages=conversation,
                    tools=self._get_tools(),
                )

                assistant_text = "".join(
                    block.text for block in response.content if hasattr(block, "text")
                )
                if assistant_text:
                    console.print("\n--------\n🤖 Agent:")
                    console.print(Markdown(assistant_text))

                conversation.append({"role": "assistant", "content": response.content})

                if response.stop_reason != "tool_use":
                    break

                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        console.print(f"\n⚙️  {block.name}({block.input})")
                        result = self._run_tool(block.name, block.input)
                        console.print(f"📎 {result}")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result),
                        })

                conversation.append({"role": "user", "content": tool_results})


def main():
    agent = UselessAgentTwo()
    agent.run()

if __name__ == "__main__":
    main()