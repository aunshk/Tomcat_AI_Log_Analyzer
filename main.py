#!/usr/bin/env python3

import argparse
import yaml
import time
import logging

from logging.handlers import RotatingFileHandler
from pathlib import Path

from log_parser import extract_error_blocks
from ai_analyzer import analyze_with_ollama_stream


CONFIG_FILE = "config.yaml"


# ------------------------------
#  Logging setup
# ------------------------------
def setup_logging(log_dir, log_file, level_str="INFO"):
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    level = getattr(logging, level_str.upper(), logging.INFO)

    log_path = Path(log_dir) / log_file

    logger = logging.getLogger()
    logger.setLevel(level)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    ch.setFormatter(ch_formatter)

    # Rotating file handler
    fh = RotatingFileHandler(str(log_path), maxBytes=5 * 1024 * 1024, backupCount=3)
    fh.setLevel(logging.DEBUG)
    fh_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    fh.setFormatter(fh_formatter)

    logger.handlers = [ch, fh]
    logging.info("Main logging initialized: %s", str(log_path))


def setup_performance_logger(log_dir):
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    perf_log_path = Path(log_dir) / "performance.log"

    perf_logger = logging.getLogger("performance")
    perf_logger.setLevel(logging.INFO)

    fh = RotatingFileHandler(str(perf_log_path), maxBytes=2 * 1024 * 1024, backupCount=2)
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    fh.setFormatter(formatter)

    if not perf_logger.handlers:
        perf_logger.addHandler(fh)

    return perf_logger


# ------------------------------
#  Load config
# ------------------------------
def load_config(path):
    if not Path(path).is_file():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)


# ------------------------------
#  MAIN
# ------------------------------
def main():
    parser = argparse.ArgumentParser(description="Tomcat Log Analyzer (Streaming)")
    parser.add_argument("logfile", help="Path to catalina.out")
    parser.add_argument("--config", "-c", default=CONFIG_FILE, help="Path to config.yaml")
    args = parser.parse_args()

    cfg = load_config(args.config)

    # Setup logging
    log_dir = cfg.get("log_dir", "./logs")
    log_file = cfg.get("log_file", "analyzer.log")
    log_level = cfg.get("log_level", "INFO")
    setup_logging(log_dir, log_file, log_level)

    perf_logger = setup_performance_logger(log_dir)

    # Phase 1: Load file
    t0 = time.time()
    with open(args.logfile, "r", encoding="utf-8", errors="ignore") as fh:
        raw_log = fh.read()
    t1 = time.time()
    perf_logger.info(f"Time to load log file: {t1 - t0:.4f} sec")

    # Phase 2: Parse log
    t2 = time.time()
    error_log = extract_error_blocks(raw_log, max_lines=cfg.get("max_error_lines", 300))
    t3 = time.time()
    perf_logger.info(f"Time to parse log: {t3 - t2:.4f} sec")

    if not error_log.strip():
        print("No relevant errors found.")
        return

    print("\n🔍 Extracted Error Log Preview:\n")
    print(error_log[:1000] + "...\n")

    print("🤖 Analyzing with remote Ollama (streaming)...\n")

    summary = analyze_with_ollama_stream(
        error_log,
        host=cfg["ollama_host"],
        model=cfg.get("model", "mistral"),
        perf_logger=perf_logger
    )

    if summary:
        print("\n🧠 Final Summary:\n")
        print(summary)
    else:
        print("\n❌ No summary returned. Check logs.")


if __name__ == "__main__":
    main()
