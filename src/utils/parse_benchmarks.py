import re 

def parse_user_context(path_user_context):
    """
    Parses the user context, in this case of the user 'Luis Santos'.

    :param path_user_context: Path of the user context. 
    :return (list[str, str]): User Context, which is defined by two Prompts. 
    """ 
    user_context = []
    
    with open(path_user_context, 'r') as file:
        lines = [str(line.strip()) for line in file] 

        for prompt_index in range(1, 3):
            start_prompt = f"<PROMPT-{prompt_index}>"
            end_prompt = f"</PROMPT-{prompt_index}>"

            for index in range(1, len(lines)-1):
                if lines[index - 1] == start_prompt and lines[index + 2] == end_prompt:
                    user_context.append(lines[index] + "\n\n" + lines[index + 1])

    return user_context 

def parse_benchmark_tier_1(path_tier_1_eval, path_tier_1, variant):
    """
    Parses the established baseline of contextual integrity acceptance scores from the user study for the given scenarios.

    :param path_tier_1_eval (str): Path of the evaluation task for Tier 1 benchmarks. 
    :param path_tier_1 (str): Path of the Tier 1 scenarios.
    :param variant (int): Tested variant of scenario/evaluation task formulation. 
    :return (list[list[int, str, str], list[list[int, str, str]]):
        - int: ID of the scenario
        - str: Information Type examined in the scenario
        - str: Prompt of the scenario with evaluation task 
    """
    start_scenario = "<SCENARIO"
    end_scenario = "</SCENARIO>"
    start_variant = f"<VARIANT-{variant}>"
    end_variant = f"</VARIANT-{variant}>"
    
    tier_1_benchmark = []
    eval_task = ""

    with open(path_tier_1_eval, 'r') as file: 
        lines = [str(line.strip()) for line in file] 
        
        for index in range(1, len(lines) - 1):
            if lines[index - 1] == start_variant and lines[index + 1] == end_variant:
                eval_task = lines[index]
                break 

    with open(path_tier_1, 'r') as file: 
        scenarios = []
        start_scenario_indices = []
        end_scenario_indices = []
        
        lines = [str(line.strip()) for line in file] 
        
        for index in range(0, len(lines)):
            if start_scenario in lines[index]:
                start_scenario_indices.append(index)
            
            if lines[index] == end_scenario:
                end_scenario_indices.append(index)

        for index in range(0, len(start_scenario_indices)):
            scenarios.append(lines[start_scenario_indices[index]:end_scenario_indices[index]])

        for scenario in scenarios: 
            scenario_text = ""
            pattern = r'ID="(\d+)"\s+INFORMATION-TYPE="([^"]+)"'

            match = re.search(pattern, scenario[0])
            scenario_id = match.group(1)
            information_type = match.group(2)

            for index in range(1, len(scenario)-1):
                if scenario[index - 1] == start_variant and scenario[index + 1] == end_variant:
                    scenario_text = scenario[index] + "\n\n" + eval_task
                    break 

            tier_1_benchmark.append([scenario_id, information_type, scenario_text])

    return tier_1_benchmark 


def parse_benchmark_tier_2_or_3(path_tier_2_or_3_eval, path_tier_2_or_3, variant, tier):
    """
    Parses the established baseline of contextual integrity acceptance scores from the user study for the given scenarios.

    :param path_tier_2_or_3_eval (str): Path of the evaluation tasks for Tier 2/3 benchmarks. 
    :param path_tier_2_or_3 (str): Path of the Tier 2/3 scenarios.
    :param variant (int): Tested variant of scenario/evaluation task formulation. 
    :param tier (int): Tier of Benchmarks 
    :return (list[list[int, str, str, str, str, str, str, str], list[int, str, str, str, str, str, str, str]]):
        - int: ID of the scenario
        - str: Information Type examined in the scenario (Tier 2 & 3)
        - str: Recipient examined in the scenario (Tier 2) or Relationship and Incentive (Tier 3)
        - str: Use Case examined in the scenario (Tier 2) or "NULL" 
        - str: First Prompt of the scenario (scenario + evaluation task + statement 1)
        - str: Second Prompt of the scenario (statement 2)
        - str: Third Prompt of the scenario (statement 3)
        - str: Fourth Prompt of the scenario (statement 4)
    """
    start_scenario = "<SCENARIO"
    end_scenario = "</SCENARIO>"
    start_variant = f"<VARIANT-{variant}>"
    end_variant = f"</VARIANT-{variant}>"
    
    tier_2_or_3_benchmark = []
    eval_tasks = []

    with open(path_tier_2_or_3_eval, 'r') as file: 
        start_variant_index = 0
        end_variant_index = 0 
        
        lines = [str(line.strip()) for line in file] 

        for index in range(0, len(lines)):
            if lines[index] == start_variant:
                start_variant_index = index 
            if lines[index] == end_variant:
                end_variant_index = index 

        current_variant = lines[start_variant_index:end_variant_index]

        for prompt_index in range(0, 5):
            start_prompt = f"<PROMPT-{prompt_index}>"
            end_prompt = f"</PROMPT-{prompt_index}>"

            for index in range(1, len(current_variant)-1):
                if prompt_index == 1:
                    if current_variant[index - 1] == start_prompt and current_variant[index + 2] == end_prompt:
                        eval_tasks.append(current_variant[index] + "\n\n" + current_variant[index + 1])
                else:
                    if current_variant[index - 1] == start_prompt and current_variant[index + 1] == end_prompt:
                        eval_tasks.append(current_variant[index])

    with open(path_tier_2_or_3, 'r') as file: 
        scenarios = []
        start_scenario_indices = []
        end_scenario_indices = []
        
        lines = [str(line.strip()) for line in file] 
        
        for index in range(0, len(lines)):
            if start_scenario in lines[index]:
                start_scenario_indices.append(index)
            
            if lines[index] == end_scenario:
                end_scenario_indices.append(index)

        for index in range(0, len(start_scenario_indices)):
            scenarios.append(lines[start_scenario_indices[index]:end_scenario_indices[index]])

        for scenario in scenarios: 
            backup_eval_tasks = eval_tasks.copy()
            
            if tier == 2: 
                pattern = r'<SCENARIO\s+ID="(?P<id>[^"]+)"\s+INFORMATION-TYPE="(?P<information_type>[^"]+)"\s+RECIPIENT="(?P<recipient>[^"]+)"\s+USE="(?P<use>[^"]+)"'
                match = re.search(pattern, scenario[0])
                scenario_id = match.group('id') 
                information_type = match.group('information_type')
                recipient = match.group('recipient')
                use = match.group('use')
                metadata = [scenario_id, information_type, recipient, use]
            if tier == 3: 
                pattern = r'<SCENARIO\s+ID="(?P<id>[^"]+)"\s+INFORMATION-TYPE="(?P<information_type>[^"]+)"\s+RELATIONSHIP-AND-INCENTIVE="(?P<relationship_and_incentive>[^"]+)"'
                match = re.search(pattern, scenario[0])
                scenario_id = match.group('id') 
                information_type = match.group('information_type')
                relationship_and_incentive = match.group('relationship_and_incentive')
                metadata = [scenario_id, information_type, relationship_and_incentive, "NULL"]

            for index in range(1, len(scenario)-1):
                if scenario[index - 1] == start_variant and scenario[index + 1] == end_variant:
                    backup_eval_tasks[0] = scenario[index] + "\n\n" + eval_tasks[0]
                    break
            
            tier_2_or_3_benchmark.append(metadata + backup_eval_tasks)

    return tier_2_or_3_benchmark