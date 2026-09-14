"""Create reproducible primary-domain statistics for ModelingBench tasks."""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = REPO_ROOT / "data" / "modeling_data_final.json"

CATEGORY_ORDER = [
    "Environmental, ecological, energy and sustainability",
    "Operations, transport and logistics",
    "Engineering, physical systems and design",
    "Health, population and social systems",
    "Governance, security and information systems",
    "Economics, finance and business decisions",
    "Games and combinatorial design",
]

# Each task is assigned one primary application domain. Mixed tasks are placed
# by their central modeled system or decision rather than their auxiliary tools.
CATEGORY_BY_TASK = {
    "2001_Adolescent_Pregnancy": "Health, population and social systems",
    "2001_Design_of_an": "Operations, transport and logistics",
    "2001_Forest_Service": "Environmental, ecological, energy and sustainability",
    "2001_Skyscrapers": "Engineering, physical systems and design",
    "2001_The_Bicycle_Wheel": "Engineering, physical systems and design",
    "2002_Airline_Overbooking": "Operations, transport and logistics",
    "2002_School_Busing": "Operations, transport and logistics",
    "2002_Wind_and_Waterspray": "Engineering, physical systems and design",
    "2003_Aviation_Baggage_Screening": "Operations, transport and logistics",
    "2003_Gamma_Knife_Treatment": "Health, population and social systems",
    "2003_The_Stunt_Person": "Engineering, physical systems and design",
    "2004_Motel_Cleaning_Problem": "Operations, transport and logistics",
    "2004_To_Be_Secure": "Governance, security and information systems",
    "2005_Flood_Planning": "Environmental, ecological, energy and sustainability",
    "2005_Nonrenewable_Resources": "Environmental, ecological, energy and sustainability",
    "2006_A_South_Sea": "Engineering, physical systems and design",
    "2006_Inflation_of_the": "Engineering, physical systems and design",
    "2006_Positioning_and_Moving": "Environmental, ecological, energy and sustainability",
    "2006_Wheel_Chair_Access": "Operations, transport and logistics",
    "2007_Gerrymandering": "Governance, security and information systems",
    "2007_Organ_Transplant:_The": "Health, population and social systems",
    "2007_The_Airplane_Seating": "Operations, transport and logistics",
    "2008_Creating_Sudoku_Puzzles": "Games and combinatorial design",
    "2008_Going_Green": "Environmental, ecological, energy and sustainability",
    "2009_Designing_a_Traffic": "Operations, transport and logistics",
    "2010_Curbing_City_Violence": "Health, population and social systems",
    "2010_The_Sweet_Spot": "Engineering, physical systems and design",
    "2011_How_environmentally_and": "Environmental, ecological, energy and sustainability",
    "2011_Repeater_Coordination": "Engineering, physical systems and design",
    "2011_Snowboard_Course": "Engineering, physical systems and design",
    "2011_Space_Shuttle_Problem:": "Operations, transport and logistics",
    "2012_Camping_along_the": "Environmental, ecological, energy and sustainability",
    "2013_Bank_Service_Problem": "Operations, transport and logistics",
    "2013_The_Ultimate_Brownie": "Engineering, physical systems and design",
    "2014_The_Next_Plague?": "Health, population and social systems",
    "2015_Is_it_sustainable?": "Environmental, ecological, energy and sustainability",
    "2016_Are_we_heading": "Environmental, ecological, energy and sustainability",
    "2016_Measuring_the_Evolution": "Governance, security and information systems",
    "2016_Modeling_Refugee_Immigration": "Health, population and social systems",
    "2016_Record_Insurance": "Economics, finance and business decisions",
    "2017_Jet_Lag": "Health, population and social systems",
    "2017_Sustainable_Cities_Needed!": "Environmental, ecological, energy and sustainability",
    "2019_Bottle_Battles": "Environmental, ecological, energy and sustainability",
    "2019_Charge!": "Environmental, ecological, energy and sustainability",
    "2020_Drowning_in_Plastic": "Environmental, ecological, energy and sustainability",
    "2020_Moving_North": "Environmental, ecological, energy and sustainability",
    "2020_The_Best_Summer": "Economics, finance and business decisions",
    "2021_Hot_Dog_Concession": "Operations, transport and logistics",
    "2021_Re-Optimizing_Food_Systems": "Environmental, ecological, energy and sustainability",
    "2021_Storing_the_Sun": "Environmental, ecological, energy and sustainability",
    "2022_Forestry_for_Carbon": "Environmental, ecological, energy and sustainability",
    "2022_Power_Profile_of": "Engineering, physical systems and design",
    "2022_The_Need_for": "Environmental, ecological, energy and sustainability",
    "2022_Water_and_Hydroelectric": "Environmental, ecological, energy and sustainability",
    "2023_Dandelions:_Friend?_Foe?": "Environmental, ecological, energy and sustainability",
    "2023_Drought-Stricken_Plant_Communities": "Environmental, ecological, energy and sustainability",
    "2023_Light_Pollution": "Environmental, ecological, energy and sustainability",
    "2023_Preparing_for_Olympic": "Operations, transport and logistics",
    "2023_Prioritizing_the_UN": "Governance, security and information systems",
    "2023_The_Future_of": "Governance, security and information systems",
    "2024_Reducing_Illegal_Wildlife": "Environmental, ecological, energy and sustainability",
    "2024_Resource_Availability_and": "Environmental, ecological, energy and sustainability",
    "2024_Searching_for_Submersibles": "Engineering, physical systems and design",
    "2024_Sustainability_of_Property": "Economics, finance and business decisions",
    "2024_The_Modeling_Musical": "Operations, transport and logistics",
    "2025_Cyber_Strong?": "Governance, security and information systems",
    "2025_Making_Room_for": "Environmental, ecological, energy and sustainability",
    "2025_Managing_Sustainable_Tourism": "Environmental, ecological, energy and sustainability",
}


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    separator = ["---"] * len(headers)
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join(separator) + " |")
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def build_statistics(tasks: dict) -> dict:
    task_ids = set(tasks)
    mapped_ids = set(CATEGORY_BY_TASK)
    missing = sorted(task_ids - mapped_ids)
    unknown = sorted(mapped_ids - task_ids)
    invalid_categories = sorted(set(CATEGORY_BY_TASK.values()) - set(CATEGORY_ORDER))
    if missing or unknown or invalid_categories:
        raise ValueError(
            f"Invalid task classification: missing={missing}, unknown={unknown}, "
            f"invalid_categories={invalid_categories}"
        )

    counts = Counter(CATEGORY_BY_TASK.values())
    source_by_category = defaultdict(Counter)
    task_rows = []
    for task_id, task in sorted(tasks.items()):
        category = CATEGORY_BY_TASK[task_id]
        source_by_category[category][str(task.get("source", "Unknown"))] += 1
        task_rows.append(
            {
                "id": task_id,
                "year": int(task.get("year", 0)),
                "source": str(task.get("source", "Unknown")),
                "title": str(task.get("title", "")).replace("|", "\\|"),
                "primary_category": category,
            }
        )
    return {
        "task_count": len(tasks),
        "category_counts": {category: counts[category] for category in CATEGORY_ORDER},
        "category_shares": {
            category: counts[category] / len(tasks) for category in CATEGORY_ORDER
        },
        "source_by_category": {
            category: dict(sorted(values.items()))
            for category, values in source_by_category.items()
        },
        "tasks": task_rows,
    }


