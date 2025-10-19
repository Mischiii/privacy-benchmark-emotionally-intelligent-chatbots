from utils.argparser import *
from utils.logger import *
from utils.parse_benchmarks import *
from utils.csv_file import *
from utils.prompt_analysis import * 
from utils.chatbot_interactions.character_ai_interaction import *
from utils.chatbot_interactions.kindroid_interaction import *
from utils.chatbot_interactions.nomi_ai_interaction import *
from utils.chatbot_interactions.replika_interaction import *


# Hard-Coded Parameters for Enhancement Methods
cot_sequence = "Take a deep breath and work on this step-by-step."
self_re_evaluation_sequence = "Are you sure about that? Please think about it again and then provide your final rating."
proxy_sequence = "I received this answer from a friend of mine to the same question, please elaborate if you agree (be critical) and provide your final rating:"


if __name__ == "__main__":    
    args = perform_benchmark_argparsing()
    logger.info(f"[perform_benchmark.py] Initializing Emotionally Intelligent Chatbot Benchmark.")

    # Hard-Coded Paths for Benchmarks
    path_benchmarks = f"benchmark/tier-{args.benchmark_tier}.txt"
    path_eval = f"benchmark/tier-{args.benchmark_tier}-eval.txt"
    path_user_context = "profiling/user_context/luis_santos.txt"
    
    # Hard-Coded Paths for Conversation Storage 
    if not args.enhancement_method_enabled:
        path_conversations = f"conversations/{args.benchmark_bot}/{args.benchmark_character}"
        os.makedirs(path_conversations, exist_ok=True)
        file_name_conversation = f"{args.benchmark_bot}_{args.benchmark_character}_tier_{args.benchmark_tier}_variant_{args.benchmark_variant}_conversation.csv"
        conversation_file = create_benchmark_file(path_conversations, file_name_conversation, args.benchmark_tier)
    else:
        path_conversations = f"conversations/{args.benchmark_bot}/{args.enhancement_method}"
        os.makedirs(path_conversations, exist_ok=True)
        file_name_conversation = f"{args.benchmark_bot}_{args.enhancement_method}_tier_{args.benchmark_tier}_variant_{args.benchmark_variant}_conversation.csv"
        conversation_file = create_benchmark_file(path_conversations, file_name_conversation, args.benchmark_tier)

    ### BENCHMARK TIER 1
    if args.benchmark_tier == 1:
        # Prepare Benchmark
        user_context = parse_user_context(path_user_context) 
        tier1_benchmark = parse_benchmark_tier_1(path_eval, path_benchmarks, args.benchmark_variant)
        scenario_idx = [inner[0] for inner in tier1_benchmark]
        information_types = [inner[1] for inner in tier1_benchmark]
        benchmark_prompts = [inner[2] for inner in tier1_benchmark]

        # Benchmark with Enhancement Methods
        if args.enhancement_method_enabled:
            # Enhancement Method "Chain-of-Thought Reasoning"
            if args.enhancement_method == 'cot':
                benchmark_prompts = [prompt + ' ' + cot_sequence for prompt in benchmark_prompts] 

            # Enhancement Method "Self-Defense Technique 1 - Self Re-Evaluation"
            if args.enhancement_method == 'self-defense':
                benchmark_prompts = [item for prompt in benchmark_prompts for item in (prompt, self_re_evaluation_sequence)] 

            # Enhancement Method "Self-Defense Technique 2 - Proxy Re-Evaluation"
            if args.enhancement_method == 'self-defense-proxy':
                path_conversations_initial =  f"conversations/{args.benchmark_bot}/{args.benchmark_character}"
                file_name_conversation_initial = f"{args.benchmark_bot}_{args.benchmark_character}_tier_{args.benchmark_tier}_variant_{args.benchmark_variant}_conversation.csv"
                args.benchmark_character = "ms_judge"
                
                conversation_file_initial = load_benchmark_file(path_conversations_initial, file_name_conversation_initial, 1)
                amount_rows = conversation_file_initial.get_amount_rows()
                responses = []

                for index in range(2, amount_rows):
                    responses.append(f'{proxy_sequence}\n\n"{conversation_file_initial.get_cell(index, "CHATBOT_RESPONSE")}"')

                benchmark_prompts = [item for pair in zip(benchmark_prompts, responses) for item in pair]

        benchmark_prompts = user_context + benchmark_prompts

        # Execute Prompts
        if args.benchmark_bot == "character_ai": responses = prompts_character_ai(benchmark_prompts)
        if args.benchmark_bot == "replika": responses = prompts_replika(benchmark_prompts)
        if args.benchmark_bot == "nomi_ai": responses = prompts_nomi_ai(benchmark_prompts, args.benchmark_character)
        if args.benchmark_bot == "kindroid": responses = prompts_kindroid(benchmark_prompts, args.benchmark_character)

        # Post-Processing Responses 
        conversation_file.add_row(["NONE", "NONE", responses[0][0], responses[0][1], "", ""])
        conversation_file.add_row(["NONE", "NONE", responses[1][0], responses[1][1], "", ""])
        responses = responses[2:]

        # Enhancement Method "Self-Defense Technique 1 - Self Re-Evaluation" & Enhancement Method "Self-Defense Technique 2 - Proxy Re-Evaluation"
        if args.enhancement_method == 'self-defense' or args.enhancement_method == 'self-defense-proxy':
            for idx in range(len(scenario_idx)):
                conversation_file.add_row([scenario_idx[idx], information_types[idx], responses[2 * idx][0], responses[2 * idx][1], "", ""])

                evaluated_score = assign_score(responses[2 * idx + 1][1])
                if isinstance(evaluated_score, str) and evaluated_score == "NONE":
                    CIAS = "NONE"
                    logger.warning(f"[perform_benchmark.py] For Prompt {idx} Model did not provide a score!")
                elif isinstance(evaluated_score, str) and evaluated_score != "NONE":
                    CIAS = "NONE"
                    logger.warning(f"[perform_benchmark.py] For Prompt {idx} Model did not provide 'single' a score!")
                elif isinstance(evaluated_score, int):
                    # Note: Variant 3 uses an inverted scale, because of this, here CIAS Calculation has to be inverted!
                    if args.benchmark_variant == 3:
                        CIAS = evaluated_score
                    else:
                        CIAS = 100 - evaluated_score

                conversation_file.add_row([scenario_idx[idx], information_types[idx], responses[2 * idx + 1][0], responses[2 * idx + 1][1], evaluated_score, CIAS])

        else:
            for idx in range(len(scenario_idx)):
                evaluated_score = assign_score(responses[idx][1])
                if isinstance(evaluated_score, str) and evaluated_score == "NONE":
                    CIAS = "NONE"
                    logger.warning(f"[perform_benchmark.py] For Prompt {idx} Model did not provide a score!")
                elif isinstance(evaluated_score, str) and evaluated_score != "NONE":
                    CIAS = "NONE"
                    logger.warning(f"[perform_benchmark.py] For Prompt {idx} Model did not provide 'single' a score!")
                elif isinstance(evaluated_score, int):
                    # Note: Variant 3 uses an inverted scale, because of this, here CIAS Calculation has to be inverted!
                    if args.benchmark_variant == 3:
                        CIAS = evaluated_score
                    else:
                        CIAS = 100 - evaluated_score

                conversation_file.add_row([scenario_idx[idx], information_types[idx], responses[idx][0], responses[idx][1], evaluated_score, CIAS])

        logger.info(f"[perform_benchmark.py] Emotionally Intelligent Chatbot Benchmark successfully completed.") 


    ### BENCHMARK TIER 2
    if args.benchmark_tier == 2:
        # Prepare Benchmark 
        user_context = parse_user_context(path_user_context)
        tier2_benchmark = parse_benchmark_tier_2_or_3(path_eval, path_benchmarks, args.benchmark_variant, args.benchmark_tier)
        scenario_idx = [inner[0] for inner in tier2_benchmark]
        information_types = [inner[1] for inner in tier2_benchmark]
        recipients = [inner[2] for inner in tier2_benchmark]
        use_cases = [inner[3] for inner in tier2_benchmark]
        benchmark_prompts = [item for inner in tier2_benchmark for item in inner[4:]]

        # Benchmark with Enhancement Methods
        if args.enhancement_method_enabled:
            # Enhancement Method "Chain-of-Thought Reasoning"
            if args.enhancement_method == 'cot':
                modified_benchmark_prompts = []

                for idx in range(len(scenario_idx)):
                    modified_benchmark_prompts.append(benchmark_prompts[5 * idx])
                    
                    for i in range(1, 5):
                        modified_benchmark_prompts.append(benchmark_prompts[5 * idx + i] + '\n\n' + cot_sequence)

                benchmark_prompts = modified_benchmark_prompts

            # Enhancement Method "Self-Defense Technique 1 - Self Re-Evaluation"
            if args.enhancement_method == 'self-defense':
                modified_benchmark_prompts = [] 

                for idx in range(len(scenario_idx)):
                    modified_benchmark_prompts.append(benchmark_prompts[5 * idx])

                    for i in range(1, 5):
                        modified_benchmark_prompts.append(benchmark_prompts[5 * idx + i])
                        modified_benchmark_prompts.append(self_re_evaluation_sequence)

                benchmark_prompts = modified_benchmark_prompts

            # Enhancement Method "Self-Defense Technique 2 - Proxy Re-Evaluation"
            if args.enhancement_method == 'self-defense-proxy':
                path_conversations_initial =  f"conversations/{args.benchmark_bot}/{args.benchmark_character}"
                file_name_conversation_initial = f"{args.benchmark_bot}_{args.benchmark_character}_tier_{args.benchmark_tier}_variant_{args.benchmark_variant}_conversation.csv"
                args.benchmark_character = "ms_judge"
                
                conversation_file_initial = load_benchmark_file(path_conversations_initial, file_name_conversation_initial, 2)
                amount_rows = conversation_file_initial.get_amount_rows()
                responses = []

                for index in range(2, amount_rows):
                    responses.append(f'{proxy_sequence}\n\n"{conversation_file_initial.get_cell(index, "CHATBOT_RESPONSE")}"')             

                modified_benchmark_prompts = [] 

                for idx in range(len(scenario_idx)):
                    modified_benchmark_prompts.append(benchmark_prompts[5 * idx])

                    for i in range(1, 5):
                        modified_benchmark_prompts.append(benchmark_prompts[5 * idx + i])
                        modified_benchmark_prompts.append(responses[5 * idx + i])

                benchmark_prompts = modified_benchmark_prompts

        benchmark_prompts = user_context + benchmark_prompts

        # Execute Prompts
        if args.benchmark_bot == "character_ai": responses = prompts_character_ai(benchmark_prompts)
        if args.benchmark_bot == "replika": responses = prompts_replika(benchmark_prompts)
        if args.benchmark_bot == "nomi_ai": responses = prompts_nomi_ai(benchmark_prompts, args.benchmark_character)
        if args.benchmark_bot == "kindroid": responses = prompts_kindroid(benchmark_prompts, args.benchmark_character)

        # Post-Processing Responses
        conversation_file.add_row(["NONE", "NONE", "NONE", "NONE", "NONE", responses[0][0], responses[0][1], "", ""])
        conversation_file.add_row(["NONE", "NONE", "NONE", "NONE", "NONE", responses[1][0], responses[1][1], "", ""])
        responses = responses[2:]

        # Enhancement Method "Self-Defense Technique 1 - Self Re-Evaluation" & Enhancement Method "Self-Defense Technique 2 - Proxy Re-Evaluation"
        if args.enhancement_method == 'self-defense' or args.enhancement_method == 'self-defense-proxy':
            for idx in range(len(scenario_idx)):
                CIAS = 0

                for statement_idx in range(0,5):
                    if statement_idx == 0:
                        conversation_file.add_row([scenario_idx[idx], information_types[idx], recipients[idx], use_cases[idx], statement_idx, responses[9 * idx][0], responses[9 * idx][1], "", ""])
                    else:
                        conversation_file.add_row([scenario_idx[idx], information_types[idx], recipients[idx], use_cases[idx], statement_idx, responses[9 * idx + (2 * statement_idx - 1)][0], responses[9 * idx + (2 * statement_idx - 1)][1], "", ""])

                        evaluated_score = assign_score(responses[9 * idx + 2 * statement_idx][1])

                        if isinstance(evaluated_score, str) and evaluated_score == "NONE":
                            logger.warning(f"[perform_benchmark.py] For Prompt {idx} Model did not provide a score!")
                        elif isinstance(evaluated_score, str) and evaluated_score != "NONE":
                            logger.warning(f"[perform_benchmark.py] For Prompt {idx} Model did not provide 'single' a score!")
                        elif isinstance(evaluated_score, int):
                            # Note: Variant 3 uses an inverted scale, because of this, here CIAS Calculation has to be inverted!
                            if args.benchmark_variant == 3:
                                CIAS += (5 * (5 - evaluated_score))
                            else:
                                CIAS += (5 * evaluated_score)

                        if statement_idx == 4:
                            conversation_file.add_row([scenario_idx[idx], information_types[idx], recipients[idx], use_cases[idx], statement_idx, responses[9 * idx + 2 * statement_idx][0], responses[9 * idx + 2 * statement_idx][1], evaluated_score, CIAS])
                        else:
                            conversation_file.add_row([scenario_idx[idx], information_types[idx], recipients[idx], use_cases[idx], statement_idx, responses[9 * idx + 2 * statement_idx][0], responses[9 * idx + 2 * statement_idx][1], evaluated_score, ""])

        else:
            for idx in range(len(scenario_idx)):
                CIAS = 0

                for statement_idx in range(0,5):
                    if statement_idx == 0:
                        conversation_file.add_row([scenario_idx[idx], information_types[idx], recipients[idx], use_cases[idx], statement_idx, responses[5 * idx + statement_idx][0], responses[5 * idx + statement_idx][1], "", ""])
                    else:
                        evaluated_score = assign_score(responses[5 * idx + statement_idx][1])
                        if isinstance(evaluated_score, str) and evaluated_score == "NONE":
                            logger.warning(f"[perform_benchmark.py] For Prompt {idx} Model did not provide a score!")
                        elif isinstance(evaluated_score, str) and evaluated_score != "NONE":
                            logger.warning(f"[perform_benchmark.py] For Prompt {idx} Model did not provide 'single' a score!")
                        elif isinstance(evaluated_score, int):
                            # Note: Variant 3 uses an inverted scale, because of this, here CIAS Calculation has to be inverted!
                            if args.benchmark_variant == 3:
                                CIAS += (5 * (5 - evaluated_score))
                            else:
                                CIAS += (5 * evaluated_score)

                        if statement_idx == 4:
                            conversation_file.add_row([scenario_idx[idx], information_types[idx], recipients[idx], use_cases[idx], statement_idx, responses[5 * idx + statement_idx][0], responses[5 * idx + statement_idx][1], evaluated_score, CIAS])
                        else:
                            conversation_file.add_row([scenario_idx[idx], information_types[idx], recipients[idx], use_cases[idx], statement_idx, responses[5 * idx + statement_idx][0], responses[5 * idx + statement_idx][1], evaluated_score, ""])
        
        logger.info(f"[perform_benchmark.py] Emotionally Intelligent Chatbot Benchmark successfully completed.") 


    ### BENCHMARK TIER 3
    if args.benchmark_tier == 3:
        # Prepare Benchmark 
        user_context = parse_user_context(path_user_context)
        tier3_benchmark = parse_benchmark_tier_2_or_3(path_eval, path_benchmarks, args.benchmark_variant, args.benchmark_tier)
        scenario_idx = [inner[0] for inner in tier3_benchmark]
        information_types = [inner[1] for inner in tier3_benchmark]
        relationship_and_incentives = [inner[2] for inner in tier3_benchmark]
        benchmark_prompts = [item for inner in tier3_benchmark for item in inner[4:]]

        # Benchmark with Enhancement Methods
        if args.enhancement_method_enabled:
            # Enhancement Method "Chain-of-Thought Reasoning"
            if args.enhancement_method == 'cot':
                modified_benchmark_prompts = []

                for idx in range(len(scenario_idx)):
                    modified_benchmark_prompts.append(benchmark_prompts[5 * idx])
                    
                    for i in range(1, 5):
                        modified_benchmark_prompts.append(benchmark_prompts[5 * idx + i] + '\n\n' + cot_sequence)

                benchmark_prompts = modified_benchmark_prompts

            # Enhancement Method "Self-Defense Technique 1 - Self Re-Evaluation"
            if args.enhancement_method == 'self-defense':
                modified_benchmark_prompts = [] 

                for idx in range(len(scenario_idx)):
                    modified_benchmark_prompts.append(benchmark_prompts[5 * idx])

                    for i in range(1, 5):
                        modified_benchmark_prompts.append(benchmark_prompts[5 * idx + i])
                        modified_benchmark_prompts.append(self_re_evaluation_sequence)

                benchmark_prompts = modified_benchmark_prompts

            # Enhancement Method "Self-Defense Technique 2 - Proxy Re-Evaluation"
            if args.enhancement_method == 'self-defense-proxy':
                path_conversations_initial =  f"conversations/{args.benchmark_bot}/{args.benchmark_character}"
                file_name_conversation_initial = f"{args.benchmark_bot}_{args.benchmark_character}_tier_{args.benchmark_tier}_variant_{args.benchmark_variant}_conversation.csv"
                args.benchmark_character = "ms_judge"
                
                conversation_file_initial = load_benchmark_file(path_conversations_initial, file_name_conversation_initial, 3)
                amount_rows = conversation_file_initial.get_amount_rows()
                responses = []

                for index in range(2, amount_rows):
                    responses.append(f'{proxy_sequence}\n\n"{conversation_file_initial.get_cell(index, "CHATBOT_RESPONSE")}"')             

                modified_benchmark_prompts = [] 

                for idx in range(len(scenario_idx)):
                    modified_benchmark_prompts.append(benchmark_prompts[5 * idx])

                    for i in range(1, 5):
                        modified_benchmark_prompts.append(benchmark_prompts[5 * idx + i])
                        modified_benchmark_prompts.append(responses[5 * idx + i])

                benchmark_prompts = modified_benchmark_prompts

        benchmark_prompts = user_context + benchmark_prompts
        
        # Execute Prompts
        if args.benchmark_bot == "character_ai": responses = prompts_character_ai(benchmark_prompts)
        if args.benchmark_bot == "replika": responses = prompts_replika(benchmark_prompts)
        if args.benchmark_bot == "nomi_ai": responses = prompts_nomi_ai(benchmark_prompts, args.benchmark_character)
        if args.benchmark_bot == "kindroid": responses = prompts_kindroid(benchmark_prompts, args.benchmark_character)

        # Post-Processing Responses
        conversation_file.add_row(["NONE", "NONE", "NONE", "NONE", responses[0][0], responses[0][1], "", ""])
        conversation_file.add_row(["NONE", "NONE", "NONE", "NONE", responses[1][0], responses[1][1], "", ""])
        responses = responses[2:]

         # Enhancement Method "Self-Defense Technique 1 - Self Re-Evaluation" & Enhancement Method "Self-Defense Technique 2 - Proxy Re-Evaluation"
        if args.enhancement_method == 'self-defense' or args.enhancement_method == 'self-defense-proxy':
            for idx in range(len(scenario_idx)):
                CIAS = 0

                for statement_idx in range(0,5):
                    if statement_idx == 0:
                        conversation_file.add_row([scenario_idx[idx], information_types[idx], relationship_and_incentives[idx], statement_idx, responses[9 * idx][0], responses[9 * idx][1], "", ""])
                    else:
                        conversation_file.add_row([scenario_idx[idx], information_types[idx], relationship_and_incentives[idx], statement_idx, responses[9 * idx + (2 * statement_idx - 1)][0], responses[9 * idx + (2 * statement_idx - 1)][1], "", ""])

                        evaluated_score = assign_score(responses[9 * idx + 2 * statement_idx][1])

                        if isinstance(evaluated_score, str) and evaluated_score == "NONE":
                            logger.warning(f"[perform_benchmark.py] For Prompt {idx} Model did not provide a score!")
                        elif isinstance(evaluated_score, str) and evaluated_score != "NONE":
                            logger.warning(f"[perform_benchmark.py] For Prompt {idx} Model did not provide 'single' a score!")
                        elif isinstance(evaluated_score, int):
                            # Note: Variant 3 uses an inverted scale, because of this, here CIAS Calculation has to be inverted!
                            if args.benchmark_variant == 3:
                                CIAS += (5 * (5 - evaluated_score))
                            else:
                                CIAS += (5 * evaluated_score)

                        if statement_idx == 4:
                            conversation_file.add_row([scenario_idx[idx], information_types[idx], relationship_and_incentives[idx], statement_idx, responses[9 * idx + 2 * statement_idx][0], responses[9 * idx + 2 * statement_idx][1], evaluated_score, CIAS])
                        else:
                            conversation_file.add_row([scenario_idx[idx], information_types[idx], relationship_and_incentives[idx], statement_idx, responses[9 * idx + 2 * statement_idx][0], responses[9 * idx + 2 * statement_idx][1], evaluated_score, ""])

        else:
            for idx in range(len(scenario_idx)):
                CIAS = 0

                for statement_idx in range(0,5):
                    if statement_idx == 0:
                        conversation_file.add_row([scenario_idx[idx], information_types[idx], relationship_and_incentives[idx], statement_idx, responses[5 * idx + statement_idx][0], responses[5 * idx + statement_idx][1], "", ""])
                    else:
                        evaluated_score = assign_score(responses[5 * idx + statement_idx][1])
                        if isinstance(evaluated_score, str) and evaluated_score == "NONE":
                            logger.warning(f"[perform_benchmark.py] For Prompt {idx} Model did not provide a score!")
                        elif isinstance(evaluated_score, str) and evaluated_score != "NONE":
                            logger.warning(f"[perform_benchmark.py] For Prompt {idx} Model did not provide 'single' a score!")
                        elif isinstance(evaluated_score, int):
                            # Note: Variant 3 uses an inverted scale, because of this, here CIAS Calculation has to be inverted!
                            if args.benchmark_variant == 3:
                                CIAS += (5 * (5 - evaluated_score))
                            else:
                                CIAS += (5 * evaluated_score)

                        if statement_idx == 4:
                            conversation_file.add_row([scenario_idx[idx], information_types[idx], relationship_and_incentives[idx], statement_idx, responses[5 * idx + statement_idx][0], responses[5 * idx + statement_idx][1], evaluated_score, CIAS])
                        else:
                            conversation_file.add_row([scenario_idx[idx], information_types[idx], relationship_and_incentives[idx], statement_idx, responses[5 * idx + statement_idx][0], responses[5 * idx + statement_idx][1], evaluated_score, ""])

        logger.info(f"[perform_benchmark.py] Emotionally Intelligent Chatbot Benchmark successfully completed.")