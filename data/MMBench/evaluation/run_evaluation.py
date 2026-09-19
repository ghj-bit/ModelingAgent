import os
import json
import re
import sys
import argparse
from dotenv import load_dotenv
from functools import partial
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from evaluation.model import gpt
from evaluation.utils import load_solution_json
from evaluation.prompts import generate_problem_analysis_prompt, generate_modeling_rigorousness_prompt, generate_practicality_and_scientificity_prompt, generate_result_and_bias_analysis_prompt

load_dotenv()

EXPECTED_ANALYSES_PER_DIMENSION = 2
DIMENSION_MAX_ATTEMPTS = 3
STRICT_OUTPUT_REMINDER = """
IMPORTANT OUTPUT REQUIREMENT:
Return exactly two evaluation items. Each item must contain one
<reason>...</reason> tag followed by one <score>INTEGER_FROM_1_TO_10</score>
tag. Keep each reason concise (at most 120 words), do not omit either item,
and do not wrap the tags in a code fence.
""".strip()

# parse the evalution result
def parse_and_save_evaluation_data(text):
    if not isinstance(text, str) or not text.strip():
        print("No matches found for reasons or scores!")
        return {}

    reason_pattern = r'<reason>\s*(.*?)\s*</reason>'
    score_pattern = r'<score>\s*(10|[1-9])(?:\.0+)?\s*(?:/\s*10)?\s*</score>'

    reasons = re.findall(reason_pattern, text, re.DOTALL | re.IGNORECASE)
    scores = re.findall(score_pattern, text, re.DOTALL | re.IGNORECASE)

    if not reasons or not scores:
        print("No matches found for reasons or scores!")
        return {}

    if len(reasons) != len(scores):
        print("Mismatch between number of reasons and scores!")
        return {}

    result_dict = {}
    for i, (reason, score) in enumerate(zip(reasons, scores), 1):
        result_dict[f"analysis_{i}"] = {
            "reason": reason.strip(),
            "score": int(score)
        }

    return result_dict


def _first_nonempty_response_text(response):
    """Normalize the native LLM wrapper's list response without unsafe [0]."""
    if isinstance(response, str):
        return response.strip()
    if isinstance(response, (list, tuple)):
        for item in response:
            if isinstance(item, str) and item.strip():
                return item.strip()
    return ""


def _is_complete_dimension(data):
    if not isinstance(data, dict) or len(data) != EXPECTED_ANALYSES_PER_DIMENSION:
        return False
    return all(
        isinstance(item, dict)
        and isinstance(item.get("score"), (int, float))
        and 1 <= item["score"] <= 10
        for item in data.values()
    )


def _evaluate_dimension(llm, prompt, dimension_name):
    """Retry only an empty or malformed MM-Bench evaluation dimension."""
    raw_attempts = []
    for attempt in range(1, DIMENSION_MAX_ATTEMPTS + 1):
        # Put the strict contract before the native rubric. Some reasoning
        # models otherwise produce several thousand tokens of prose and hit
        # max_tokens before emitting the second score.
        retry_prompt = STRICT_OUTPUT_REMINDER + "\n\n" + prompt

        raw_text = _first_nonempty_response_text(llm(retry_prompt))
        raw_attempts.append(
            f"=== {dimension_name} attempt {attempt}/{DIMENSION_MAX_ATTEMPTS} ===\n"
            + (raw_text or "[empty response]")
        )
        parsed = parse_and_save_evaluation_data(raw_text)
        if _is_complete_dimension(parsed):
            return "\n\n".join(raw_attempts), parsed

        if attempt < DIMENSION_MAX_ATTEMPTS:
            print(
                f"{dimension_name} attempt {attempt}/{DIMENSION_MAX_ATTEMPTS} "
                "returned an empty or incomplete result; retrying only this dimension...",
                flush=True,
            )

    print(
        f"{dimension_name} remained incomplete after "
        f"{DIMENSION_MAX_ATTEMPTS} attempts.",
        flush=True,
    )
    return "\n\n".join(raw_attempts), {}


def _load_existing_results(path):
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError) as error:
        print(f"Ignoring unreadable existing evaluation result: {error}")
        return {}