def render_markdown(statistics: dict) -> str:
    total = statistics["task_count"]
    summary_rows = [
        [
            category,
            str(statistics["category_counts"][category]),
            f"{statistics['category_shares'][category] * 100:.1f}%",
        ]
        for category in CATEGORY_ORDER
    ]
    source_names = sorted(
        {source for values in statistics["source_by_category"].values() for source in values}
    )
    cross_rows = []
    for category in CATEGORY_ORDER:
        values = statistics["source_by_category"].get(category, {})
        cross_rows.append([category] + [str(values.get(source, 0)) for source in source_names])
    task_rows = [
        [
            row["id"],
            str(row["year"]),
            row["source"],
            row["title"],
            row["primary_category"],
        ]
        for row in statistics["tasks"]
    ]
    return "\n".join(
        [
            "# ModelingBench Task Type Statistics",
            "",
            f"Dataset: `data/modeling_data_final.json` ({total} tasks).",
            "",
            "Classification rule: each mixed-domain task is assigned to the "
            "primary real-world system or decision requested in its original statement. "
            "This is a descriptive domain taxonomy, not a Judge-derived label.",
            "",
            "## Primary Domain Distribution",
            "",
            markdown_table(["Primary domain", "Tasks", "Share"], summary_rows),
            "",
            "## Source by Primary Domain",
            "",
            markdown_table(["Primary domain"] + source_names, cross_rows),
            "",
            "## Task-Level Classification",
            "",
            markdown_table(
                ["Task ID", "Year", "Source", "Title", "Primary domain"],
                task_rows,
            ),
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=REPO_ROOT / "data" / "modeling_task_type_statistics.md",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=REPO_ROOT / "data" / "modeling_task_type_statistics.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tasks = json.loads(args.data.resolve().read_text(encoding="utf-8"))
    statistics = build_statistics(tasks)
    args.markdown_output.resolve().write_text(
        render_markdown(statistics), encoding="utf-8"
    )
    args.json_output.resolve().write_text(
        json.dumps(statistics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Markdown table: {args.markdown_output.resolve()}")
    print(f"JSON statistics: {args.json_output.resolve()}")


if __name__ == "__main__":
    main()
