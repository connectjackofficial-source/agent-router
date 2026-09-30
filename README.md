# agent-router

> Route LLM calls to the cheapest model that can handle them. Simple prompts
> go to cheap models, complex ones to expensive ones.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#)

You're overpaying. A 5-word question doesn't need an opus-level model.
`agent-router` picks the cheapest tier based on prompt length.

## Usage

```python
from agent_router.router import route, estimate_cost

model = route("what time is it?")  # "haiku"
model = route("refactor this 300-line module with tests")  # "sonnet"
print(estimate_cost("write a long essay"))
# {'model': 'sonnet', 'input_words': 5, 'estimated_cost': 0.0003}
```

## Tiers

| Model | Cost / 1k tokens | Up to |
| --- | --- | --- |
| haiku | $0.00025 | 30 words |
| sonnet | $0.003 | 200 words |
| opus | $0.015 | 200+ words |

## License

MIT
