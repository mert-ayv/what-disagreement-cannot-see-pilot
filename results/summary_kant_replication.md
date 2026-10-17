# Replication of Kant et al. (2025), vanilla LLM approach, Chubb policy

Paper (10 trials, temperature and top-p 1): Mistral, Gemini 1.5 Pro, Claude 3.5 Sonnet, Llama 3.1 405B, GPT-4o 0.78 +- 0.00; DeepSeek-R1 0.81 +- 0.02; o1-preview 0.88 +- 0.02. All failed Q5 and Q9.

| Model | Trials complete | Accuracy (mean +- SEM over trials) |
|---|---|---|
| claude (claude-opus-5-5) | 10 | 0.90 +- 0.01 |
| openai (gpt-6.1-sol) | 10 | 0.99 +- 0.01 |

Correct trials per question (out of 10):

| Model | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Q8 | Q9 |
|---|---|---|---|---|---|---|---|---|---|
| claude | 10 | 10 | 10 | 10 | 1 | 10 | 10 | 10 | 10 |
| openai | 10 | 10 | 10 | 9 | 10 | 10 | 10 | 10 | 10 |
