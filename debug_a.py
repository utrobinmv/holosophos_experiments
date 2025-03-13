import litellm
from smolagents import LiteLLMModel


messages = [
  {"role": "user", "content": [{"type": "text", "text": "Кто лучший в мире сапер?"}]}
]

litellm._turn_on_debug()

model = LiteLLMModel(model_id="litellm_proxy/arcee-ai-Arcee-Agent-AWQ-4bit-smashed", temperature=0.0)

a = model(messages)
print(a)
print("echo")