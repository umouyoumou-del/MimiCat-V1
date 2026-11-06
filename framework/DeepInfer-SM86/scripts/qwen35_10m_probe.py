"""End-to-end 10M retrieval probe with DeepInfer-SM86 and Qwen3.5-4B.

DeepInfer-SM86 supplies the 10M hierarchical retrieval path: a persistent FTS5
index and a small retrieved evidence window.  Qwen3.5-4B is a hybrid
linear/full-attention architecture that the repository's native GGUF executor
does not implement yet, so this probe uses the already-verified llama.cpp
OpenAI-compatible server only for token generation.  The retrieval, evidence
selection, token accounting, and pass/fail check are DeepInfer code.

Example (PowerShell):

    python scripts/qwen35_10m_probe.py ^
      --index E:\DeepInfer-Qwen35\bench\needle10m\index.sqlite ^
      --question "What is the special magic number for needle 000?" ^
      --expected 6433012 ^
      --gguf E:\AI\Qwen3.5-4B\models\Qwen3.5-4B-Q4_K_M.gguf ^
      --llama-server F:\QwenQLoRA\llama.cpp\cpu\llama-server.exe ^
      --top-k 4 --max-tokens 32 --port 8099

The result is written as JSON with the retrieved chunk count, prompt tokens,
prefill/decode timings, and the exact answer check.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from deepinfer.retrieval.hybrid import retrieve


def health_ok(url: str, timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(url + "/health", timeout=timeout) as response:
            return response.status == 200
    except (OSError, urllib.error.URLError):
        return False


def wait_health(url: str, timeout: float) -> None:
    deadline = time.perf_counter() + timeout
    while time.perf_counter() < deadline:
        if health_ok(url):
            return
        time.sleep(1.0)
    raise RuntimeError(f"llama-server did not become healthy within {timeout:.0f}s: {url}")


def start_server(args) -> tuple[subprocess.Popen, object]:
    log_path = Path(args.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log = log_path.open("a", encoding="utf-8")
    command = [
        str(args.llama_server),
        "-m", str(args.gguf),
        "--host", "127.0.0.1",
        "--port", str(args.port),
        "-c", str(args.ctx_size),
        "-ngl", str(args.ngl),
        "--no-warmup",
        "-np", "1",
        "--jinja",
    ]
    process = subprocess.Popen(
        command,
        stdout=log,
        stderr=subprocess.STDOUT,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    try:
        wait_health(f"http://127.0.0.1:{args.port}", args.startup_timeout)
    except Exception:
        process.terminate()
        raise
    return process, log


def ask(args, prompt: str) -> tuple[dict, float]:
    body = {
        "model": "qwen3.5-4b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "top_p": 1,
        "max_tokens": args.max_tokens,
        "stream": False,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    request = urllib.request.Request(
        f"http://127.0.0.1:{args.port}/v1/chat/completions",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    began = time.perf_counter()
    with urllib.request.urlopen(request, timeout=args.request_timeout) as response:
        payload = json.load(response)
    return payload, time.perf_counter() - began


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--index", required=True, help="DeepInfer FTS5 index for the 10M document")
    parser.add_argument("--question", required=True)
    parser.add_argument("--expected", default="", help="substring that must appear in the answer")
    parser.add_argument("--gguf", required=True)
    parser.add_argument("--llama-server", type=Path,
                        default=Path(os.environ.get("LLAMA_SERVER", r"F:\QwenQLoRA\llama.cpp\cpu\llama-server.exe")))
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--max-tokens", type=int, default=32)
    parser.add_argument("--ctx-size", type=int, default=8192)
    parser.add_argument("--ngl", type=int, default=0)
    parser.add_argument("--port", type=int, default=8099)
    parser.add_argument("--startup-timeout", type=float, default=120.0)
    parser.add_argument("--request-timeout", type=float, default=600.0)
    parser.add_argument("--log", default=str(ROOT / "build" / "qwen35_10m_probe_server.log"))
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    if not Path(args.index).is_file():
        raise SystemExit(f"index not found: {args.index}")
    if not args.llama_server.is_file():
        raise SystemExit(f"llama-server not found: {args.llama_server}")

    con = sqlite3.connect(args.index)
    rows = retrieve(con, args.question, args.top_k)
    con.close()
    if not rows:
        raise SystemExit("DeepInfer retrieval returned no chunks")

    context = "\n\n".join(body for _, body in rows)
    prompt = (
        "You are a careful retrieval QA assistant. Use only the retrieved evidence below.\n"
        "The evidence comes from a 10,000,000-token document.\n\n"
        f"Question: {args.question}\n\n"
        f"Retrieved evidence:\n{context}\n\n"
        "Return exactly one line in the form `Answer: <number>`. Do not explain."
    )

    process = None
    log = None
    began = time.perf_counter()
    try:
        if not health_ok(f"http://127.0.0.1:{args.port}"):
            process, log = start_server(args)
        payload, request_seconds = ask(args, prompt)
    finally:
        if log is not None:
            log.close()
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
    elapsed = time.perf_counter() - began

    message = payload["choices"][0]["message"]
    answer = str(message.get("content") or "")
    usage = payload.get("usage", {})
    timings = payload.get("timings", {})
    passed = not args.expected or args.expected in answer
    result = {
        "mode": "DeepInfer-SM86 hierarchical retrieval + Qwen3.5-4B generation",
        "index": args.index,
        "question": args.question,
        "expected": args.expected,
        "answer": answer,
        "passed": passed,
        "retrieved_chunks": len(rows),
        "context_chars": len(context),
        "context_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "request_seconds": round(request_seconds, 2),
        "total_seconds_including_server_start": round(elapsed, 2),
        "prompt_tokens_per_second": timings.get("prompt_per_second"),
        "decode_tokens_per_second": timings.get("predicted_per_second"),
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text, flush=True)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text + "\n", encoding="utf-8")
        print(f"wrote {args.out}", flush=True)
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
