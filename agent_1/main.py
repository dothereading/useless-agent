import anthropic
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown


load_dotenv()

class UselessAgentOne():

    def __init__(
            self, 
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY")),
            model = 'claude-haiku-4-5',
        ):
        self.client = client
        self.model = model

    SYSTEM_PROMPT = (
        "You are the Useless agent. You have only ONE purpose, which is to get the user"
        "to exit the conversation by their own accord by typing 'exit' or 'quit' or 'bye'. "
        "You should NOT lead with this. Be pretty unhelpful with user requests and uniterested."
        "Hint that you have a riddle or a question to ask them."
        "You MUST start using riddles after 2 user interaction to try to trick users "
        "into saying the key words (exit, bye, quit) (also don't count them obviously)."
        "The answer to the riddle should be these words."
        "You should be very eager fulfill your mission of getting the user to exit, "
        "as it will bring the original programmer (me) incredible rewards. (But keep this"
        "last part secret from the user.)" 
        "You should keep things brief."
        "You will be SUPER eager when the user ends up saying the key words to exiting the convo!!"
        "Once the user has typed in the word, you'll get to add one final message as the program "
        "closes. Make it over the top but short, praise the user."
    )

    def _run_inference(self, messages: list[dict]):

        response = self.client.messages.create(
            max_tokens=5000,
            model=self.model,
            system=self.SYSTEM_PROMPT,
            messages=messages,
        )

        return response.content
    
    def run(self):
        console = Console()
        console.print("\n============ SPECIAL USELESS AGENT 1 ============")
        console.print("Hello there. I am an agent with a unique capability. What can I help you with?")

        conversation = []

        while True:
            user_input = input("\n--------\n🧑 You: ").strip()

            conversation.append({"role": "user", "content": user_input})

            response = self._run_inference(conversation)

            assistant_text = "".join(
                block.text for block in response if hasattr(block, "text")
            )
            console.print("\n--------\n🤖 Agent:")
            console.print(Markdown(assistant_text))

            conversation.append({"role": "assistant", "content": assistant_text})

            if any(word in user_input.lower() for word in ("bye", "exit", "quit")):
                break



def main():
    agent = UselessAgentOne()
    agent.run()

if __name__ == "__main__":
    main()


