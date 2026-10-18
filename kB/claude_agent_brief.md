# Brief for the Claude encoder agents (kB)

Encoding agent (one fresh agent per encoding, 9 in total):
"Read /Users/mertayvazoglu/Life/career/applications/stanford-codex/pilot/kB/prompt_<role>.txt and do exactly what it
asks. Save the contents of your single python code block (the code only, without the backticks) to
/Users/mertayvazoglu/Life/career/applications/stanford-codex/pilot/kB/encodings_claude/<role>_<k>.py. Do not read
any other file in the pilot folder."

Adapter agent (one fresh agent per encoding, after the encoding exists):
"Read /Users/mertayvazoglu/Life/career/applications/stanford-codex/pilot/kB/adapter_template.txt. Replace {encoding}
with the contents of .../kB/encodings_claude/<role>_<k>.py and do exactly what the resulting prompt asks. Save the
code only to .../kB/encodings_claude/<role>_<k>_adapter.py. Do not read any other file in the pilot folder."
