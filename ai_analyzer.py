# ai_analyzer.py
import requests
import json
import logging
import time

logger = logging.getLogger(__name__)


def analyze_with_ollama_stream(error_log, host, model, stream=True, timeout=60, perf_logger=None):
    """
    Streams AI response from a remote Ollama server and prints it live to CLI.

    Logs:
      - time to connect
      - time to stream response
      - total analysis time
    """

    if not host:
        logger.error("Empty Ollama host provided.")
        raise ValueError("Empty Ollama host provided.")

    prompt = f"""You are an expert DevOps AI assistant.

Analyze the following Apache Tomcat log.
Identify the root cause clearly.
Include probable solutions.

Log:
{error_log}
"""

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": bool(stream),
    }

    url = host.rstrip("/") + "/api/generate"
    logger.info("Sending request to Ollama: %s (model=%s)", url, model)

    full_output = ""

    # -------------------------
    # 1) MEASURE CONNECT TIME
    # -------------------------
    connect_start = time.time()

    try:
        resp = requests.post(
            url,
            json=payload,
            stream=True,
        )

        connect_end = time.time()

        if perf_logger:
            perf_logger.info(
                f"Time to connect to Ollama: {connect_end - connect_start:.4f} sec"
            )

        if resp.status_code != 200:
            text = resp.text
            logger.error("Ollama returned status %s: %s", resp.status_code, text)
            print(f"\n❌ Ollama API error: {resp.status_code}")
            print(text)
            return ""

    except Exception as e:
        connect_end = time.time()
        if perf_logger:
            perf_logger.info(
                f"Time to connect to Ollama (FAILED): {connect_end - connect_start:.4f} sec"
            )
        logger.exception("Connection to Ollama FAILED: %s", e)
        print(f"\n❌ Connection error: {e}")
        return ""

    # -------------------------
    # 2) STREAM RESPONSE
    # -------------------------
    stream_start = time.time()

    try:
        for line in resp.iter_lines():
            if not line:
                continue

            try:
                chunk = json.loads(line.decode("utf-8"))
            except Exception:
                logger.debug("Failed to parse chunk: %s", line)
                continue

            token = chunk.get("response", "")
            if token:
                print(token, end="", flush=True)
                full_output += token

        stream_end = time.time()

        if perf_logger:
            perf_logger.info(
                f"Time to stream response: {stream_end - stream_start:.4f} sec"
            )
            perf_logger.info(
                f"Total analysis time: {stream_end - connect_start:.4f} sec"
            )

        print(f"\n\n⏱️ Total analysis time: {(stream_end - connect_start):.2f} seconds")
        print("✅ Streaming complete.\n")

        # -------------------------
        # LOG FULL AI RESPONSE
        # -------------------------
        logger.info("========== AI ANALYSIS START ==========")
        for line in full_output.splitlines():
            logger.info(line)
        logger.info("=========== AI ANALYSIS END ===========")

        return full_output


    except Exception as e:
        stream_end = time.time()
        if perf_logger:
            perf_logger.info(
                f"Time to stream response (FAILED): {stream_end - stream_start:.4f} sec"
            )
        logger.exception("Error during streaming: %s", e)
        print(f"\n❌ Unexpected error: {e}")
        return ""
