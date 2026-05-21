# Demo Recording

The best first GIF should show the zero-API-key demo. It proves llm-spy works without asking viewers to spend credits or paste secrets.

## What The GIF Should Show

1. Start the fake OpenAI-compatible provider.
2. Start `llm-spy`.
3. Run the demo client through `HTTP_PROXY`.
4. Show the Rich terminal call card.
5. Run `llm-spy history`.
6. Optionally open `llm-spy dashboard`.

Place the final GIF at:

```text
docs/assets/demo.gif
```

Then update the README placeholder to embed it.

## Manual Commands

Terminal 1:

```bash
python examples/fake_openai_provider.py
```

Terminal 2:

```bash
llm-spy start --port 8080
```

Terminal 3:

```bash
HTTP_PROXY=http://localhost:8080 python examples/openai_compatible_example.py
llm-spy history --last 1
llm-spy dashboard
```

## VHS

Install VHS from <https://github.com/charmbracelet/vhs>, then create `docs/demo.tape`:

```tape
Output docs/assets/demo.gif
Set FontSize 18
Set Width 1200
Set Height 760
Set Theme "Catppuccin Mocha"

Type "python examples/fake_openai_provider.py"
Enter
Sleep 1s
Ctrl+C

Type "llm-spy start --port 8080"
Enter
Sleep 1s
Ctrl+C

Type "HTTP_PROXY=http://localhost:8080 python examples/openai_compatible_example.py"
Enter
Sleep 1s
Type "llm-spy history --last 1"
Enter
Sleep 2s
```

The simple tape above records commands, but a polished demo usually needs a small shell script that starts the fake provider and proxy in the background, then cleans them up.

Example script:

```bash
#!/usr/bin/env bash
set -euo pipefail

TMP_HOME=$(mktemp -d)
python examples/fake_openai_provider.py &
FAKE_PID=$!
LLM_SPY_HOME=$TMP_HOME llm-spy start --port 8080 &
SPY_PID=$!
sleep 2
HTTP_PROXY=http://localhost:8080 LLM_SPY_HOME=$TMP_HOME python examples/openai_compatible_example.py
LLM_SPY_HOME=$TMP_HOME llm-spy history --last 1
kill $SPY_PID $FAKE_PID
```

## Terminalizer

```bash
npm install -g terminalizer
terminalizer record llm-spy-demo
terminalizer render llm-spy-demo -o docs/assets/demo.gif
```

Record the same zero-key flow. Keep the GIF under 30 seconds if possible.
