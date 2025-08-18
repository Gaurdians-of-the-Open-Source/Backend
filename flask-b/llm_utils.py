import anthropic
import os

MODEL = 'claude-sonnet-4-20250514'
MAX_TOKENS = 2048

ANTHROPIC_API_KEY = os.environ['ANTHROPIC_API_KEY']
CLIENT = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_DEFAULT = (
    'Act as a senior security auditor. Output pure Markdown with a final "Instructions" section. '
    'For each issue: summary, risk, vulnerable snippet, fixed snippet.'
)

def generate_llm_md(issue_json_text, code_text, system=SYSTEM_DEFAULT):
    resp = CLIENT.messages.create(
        model=MODEL,
        system=system,
        messages=[{
            'role': 'user',
            'content': (
                '## JSON\n```json\n' + issue_json_text + '\n```\n\n'
                '## Source Code\n```text\n' + code_text + '\n```\n'
                '## Output Rules\nPure Markdown only; include "Instructions" at the end.'
            ),
        }],
        max_tokens=MAX_TOKENS,
        timeout = 30
    )

    parts = []
    for block in resp.content:
        text = getattr(block, 'text', None)
        if isinstance(text, str):
            parts.append(text)
    return "".join(parts).strip()
