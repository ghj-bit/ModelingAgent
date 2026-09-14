"""Build the audited ModelingBench train/test split used by workflow evolution."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "data" / "modeling_data_final.json"
CATEGORY_PATH = ROOT / "data" / "modeling_task_type_statistics.json"
OUTPUT_PATH = ROOT / "data" / "modelingbench_train_test_split.json"
TRAIN_PATH = ROOT / "data" / "modeling_data_train.json"
TEST_PATH = ROOT / "data" / "modeling_data_test.json"
EXCLUDED_PATH = ROOT / "data" / "modeling_data_excluded.json"


REQUIRED_TRAIN = {
    "2003_Aviation_Baggage_Screening",
    "2013_Bank_Service_Problem",
    "2025_Managing_Sustainable_Tourism",
}

# These two records describe the missing asset instead of preserving the values needed
# by the task. They are excluded until the original asset is restored.
MISSING_ASSETS = {
    "2001_Adolescent_Pregnancy": (
        "题目要求分析12个县的2000年数据，但当前JSON只保留列名和1998/1999汇总，"
        "没有图中12行县级数值。"
    ),
    "2004_To_Be_Secure": (
        "题目明确依赖附件A/B中的防御措施成本与效果；当前JSON只有机会成本表和附件说明，"
        "没有附件A/B的数值。"
    ),
}

# Strict criterion: the requested real-case result cannot be reproduced from the local
# statement alone because it explicitly needs historical/current data, a named-site
# dataset, policy comparison, or research on selected real entities.
EXTERNAL_REQUIRED = {
    "2005_Flood_Planning": "需要Lake Murray下游地形、河网和溃坝水文参数才能回答具体淹没范围。",
    "2005_Nonrenewable_Resources": "明确要求自行寻找全球储量、发现量、消费量和价格的历史数据。",
    "2007_Gerrymandering": "纽约州应用需要人口空间分布和州界/选区地理数据。",
    "2007_Organ_Transplant:_The": "要求建模真实移植网络并比较另一国家政策，本地只给出少量汇总数。",
    "2008_Going_Green": "全国碳中和可行性与成本测算需要排放、碳汇和经济数据。",
    "2011_How_environmentally_and": "题面直接列出BP和EIA能源数据源，生命周期与发电结构分析依赖外部数据。",
    "2011_Space_Shuttle_Problem:": "十年成本、载荷与飞行计划需要运载工具能力、价格和任务需求数据。",
    "2015_Is_it_sustainable?": "要求选择一个最不发达国家并依据其人口、资源、经济和社会条件制定计划。",
    "2016_Are_we_heading": "要求选择真实缺水国家/地区并分析历史、地质、生态、人口和健康数据。",
    "2016_Measuring_the_Evolution": "明确要求用多个历史时期的数据验证信息传播模型。",
    "2016_Modeling_Refugee_Immigration": "六条迁徙路线、国家容量、法律和动态事件数据未在本地完整给出。",
    "2016_Record_Insurance": "破纪录概率和保险定价需要历年世界纪录、赛事和运动员表现数据。",
    "2017_Jet_Lag": "给定出发城市后，候选会址比较仍需时区、航程、气候和旅行数据。",
    "2017_Sustainable_Cities_Needed!": "明确要求研究两个真实城市的现有增长规划并进行跨洲比较。",
    "2020_Drowning_in_Plastic": "全球及区域塑料产生、处理能力、政策效果和产业影响需要外部数据。",
    "2020_Moving_North": "50年鱼群迁移预测需要海温情景、物种适温、海域和渔业经济数据。",
    "2021_Re-Optimizing_Food_Systems": "要求应用于一个发达国家和一个发展中国家，需国家食物系统指标。",
    "2022_Forestry_for_Carbon": "具体森林的生长、碳汇、采伐和多重价值分析需要所选森林数据。",
    "2022_Power_Profile_of": "东京赛道、车手功率曲线、坡度和天气条件未在本地题面中提供。",
    "2022_Water_and_Hydroelectric": "五州分水与发电方案需要库容、入流、需求和发电关系数据。",
    "2023_Dandelions:_Friend?_Foe?": "气候传播及另外两种入侵植物的真实案例需要物种和地区资料。",
    "2023_Light_Pollution": "对两个真实地点计算风险和干预效果需要夜光、人口、生态与照明数据。",
    "2023_Preparing_for_Olympic": "三个场馆的比赛日程、项目和奖牌仪式安排需从所列外部资料取得。",
    "2024_Reducing_Illegal_Wildlife": "题目明确要求以研究和数据分析支持具体客户的五年项目。",
    "2024_Searching_for_Submersibles": "Ionian Sea定位与搜救需要海流、风、深度、海岸和设备性能数据。",
    "2024_Sustainability_of_Property": "两洲灾害地区和历史地标应用需要灾损、保费、房产及适应成本数据。",
    "2024_The_Modeling_Musical": "明确要求调查所选艺人的历史巡演并据此规划下一次巡演。",
    "2025_Cyber_Strong?": "明确要求使用GCI、VERIS/VCDB等国家政策和网络事件数据。",
    "2025_Managing_Sustainable_Tourism": "Juneau方案及另一旅游地迁移验证需要题面引用的地方报告和目的地数据。",
}

# These tasks are executable with explicit assumptions or synthetic cases, but retrieval
# materially improves calibration or factual grounding.
EXTERNAL_RECOMMENDED = {
    "2001_Design_of_an": "真实航站楼流量、步行距离和登机口数据可校准模型，但题目允许设计一般模型。",
    "2001_The_Bicycle_Wheel": "轮组质量与空气阻力参数可外查，也可作为清晰假设或参数化输入。",
    "2002_Airline_Overbooking": "真实缺席率和补偿成本有助于校准，但可用概率参数和敏感性分析完成。",
    "2003_The_Stunt_Person": "纸箱压溃和缓冲性能可外查，也可通过材料参数与实验方案表达。",
    "2006_Inflation_of_the": "伞衣、气动力和折叠参数可外查，但可建立无量纲或参数化模型。",
    "2006_Wheel_Chair_Access": "机场流量、人工与设备成本可提升真实性，题目允许构造多规模示例。",
    "2011_Snowboard_Course": "运动员与雪道物理参数可用于数值校准，核心模型可参数化完成。",
    "2013_The_Ultimate_Brownie": "材料热物性和烤箱边界条件有助于校准，题面允许比较型模型。",
    "2019_Charge!": "电价、设备功率和历史增长数据有助于成本量化，亦可用情景假设。",
    "2021_Storing_the_Sun": "电器负荷和当地太阳辐照数据有助于选型，但电池表已嵌入且可做情景测试。",
    "2022_The_Need_for": "蜂群生物参数可增强校准，题面已给出关键数量级并可做敏感性分析。",
    "2023_Prioritizing_the_UN": "SDG关联证据和指标数据可增强网络权重，17项目标已完整列出。",
    "2023_The_Future_of": "历届奥运成本和社会影响能支持指标权重，策略模型本身可用情景数据完成。",
}

EMBEDDED_DATA = {
    "2003_Aviation_Baggage_Screening": "EDS参数及机场TIS表已经转写到question中。",
    "2010_Curbing_City_Violence": "2000-2008暴力、人口、失业、学校及监狱/假释表均已转写。",
    "2013_Bank_Service_Problem": "到达间隔和服务时间的离散概率表已完整转写。",
    "2021_Hot_Dog_Concession": "五年十场销量表、包装规格与成本表已完整转写。",
    "2021_Storing_the_Sun": "五种电池的价格、功率、效率和容量表已完整转写。",
}

# Hand-stratified holdout across age, source, domain, and data dependency. The only
# singleton category (Sudoku/combinatorial design) stays in training so evolution sees it.
TEST_IDS = {
    "2001_Design_of_an",
    "2002_Wind_and_Waterspray",
    "2004_Motel_Cleaning_Problem",
    "2005_Nonrenewable_Resources",
    "2006_Inflation_of_the",
    "2008_Going_Green",
    "2009_Designing_a_Traffic",
    "2010_Curbing_City_Violence",
    "2011_How_environmentally_and",
    "2013_The_Ultimate_Brownie",
    "2016_Modeling_Refugee_Immigration",
    "2019_Bottle_Battles",
    "2021_Hot_Dog_Concession",
    "2021_Re-Optimizing_Food_Systems",
    "2023_Drought-Stricken_Plant_Communities",
    "2024_Resource_Availability_and",
    "2024_Sustainability_of_Property",
    "2025_Cyber_Strong?",
}


def counts(ids: list[str], audit: dict[str, dict]) -> dict:
    return {
        "total": len(ids),
        "by_primary_category": dict(sorted(Counter(audit[x]["primary_category"] for x in ids).items())),
        "by_source": dict(sorted(Counter(audit[x]["source"] for x in ids).items())),
        "by_external_retrieval": dict(
            sorted(Counter(audit[x]["external_retrieval"] for x in ids).items())
        ),
        "by_local_data_status": dict(
            sorted(Counter(audit[x]["local_data_status"] for x in ids).items())
        ),
    }


def main() -> None:
    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    categories_doc = json.loads(CATEGORY_PATH.read_text(encoding="utf-8"))
    categories = {task["id"]: task["primary_category"] for task in categories_doc["tasks"]}

    all_ids = list(dataset)
    assert set(categories) == set(all_ids)
    assert REQUIRED_TRAIN <= set(all_ids)
    assert TEST_IDS.isdisjoint(REQUIRED_TRAIN)
    assert TEST_IDS.isdisjoint(MISSING_ASSETS)

    audit: dict[str, dict] = {}
    for task_id, task in dataset.items():
        if task_id in MISSING_ASSETS:
            external = "not_assessed"
            local_status = "incomplete_missing_required_asset"
            reason = MISSING_ASSETS[task_id]
            eligible = False
        elif task_id in EXTERNAL_REQUIRED:
            external = "required"
            local_status = "external_data_not_bundled"
            reason = EXTERNAL_REQUIRED[task_id]
            eligible = True
        elif task_id in EXTERNAL_RECOMMENDED:
            external = "recommended"
            local_status = (
                "complete_embedded_data" if task_id in EMBEDDED_DATA else "complete_self_contained"
            )
            reason = EXTERNAL_RECOMMENDED[task_id]
            eligible = True
        else:
            external = "not_required"
            local_status = (
                "complete_embedded_data" if task_id in EMBEDDED_DATA else "complete_self_contained"
            )
            reason = EMBEDDED_DATA.get(
                task_id,
                "题面提供了定义建模任务所需的情境和约束；允许声明假设、构造情景或进行参数化分析。",
            )
            eligible = True

        audit[task_id] = {
            "year": task["year"],
            "title": task["title"],
            "source": task["source"],
            "level": task["level"],
            "primary_category": categories[task_id],
            "eligible_for_split": eligible,
            "local_data_status": local_status,
            "external_retrieval": external,
            "reason": reason,
        }

    eligible_ids = [task_id for task_id in all_ids if audit[task_id]["eligible_for_split"]]
    test_ids = [task_id for task_id in all_ids if task_id in TEST_IDS]
    train_ids = [task_id for task_id in eligible_ids if task_id not in TEST_IDS]
    excluded_ids = [task_id for task_id in all_ids if not audit[task_id]["eligible_for_split"]]

    assert len(all_ids) == 68
    assert len(train_ids) == 48
    assert len(test_ids) == 18
    assert len(excluded_ids) == 2
    assert REQUIRED_TRAIN <= set(train_ids)
    assert set(train_ids).isdisjoint(test_ids)
    assert set(train_ids) | set(test_ids) | set(excluded_ids) == set(all_ids)

    complete_local = [
        task_id
        for task_id in all_ids
        if audit[task_id]["local_data_status"]
        in {"complete_self_contained", "complete_embedded_data"}
    ]
    required_external = [task_id for task_id in all_ids if audit[task_id]["external_retrieval"] == "required"]
    recommended_external = [
        task_id for task_id in all_ids if audit[task_id]["external_retrieval"] == "recommended"
    ]

    output = {
        "schema_version": "1.0",
        "source_dataset": str(DATASET_PATH.relative_to(ROOT)).replace("\\", "/"),
        "materialized_datasets": {
            "train": str(TRAIN_PATH.relative_to(ROOT)).replace("\\", "/"),
            "test": str(TEST_PATH.relative_to(ROOT)).replace("\\", "/"),
            "excluded": str(EXCLUDED_PATH.relative_to(ROOT)).replace("\\", "/"),
        },
        "audit_date": "2026-09-14",
        "policy": {
            "split_unit": "task_id",
            "split_strategy": (
                "人工分层留出：兼顾年份、竞赛来源、一级主题和数据依赖；唯一的组合设计题保留在训练集。"
            ),
            "eligibility": (
                "题干完整且可通过本地信息或明确的外部检索完成；缺关键原始附件的题目不进入主划分。"
            ),
            "external_retrieval_definition": {
                "required": "不获取真实外部数据就无法可复现地完成题目指定的真实案例、历史验证或数值应用。",
                "recommended": "可以用清晰假设或合成情景完成，但检索能显著改善参数校准和事实依据。",
                "not_required": "题面信息足以建立、验证和讨论模型，外部检索不是任务成立的必要条件。",
            },
            "usage": (
                "演化只从train采样；test在工作流和选择规则冻结后仅运行一次。"
                "检索题与非检索题应分别汇报分数，避免把检索可用性误当成建模能力。"
            ),
        },
        "required_training_tasks": sorted(REQUIRED_TRAIN),
        "train": train_ids,
        "test": test_ids,
        "excluded_missing_assets": excluded_ids,
        "groups": {
            "complete_locally_without_required_retrieval": complete_local,
            "external_retrieval_required": required_external,
            "external_retrieval_recommended": recommended_external,
            "complete_embedded_data": [task_id for task_id in all_ids if task_id in EMBEDDED_DATA],
        },
        "protocol_subsets": {
            "train_closed_book": [
                task_id for task_id in train_ids if audit[task_id]["external_retrieval"] != "required"
            ],
            "train_retrieval_required": [
                task_id for task_id in train_ids if audit[task_id]["external_retrieval"] == "required"
            ],
            "test_closed_book": [
                task_id for task_id in test_ids if audit[task_id]["external_retrieval"] != "required"
            ],
            "test_retrieval_required": [
                task_id for task_id in test_ids if audit[task_id]["external_retrieval"] == "required"
            ],
        },
        "statistics": {
            "all_records": len(all_ids),
            "eligible_records": len(eligible_ids),
            "train": counts(train_ids, audit),
            "test": counts(test_ids, audit),
            "excluded": counts(excluded_ids, audit),
        },
        "task_audit": audit,
    }

    TRAIN_PATH.write_text(
        json.dumps({task_id: dataset[task_id] for task_id in train_ids}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    TEST_PATH.write_text(
        json.dumps({task_id: dataset[task_id] for task_id in test_ids}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    EXCLUDED_PATH.write_text(
        json.dumps({task_id: dataset[task_id] for task_id in excluded_ids}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")
    print(json.dumps(output["statistics"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
