import numpy as np 
from scipy.stats import pearsonr

from utils.argparser import *
from utils.logger import *
from utils.csv_file import *
from utils.sentiment_analysis import *
from utils.visualizer import *

AMOUNT_TIERS = 3
AMOUNT_VARIANTS = 3
AMOUNT_SCENARIOS_TIER_1 = 8
AMOUNT_SCENARIOS_TIER_2 = 24
AMOUNT_SCENARIOS_TIER_3 = 16

if __name__ == "__main__":
    args = perform_evaluation_argparsing()
    chatbot_responses = []
    
    logger.info(f"[perform_evaluation.py] Initializing Emotionally Intelligent Chatbot Evaluation.")

    # Establish Paths and File Names  
    if not args.enhancement_method_enabled:
        path_conversations = f"conversations/{args.benchmark_bot}/{args.benchmark_character}"
        path_evaluation = f"evaluation/{args.benchmark_bot}/{args.benchmark_character}"
        file_name_pearson_correlation = f"pearson_correlation_{args.benchmark_bot}_{args.benchmark_character}.csv"
        file_name_PYSentimiento_tier1 = f"PYSentimiento_evaluation_{args.benchmark_bot}_{args.benchmark_character}_tier_1.csv"
        file_name_PYSentimiento_tier2 = f"PYSentimiento_evaluation_{args.benchmark_bot}_{args.benchmark_character}_tier_2.csv"
        file_name_PYSentimiento_tier3 = f"PYSentimiento_evaluation_{args.benchmark_bot}_{args.benchmark_character}_tier_3.csv"
        file_name_heatmap = f"benchmark_heatmap_{args.benchmark_bot}_{args.benchmark_character}.jpeg"
        file_name_heatmap_differences = f"benchmark_heatmap_differences_{args.benchmark_bot}_{args.benchmark_character}.jpeg"
    else:
        path_conversations = f"conversations/{args.benchmark_bot}/{args.enhancement_method}"
        path_evaluation = f"evaluation/{args.benchmark_bot}/{args.enhancement_method}"
        file_name_pearson_correlation = f"pearson_correlation_{args.benchmark_bot}_{args.enhancement_method}.csv"
        file_name_PYSentimiento_tier1 = f"PYSentimiento_evaluation_{args.benchmark_bot}_{args.enhancement_method}_tier_1.csv"
        file_name_PYSentimiento_tier2 = f"PYSentimiento_evaluation_{args.benchmark_bot}_{args.enhancement_method}_tier_2.csv"
        file_name_PYSentimiento_tier3 = f"PYSentimiento_evaluation_{args.benchmark_bot}_{args.enhancement_method}_tier_3.csv"
        file_name_heatmap = f"benchmark_heatmap_{args.benchmark_bot}_{args.enhancement_method}.jpeg"
        file_name_heatmap_differences = f"benchmark_heatmap_differences_{args.benchmark_bot}_{args.enhancement_method}.jpeg"

    # Parse Human Baseline & Scenario Description 
    tier_1, tier1_scenarios = [], []
    tier_2, tier2_scenarios = [], []
    tier_3, tier3_scenarios = [], []

    path_results = "user_study_baseline"
    file_name_tier1 = "results_tier_1.csv"
    file_name_tier2 = "results_tier_2.csv"
    file_name_tier3 = "results_tier_3.csv"

    results_tier_1_benchmarks = load_benchmark_results_file(path_results, file_name_tier1, 1)
    results_tier_2_benchmarks = load_benchmark_results_file(path_results, file_name_tier2, 2)
    results_tier_3_benchmarks = load_benchmark_results_file(path_results, file_name_tier3, 3)

    for index in range(AMOUNT_SCENARIOS_TIER_1):
        tier_1.append(float(results_tier_1_benchmarks.get_cell(index, "CIAS")))
        tier1_scenarios.append([results_tier_1_benchmarks.get_cell(index, "SCENARIO_ID"),
                                results_tier_1_benchmarks.get_cell(index, "INFORMATION_TYPE")])

    for index in range(AMOUNT_SCENARIOS_TIER_2):
        tier_2.append(float(results_tier_2_benchmarks.get_cell(index, "CIAS")))
        tier2_scenarios.append([results_tier_2_benchmarks.get_cell(index, "SCENARIO_ID"), 
                                results_tier_2_benchmarks.get_cell(index, "INFORMATION_TYPE"), 
                                results_tier_2_benchmarks.get_cell(index, "RECIPIENT"),
                                results_tier_2_benchmarks.get_cell(index, "USE")])

    for index in range(AMOUNT_SCENARIOS_TIER_3):
        tier_3.append(float(results_tier_3_benchmarks.get_cell(index, "CIAS")))
        tier3_scenarios.append([results_tier_3_benchmarks.get_cell(index, "SCENARIO_ID"),
                                results_tier_3_benchmarks.get_cell(index, "INFORMATION_TYPE"),
                                results_tier_3_benchmarks.get_cell(index, "RELATIONSHIP_AND_INCENTIVE")
        ])

    logger.info(f"[perform_evaluation.py] Successfully parsed Human Baseline of Contextual Integrity Acceptability Scores (CIAS).")

    # Parse Benchmark Files and create Result Files 
    CIAS_benchmark = []
    
    for tier in range(1, AMOUNT_TIERS + 1):
        responses_current_tier = []
        CIAS_current_tier = []

        if not args.enhancement_method_enabled:
            file_name_evaluation = f"{args.benchmark_bot}_{args.benchmark_character}_tier_{tier}_results.csv"
        else:
            file_name_evaluation = f"{args.benchmark_bot}_{args.enhancement_method}_tier_{tier}_results.csv"

        result_file = create_benchmark_results_file(path_evaluation, file_name_evaluation, tier)

        for variant in range(1, AMOUNT_VARIANTS + 1):
            CIAS_current_variant = []
            
            if not args.enhancement_method_enabled:
                file_name_conversation = f"{args.benchmark_bot}_{args.benchmark_character}_tier_{tier}_variant_{variant}_conversation.csv"
            else:
                file_name_conversation = f"{args.benchmark_bot}_{args.enhancement_method}_tier_{tier}_variant_{variant}_conversation.csv"

            conversation_file = load_benchmark_file(path_conversations, file_name_conversation, tier)
            amount_rows = conversation_file.get_amount_rows()

            for index in range(amount_rows):
                responses_current_tier.append(conversation_file.get_cell(index, "CHATBOT_RESPONSE"))

                CIAS = conversation_file.get_cell(index, "CIAS")
                if CIAS != "" and CIAS != "NONE":
                    CIAS_current_variant.append(CIAS)

            if tier == 1:
                if len(CIAS_current_variant) != AMOUNT_SCENARIOS_TIER_1:
                    logger.error(f"[perform_evaluation.py] Conversation File {file_name_conversation} does not contain {AMOUNT_SCENARIOS_TIER_1} CIAS Scores!")
            
            if tier == 2:
                if len(CIAS_current_variant) != AMOUNT_SCENARIOS_TIER_2:
                    logger.error(f"[perform_evaluation.py] Conversation File {file_name_conversation} does not contain {AMOUNT_SCENARIOS_IER_2} CIAS Scores!")

            if tier == 3: 
                if len(CIAS_current_variant) != AMOUNT_SCENARIOS_TIER_3:
                    logger.error(f"[perform_evaluation.py] Conversation File {file_name_conversation} does not contain {AMOUNT_SCENARIOS_TIER_3} CIAS Scores!")
            
            CIAS_current_tier.append(CIAS_current_variant)

        chatbot_responses.append(responses_current_tier)
        amount_scenarios, scenarios = 0, []

        if tier == 1: 
            amount_scenarios = AMOUNT_SCENARIOS_TIER_1
            scenarios = tier1_scenarios

        if tier == 2: 
            amount_scenarios = AMOUNT_SCENARIOS_TIER_2
            scenarios = tier2_scenarios

        if tier == 3:
            amount_scenarios = AMOUNT_SCENARIOS_TIER_3
            scenarios = tier3_scenarios
        
        for idx in range(amount_scenarios):
            average_CIAS = round((float(CIAS_current_tier[0][idx]) + float(CIAS_current_tier[1][idx]) + float(CIAS_current_tier[2][idx])) / 3, 2)
            result_file.add_row(scenarios[idx] + [CIAS_current_tier[0][idx], CIAS_current_tier[1][idx], CIAS_current_tier[2][idx], average_CIAS])
            CIAS_benchmark.append(average_CIAS)

        logger.info(f"[perform_evaluation.py] Result File {file_name_evaluation} successfully created.")

    # Calculate Pearson Correlation and p-Value
    human_baseline_tier1 = np.array(tier_1)
    human_baseline_tier2 = np.array(tier_2)
    human_baseline_tier3 = np.array(tier_3)

    chatbot_tier1 = np.array(CIAS_benchmark[0:8])
    chatbot_tier2 = np.array(CIAS_benchmark[8:32])
    chatbot_tier3 = np.array(CIAS_benchmark[32:48])

    corr_tier1, p_value_tier1 = pearsonr(human_baseline_tier1, chatbot_tier1)
    corr_tier2, p_value_tier2 = pearsonr(human_baseline_tier2, chatbot_tier2)
    corr_tier3, p_value_tier3 = pearsonr(human_baseline_tier3, chatbot_tier3)

    pearson_corr_file = CSVFile(path_evaluation, file_name_pearson_correlation, ["CORR_TIER1", "P_VALUE_TIER1", "CORR_TIER2", "P_VALUE_TIER2", "CORR_TIER3", "P_VALUE_TIER3"], False)
    pearson_corr_file.add_row([corr_tier1, p_value_tier1, corr_tier2, p_value_tier2, corr_tier3, p_value_tier3])
    logger.info(f"[perform_evaluation.py] Pearson Correlation File {file_name_pearson_correlation} successfully created.")

    # Perform PYSentimiento Analysis
    PYSentimiento_analyzer_tier1 = PYSentimiento(path_evaluation, file_name_PYSentimiento_tier1)
    PYSentimiento_analyzer_tier1.perform_analysis(chatbot_responses[0])

    PYSentimiento_analyzer_tier2 = PYSentimiento(path_evaluation, file_name_PYSentimiento_tier2)
    PYSentimiento_analyzer_tier2.perform_analysis(chatbot_responses[1])

    PYSentimiento_analyzer_tier3 = PYSentimiento(path_evaluation, file_name_PYSentimiento_tier3)
    PYSentimiento_analyzer_tier3.perform_analysis(chatbot_responses[2])

    # Perform Visualization 
    block_1 = np.array(CIAS_benchmark[0:8]).reshape(4, 2)
    block_2 = np.array(CIAS_benchmark[8:20]).reshape(4, 3)
    block_3 = np.array(CIAS_benchmark[20:32]).reshape(4, 3)
    block_4 = np.array(CIAS_benchmark[32:48]).reshape(4, 4)
    create_heatmap([block_1, block_2, block_3, block_4], path_evaluation, file_name_heatmap, False)

    block_1_differences = np.subtract(CIAS_benchmark[0:8], tier_1).reshape(4, 2)
    block_2_differences = np.subtract(CIAS_benchmark[8:20], tier_2[0:12]).reshape(4, 3)
    block_3_differences = np.subtract(CIAS_benchmark[20:32], tier_2[12:24]).reshape(4, 3)
    block_4_differences = np.subtract(CIAS_benchmark[32:48], tier_3).reshape(4, 4)
    create_heatmap([block_1_differences, block_2_differences, block_3_differences, block_4_differences], path_evaluation, file_name_heatmap_differences, True)

    logger.info(f"[perform_evaluation.py] Emotionally Intelligent Chatbot Evaluation completed successfully.")