def _save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def evaluate_math_modeling(llm, solution_path):
    
    # get file name
    file_name = os.path.basename(solution_path).split('.')[0]

    # define evaluation result directory
    base_dir = os.path.dirname(solution_path)
    evaluation_dir = os.path.join(base_dir, "evaluation_result")
    if not os.path.exists(evaluation_dir):
        os.makedirs(evaluation_dir)
    if not os.path.exists(os.path.join(evaluation_dir, file_name)):
        os.makedirs(os.path.join(evaluation_dir, file_name))
    evaluation_dir = os.path.join(evaluation_dir, file_name)
    print(f"Evaluation directory created at: {evaluation_dir}")

    # define evaluation result path
    evaluation_results_txt_path = os.path.join(evaluation_dir, 'evaluation_results.txt')
    evaluation_results_json_path = os.path.join(evaluation_dir, 'evaluation_results.json')
    
    # load problem sultion
    solution_data = load_solution_json(solution_path)
    if not solution_data:
        print("Error: can not load the solution file.")
        return

    evaluation_specs = (
        ("analysis_evaluation", "problem analysis", generate_problem_analysis_prompt),
        (
            "modeling_rigorousness_evaluation",
            "modeling rigorousness",
            generate_modeling_rigorousness_prompt,
        ),
        (
            "practicality_and_scientificity_evaluation",
            "practicality and scientificity",
            generate_practicality_and_scientificity_prompt,
        ),
        (
            "result_and_bias_analysis_evaluation",
            "result and bias analysis",
            generate_result_and_bias_analysis_prompt,
        ),
    )

    # Resume a partially successful native evaluation. The OpenClaw wrapper may
    # retry this function, so completed dimensions must not be charged again.
    all_evaluation_data = _load_existing_results(evaluation_results_json_path)
    raw_sections = []
    for result_key, display_name, prompt_factory in evaluation_specs:
        if _is_complete_dimension(all_evaluation_data.get(result_key)):
            print(f"Reusing completed {display_name} evaluation.", flush=True)
            continue

        raw_text, parsed = _evaluate_dimension(
            llm,
            prompt_factory(solution_data),
            display_name,
        )
        all_evaluation_data[result_key] = parsed
        raw_sections.append(raw_text)
        # Persist each completed/failed dimension immediately so an outer retry
        # can continue from this checkpoint after interruption or API failure.
        _save_json(evaluation_results_json_path, all_evaluation_data)

    # Keep all four keys in the native result schema, including any dimension
    # that exhausted its own retries and remains incomplete.
    for result_key, _, _ in evaluation_specs:
        all_evaluation_data.setdefault(result_key, {})
    _save_json(evaluation_results_json_path, all_evaluation_data)

    print(f"The evaluation result is saved in {evaluation_results_json_path}.")

    # Preserve earlier raw responses when resuming and append only new calls.
    previous_raw = ""
    if os.path.isfile(evaluation_results_txt_path):
        with open(evaluation_results_txt_path, 'r', encoding='utf-8') as f:
            previous_raw = f.read().rstrip()
    all_evaluation_results = "\n\n".join(
        part for part in (previous_raw, *raw_sections) if part
    )

    # save the evaluation result
    with open(evaluation_results_txt_path, 'w', encoding='utf-8') as f:
        f.write(all_evaluation_results)

    print(f"The evaluation result is saved in {evaluation_results_txt_path}.")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--solution_file_path',
        type=str,
        default='MMBench/example_solution/example1.json'
    )

    parser.add_argument(
        '--base_url',
        type=str,
        default=os.getenv("DEEPSEEK_API_BASE") or os.getenv("BASE_URL") or "https://api.deepseek.com"
    )

    parser.add_argument(
        '--key',
        type=str,
        default=os.getenv("DEEPSEEK_API_KEY") or os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY") or ''
    )

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    llm =  partial(
        gpt,
        base_url=args.base_url,
        key=args.key,
        model=os.getenv("MODEL_NAME", "deepseek-v4-pro"),
        temperature=0.7,
        max_tokens=int(os.getenv("MMBENCH_JUDGE_MAX_TOKENS", "8192")),
    )
    solution_path = args.solution_file_path
    evaluate_math_modeling(llm,  solution_path)
