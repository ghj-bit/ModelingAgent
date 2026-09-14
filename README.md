# ModelingAgent: Bridging LLMs and Mathematical Modeling for Real-World Challenges
[**📊 Dataset**](https://github.com/qiancheng0/ModelingAgent/tree/main/data) | [**📖 Paper**](https://www.arxiv.org/pdf/2505.15068)

This repository contains the official code and dataset for the paper *"ModelingAgent: Bridging LLMs and Mathematical Modeling for Real-World Challenges."*

The data includes the ModelingBench dataset, featuring detailed question descriptions, requirements, and evaluation criteria.

![Pipeline](assets/pipeline.png)

## 🔍 Quick Start
First, install the required packages by running:
```bash
pip install -r requirements.txt
```

### Model and API Setup
Some models may require API keys to function correctly. Please add the appropriate keys to the configuration file located in each directory under `src`.

We use the Serper API as the backend to support our Search tool. Please include your Serper API key to use this feature ([**link**](https://serper.dev)).

```json
{
    "openai_key": "YOUR_OPENAI_API_KEY",
    "google_api_key": "YOUR_GOOGLE_API_KEY",
    "serper_key": "YOUR_SERPER_API_KEY"
}
```

If you are testing a self-hosted model, please use the script in the `src/host` directory. We currently support hosting models (and their tool-use functions) through `vllm`. The supported open-source model hosting scripts include: `Llama-3.1-70B-Instruct`, `Qwen-2.5-72B-Instruct`, and `QwQ-32B`.

### ModelingBench Data
Our ModelingBench data is located in the `data` directory. It can be freely used for various purposes. Each data point contains several fields. Here is an example:
```json
"2001_Adolescent_Pregnancy": {
    "year": "2001",
    "title": "Adolescent Pregnancy",
    "level": "High School",
    "source": "HiMCM",
    "link": "Problems/2001/HIMCM-A-2/index.html",
    "question": "You are working temporarily for the Department of Health ...",
    "requirements": [
        {
            "category": "Data Analysis", 
            "description": "Evaluate the accuracy and completeness of the data ..."
        }
    ],
    "eval_roles": [
        {
            "name": "Mathematician",
            "details": "You are a mathematician with expertise in ..."
        }
    ]
}
```

## 🧪 Experiments

### Testing Code
We provide testing code for Vanilla Generation in the `ModelBase` directory, Tool Agent in `ModelTool`, and ModelingAgent in `ModelAgent`. Please ensure the model configuration files are correctly set up with the required API keys and configurations.

Also, set the output directory and other paths properly in the respective entry point file you wish to run. You can then run the following:
```bash
cd ModelBase # For running Vanilla Generation
python baseline.py

cd src/ModelTool # For running Tool Agent
python baseline.py 2013_Bank_Service_Problem # Run one problem by ID
python baseline.py # Run all problems

cd ../.. # Run one Tool Agent problem and evaluate it end to end
python run_and_evaluate.py 2013_Bank_Service_Problem

cd ModelAgent # For running ModelingAgent
python mathmodel.py

# Run OpenClaw and evaluate only its final solution report
cd ../OpenClaw
python baseline.py 2013_Bank_Service_Problem
python baseline.py --all

# Render the benchmark-adapted prompt without calling OpenClaw or the judge
python baseline.py 2013_Bank_Service_Problem --prepare-only

# Evolve only the Required Workflow section for five scored rounds
python run_evolution.py --max_rounds 5 --problem_id 2013_Bank_Service_Problem

# Preview five prompt workflow rounds without running the benchmark or judge
python run_prompt_evolution.py --max_rounds 5

# Resume one specific evolution experiment
python run_evolution.py --max_rounds 5 \
  --problem_id 2013_Bank_Service_Problem \
  --exp ../../openclaw_experiments/run_YYYYMMDD_HHMMSS
```

The OpenClaw baseline requires a configured `openclaw` CLI. Each run is written
to `output_workspace_openclaw/<model>/<problem_id>_<timestamp>/`. OpenClaw must
write its final answer to `output/results/solution_report.md`; the runner copies
only that file into `final_submission/` and submits only that directory to
ModelingJudge. Judge results are written under `output_judge/OpenClaw/`.
After OpenClaw prints its agent-completion marker, the runner allows the CLI five
minutes to exit normally. If the completed CLI still does not exit, the runner
terminates that CLI process and continues with artifact checks and judging.
Sub-agent completion markers are ignored until a non-empty final report exists,
so an `AskExpert` sub-agent cannot prematurely trigger the CLI watchdog.
When resuming an evolution experiment, each unscored round is scanned for its
latest non-empty `output/results/solution_report.md`. An existing report skips
OpenClaw execution and proceeds directly through workflow checking, judging,
result recording, and then the next round.

OpenClaw workflow evolution permits only `AskExpert`, `ScEnsemble`, and
`Review`. Each round inserts one operator after one numbered step in
`## Required Workflow`; every other part of the parent prompt remains byte-for-byte
unchanged. The complete final report and its six-metric average score are used
to select and optimize the next round. Evolution artifacts are stored under
`openclaw_experiments/run_<timestamp>/`.

Identical operators may not be adjacent in an evolved workflow. Every inserted
operator declares a JSON evidence file under `output/logs/workflow_evidence/`.
After OpenClaw finishes and before judging starts, the runner validates the
operator order, evidence paths, JSON schemas, and required values, then writes
`meta/workflow_check.json`. A failed workflow check stops the run before Judge.

Please note that some errors may still exist due to the complexity of the agent structure. The model may not always use tools optimally or strictly follow instructions. Use this preview version with caution.

### Evaluation
We use the ModelingJudge framework to evaluate the final generated reports. The expert roles for each problem are included in the ModelingBench dataset.

To evaluate using ModelingJudge, run:
```bash
cd src/judger
python main_judge.py

# Evaluate one Tool Agent run
python main_judge.py 2013_Bank_Service_Problem --workspace ../../output_workspace_modeltool/deepseek-v4-flash/2013_Bank_Service_Problem_20260817_232902
```

Each evaluation metric corresponds to a Python file containing its specific prompt.

## 📖 File Structure
- Benchmark data is located in the `data` directory.
- Under `src/`, we include the code for our method and two baselines in `ModelAgent`, `ModelBase`, and `ModelTool`.
- The `judger` directory contains code, evaluation standards, and prompts for ModelingJudge.
- The `tools` directory contains all tools that may be invoked in the sandbox environment.

## 🖊️ Citation
```text
@article{qian2025modelingagent,
  title={ModelingAgent: Bridging LLMs and Mathematical Modeling for Real-World Challenges},
  author={Qian, Cheng and Du, Hongyi and Wang, Hongru and Chen, Xiusi and Zhang, Yuji and Sil, Avirup and Zhai, Chengxiang and McKeown, Kathleen and Ji, Heng},
  journal={arXiv preprint arXiv:2505.15068},
  year={2025}
}
```
