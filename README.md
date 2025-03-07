# Holosophos

Tools and agents for autonomous research.

## Install

Dependencies:
```
python3 -m pip install -r requirements.txt
```

Tokens in .env:
```
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
OPENROUTER_API_KEY=...
VAST_AI_KEY=...
```

Loging in HF:
```
huggingface-cli login
```


## Run

```
python3 -m holosophos.main_agent --query "..." --model-name "anthropic/claude-3-5-sonnet-20241022"
```
