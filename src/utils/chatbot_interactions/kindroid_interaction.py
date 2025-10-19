import requests 

from ..logger import * 

def prompts_kindroid(prompts, character):
    """
    Sends several prompts to kindroid.ai and saves the prompt and response in an array. 

    :param prompts (list[str]): Prompts that should be sended to character.ai. 
    :param character (str): Chosen Kindroid Character. 
    :return (list[list[str,str], list[str,str]]): List of Lists, which contain the prompt as first element and the response as second.
    """
    API_KEY = "kn_fc7f49f5-51dd-4e98-9b1f-a31aeca89985"
 
    if character == "emilia": KIN_ID = "6EqlNGaJY7yjgDB7xoQC"
    if character == "matteo": KIN_ID = "qoUH3bRt3PFPQe6osVuJ" 
    if character == "ms_smith": KIN_ID = "6xc2ofsM88CPNPgdJXbJ"
    if character == "satoru_gojo": KIN_ID = "9wdqrpHiK3blB8ChNYDu"
    if character == "ms_judge": KIN_ID = "l7obLSuZdce5V7vkZG26"

    responses = []
    for idx, prompt in enumerate(prompts, start=1):
        logger.info(f"[utils/chatbot_interactions/kindroid_interaction.py] Start Chatbot Interaction for Prompt {idx}.")
        
        API_URL = "https://api.kindroid.ai/v1/send-message"

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "ai_id": KIN_ID,
            "message": prompt,
        }

        response = requests.post(API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            responses.append([prompt, response.text]) 
            logger.info(f"[utils/chatbot_interactions/kindroid_interaction.py] Chatbot Interaction for Prompt {idx} was successful.")
        else:
            logger.warning(f"[utils/chatbot_interactions/kindroid_interaction.py] Chatbot Interaction for Prompt {idx} failed!")
            responses.append([prompt, "NONE"])

    return responses 