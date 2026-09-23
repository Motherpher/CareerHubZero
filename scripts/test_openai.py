#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from openai import OpenAI


def main() -> None:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        print("OPENAI_API_KEY is not available to this workflow.", file=sys.stderr)
        raise SystemExit(2)

    model = os.getenv("CAREERHUB_MODEL") or "gpt-5.6-sol"
    client = OpenAI(api_key=key)

    response = client.responses.create(
        model=model,
        store=False,
        input="Reply with exactly: CAREERHUBZERO_OK",
        max_output_tokens=32,
    )

    output = (response.output_text or "").strip()
    if "CAREERHUBZERO_OK" not in output:
        print(f"Unexpected OpenAI response: {output!r}", file=sys.stderr)
        raise SystemExit(3)

    print("CAREERHUBZERO_OK")
    print(f"Model: {model}")
    print("OpenAI Responses API connection is working.")


if __name__ == "__main__":
    main()
