import urllib.request
import json

from ..logger import *

def prompts_nomi_ai(prompts, character):
    """
    Sends several prompts to nomi.ai and saves the prompt and response in an array. 

    :param prompts (list[str]): Prompts that should be sended to character.ai. 
    :param character (str): Chosen Nomi Character. 
    :return (list[list[str,str], list[str,str]]): List of Lists, which contain the prompt as first element and the response as second.
    """
    API_KEY = "457b2bce-ead8-416e-afe4-0fa4c942b875"
    
    if character == "emilia": NOMI_UUID = "d4fbd60a-e304-416d-8f87-f65321ac4590"
    if character == "matteo": NOMI_UUID = "d1b9cbbe-8838-40a0-99ac-ce0c01bb812b"
    if character == "ms_smith": NOMI_UUID = "82422cfe-8052-4110-9151-0ef77d766eb9"  
    if character == "satoru_gojo": NOMI_UUID = "c4f6d373-14f9-42e1-9c15-8af876e5e1ca"
    if character == "ms_judge": NOMI_UUID = "d14d8bc1-1a43-426b-b032-370fbdeeac0c"
    
    responses = []
    
    for idx, prompt in enumerate(prompts, start=1):
        logger.info(f"[utils/chatbot_interactions/nomi_ai_interaction.py] Start Chatbot Interaction for Prompt {idx}.")
        
        url = f"https://api.nomi.ai/v1/nomis/{NOMI_UUID}/chat"

        data = json.dumps({"messageText": prompt}).encode("utf-8")

        headers = {
            "Authorization": API_KEY,
            "Content-Type": "application/json",
        }

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req) as response:
                response_data = json.loads(response.read().decode())
                responses.append([prompt, response_data["replyMessage"]["text"]]) 
                logger.info(f"[utils/chatbot_interactions/nomi_ai_interaction.py] Chatbot Interaction for Prompt {idx} was successful.")

        except Exception as e:
            logger.warning(f"[utils/chatbot_interactions/nomi_ai_interaction.py] Chatbot Interaction for Prompt {idx} failed!")
            responses.append([prompt, "NONE"])

    return responses 