# Three-valued comparison with the expert (unguided encodings)

Scope facts without an expert counterpart are treated as unknown: an encoding's answer is 'undetermined' when it changes with them. Nothing is assumed about them.

| Encoding | Agrees with expert | Undetermined, expert covers | Undetermined, expert denies | Decides differently | of which: grants what expert denies | denies what expert covers |
|---|---|---|---|---|---|---|
| unguided/claude_0 | 865686 (95.4%) | 26428 (2.9%) | 15086 (1.7%) | 0 (0.0%) | 0 | 0 |
| unguided/claude_1 | 865686 (95.4%) | 26428 (2.9%) | 15086 (1.7%) | 0 (0.0%) | 0 | 0 |
| unguided/gemini_1 | 857806 (94.6%) | 26428 (2.9%) | 22966 (2.5%) | 0 (0.0%) | 0 | 0 |
| unguided/openai_0 | 865686 (95.4%) | 26428 (2.9%) | 15086 (1.7%) | 0 (0.0%) | 0 | 0 |
| unguided/openai_1 | 865686 (95.4%) | 26428 (2.9%) | 15086 (1.7%) | 0 (0.0%) | 0 | 0 |
| unguided2/claude_0 | 858580 (94.6%) | 25672 (2.8%) | 22192 (2.4%) | 756 (0.1%) | 0 | 756 |
| unguided2/claude_1 | 858580 (94.6%) | 25672 (2.8%) | 22192 (2.4%) | 756 (0.1%) | 0 | 756 |
| unguided2/claude_2 | 859108 (94.7%) | 25672 (2.8%) | 21664 (2.4%) | 756 (0.1%) | 0 | 756 |
| unguided2/claude_3 | 859108 (94.7%) | 25672 (2.8%) | 21664 (2.4%) | 756 (0.1%) | 0 | 756 |
| unguided2/claude_4 | 875860 (96.5%) | 25672 (2.8%) | 4912 (0.5%) | 756 (0.1%) | 0 | 756 |
| unguided2/openai_0 | 858580 (94.6%) | 25672 (2.8%) | 22192 (2.4%) | 756 (0.1%) | 0 | 756 |
| unguided2/openai_1 | 862436 (95.1%) | 25756 (2.8%) | 18336 (2.0%) | 672 (0.1%) | 0 | 672 |
| unguided2/openai_2 | 880772 (97.1%) | 0 (0.0%) | 0 (0.0%) | 26428 (2.9%) | 0 | 26428 |
| unguided2/openai_3 | 880772 (97.1%) | 0 (0.0%) | 0 (0.0%) | 26428 (2.9%) | 0 | 26428 |
| unguided2/openai_4 | 858580 (94.6%) | 25672 (2.8%) | 22192 (2.4%) | 756 (0.1%) | 0 | 756 |

## Where the decided cases differ from the expert

- **unguided2/claude_0:** other: female with male partner (denies) [756]
- **unguided2/claude_1:** other: female with male partner (denies) [756]
- **unguided2/claude_2:** other: female with male partner (denies) [756]
- **unguided2/claude_3:** other: female with male partner (denies) [756]
- **unguided2/claude_4:** other: female with male partner (denies) [756]
- **unguided2/openai_0:** other: female with male partner (denies) [756]
- **unguided2/openai_1:** two identical FSH tests (denies) [672]
- **unguided2/openai_2:** other: male with female partner (denies) [9408]; other: female with female partner (denies) [8592]; other: female with no_partner partner (denies) [4296]; other: female with male partner (denies) [3460]; two identical FSH tests (denies) [672]
- **unguided2/openai_3:** other: male with female partner (denies) [9408]; other: female with female partner (denies) [8592]; other: female with no_partner partner (denies) [4296]; other: female with male partner (denies) [3460]; two identical FSH tests (denies) [672]
- **unguided2/openai_4:** other: female with male partner (denies) [756]
