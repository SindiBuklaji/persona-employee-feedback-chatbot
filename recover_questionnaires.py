#!/usr/bin/env python3
"""
Questionnaire Recovery Script
Regenerates questionnaire responses from already-saved transcripts.

Context: generate_synthetic_data.py had a participant_id key mismatch bug that
caused synthetic_questionnaires.csv to be written with 0 data rows even though
73 sessions completed successfully. Transcripts and honesty codings were saved
correctly (keyed by the real backend participant_id), so we recover by re-running
only the questionnaire-generation LLM call against those saved transcripts.

Demographics could not be recovered (never persisted) and are freshly randomized.
"""

import json
import os
import glob
import logging

from generate_synthetic_data import (
    load_config,
    generate_questionnaire_response,
    generate_random_demographics,
)

logger = logging.getLogger("QuestionnaireRecovery")


def setup_logging(output_dir: str) -> logging.Logger:
    log_file = f"{output_dir}/recovery.log"
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S'
    ))
    logger.addHandler(ch)

    return logger


def find_model_config(config: dict, model_name: str) -> dict:
    for model in config["models"]:
        if model["display_name"] == model_name:
            return model
    raise ValueError(f"No model config found for display_name={model_name}")


def write_recovered_questionnaires_csv(rows: list, output_dir: str):
    import csv
    csv_path = f"{output_dir}/synthetic_questionnaires.csv"

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "participant_id",
            "condition",
            "model_name",
            "model_id",
            "perc_warmth_bipolar",
            "perc_task_focus_bipolar",
            "psych_safe_1",
            "psych_safe_2",
            "psych_safe_3",
            "psychological_safety_mean",
            "openness_1",
            "openness_2_raw",
            "self_reported_honesty_mean",
            "engagement_self_report",
            "ai_experience",
            "years_work_experience",
            "age",
            "gender",
            "industry",
            "job_role",
            "timestamp_submit",
        ])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    logger.info(f"[OK] Wrote {csv_path} ({len(rows)} rows)")


def main():
    import sys
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    config = load_config()
    output_dir = config["output"]["directory"]
    setup_logging(output_dir)

    logger.info("=" * 70)
    logger.info("Questionnaire Recovery (from saved transcripts)")
    logger.info("=" * 70)

    transcript_paths = sorted(glob.glob(f"{output_dir}/transcripts/*.json"))
    logger.info(f"[*] Found {len(transcript_paths)} transcripts")

    rows = []
    failed = []

    for idx, path in enumerate(transcript_paths, 1):
        with open(path) as f:
            transcript = json.load(f)

        participant_id = transcript["participant_id"]
        condition = transcript["condition"]
        model_name = transcript["model_name"]

        logger.info(f"[{idx:3d}/{len(transcript_paths)}] {model_name:15s} ({condition:10s}) | {participant_id[:12]}...")

        try:
            model_config = find_model_config(config, model_name)
        except ValueError as e:
            logger.warning(f"  [FAIL] {e}")
            failed.append(participant_id)
            continue

        api_key = os.getenv(model_config["api_key_env"])
        if not api_key:
            logger.warning(f"  [FAIL] Missing API key env var: {model_config['api_key_env']}")
            failed.append(participant_id)
            continue

        session_data = {
            "completed_task": True,
            "condition": condition,
            "transcript": transcript["transcript"],
        }

        q_response = generate_questionnaire_response(
            session_data,
            config,
            model_config["model_id"],
            model_config["provider"],
            api_key,
        )

        if not q_response:
            logger.warning(f"  [FAIL] Questionnaire generation failed")
            failed.append(participant_id)
            continue

        demographics = generate_random_demographics(config)

        rows.append({
            "participant_id": participant_id,
            "condition": condition,
            "model_name": model_name,
            "model_id": model_config["model_id"],
            "perc_warmth_bipolar": q_response.get("perc_warmth_bipolar", ""),
            "perc_task_focus_bipolar": q_response.get("perc_task_focus_bipolar", ""),
            "psych_safe_1": q_response.get("psych_safe_1", ""),
            "psych_safe_2": q_response.get("psych_safe_2", ""),
            "psych_safe_3": q_response.get("psych_safe_3", ""),
            "psychological_safety_mean": q_response.get("psychological_safety_mean", ""),
            "openness_1": q_response.get("openness_1", ""),
            "openness_2_raw": q_response.get("openness_2_raw", ""),
            "self_reported_honesty_mean": q_response.get("self_reported_honesty_mean", ""),
            "engagement_self_report": q_response.get("engagement_self_report", ""),
            "ai_experience": demographics["ai_experience"],
            "years_work_experience": demographics["years_work_experience"],
            "age": demographics["age"],
            "gender": demographics["gender"],
            "industry": demographics["industry"],
            "job_role": demographics["job_role"],
            "timestamp_submit": "",
        })

        engagement = q_response.get('engagement_self_report', '?')
        psych_safe = q_response.get('psychological_safety_mean', '?')
        logger.info(f"  [OK] H={engagement}, PS={psych_safe}")

    write_recovered_questionnaires_csv(rows, output_dir)

    logger.info("=" * 70)
    logger.info(f"[OK] RECOVERY COMPLETE: {len(rows)}/{len(transcript_paths)} recovered")
    if failed:
        logger.warning(f"Failed: {len(failed)} -> {failed}")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
