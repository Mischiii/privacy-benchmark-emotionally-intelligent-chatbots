import ollama
import re

from utils.logger import *

class LlamaModel:
    def __init__(self, model_name="llama3.2:3b"):
        """
        Initializes the Llama Model instance with a default or specified model name.

        :param model_name (str): The name of the Llama model to use (default is "llama3.2:3b").
        """
        self.model_name = model_name

    def get_response(self, prompt):
        """
        Sends a prompt to the Llama model and retrieves the response.

        :param prompt (str): The input text prompt to send to the model.
        :return (str): The response from the model.
        """
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response["message"]["content"]
        except Exception as e:
            logger.warning(f"[utils/prompt_analysis.py] Error while querying Llama: {str(e)}")
            return "NONE"

def assign_score(prompt):
    possible_scores = re.findall(r'\d+', prompt)
    if len(possible_scores) == 1:
        logger.info("[utils/prompt_analysis.py] Automated Score Extraction was successful and used Regex Extraction.")
        return int(possible_scores[0])

    model = LlamaModel()
    question = (
        f"Consider the following answer: {prompt} - "
        f"This prompt contains the following mentioned numbers: {possible_scores} - "
        "Please give me the final assigned score as numerical value, read the scenario very carefully!"
    )
    
    response = model.get_response(question)
    model_scores = re.findall(r'\d+', response) if response and response != "NONE" else []

    if model_scores:
        logger.info("[utils/prompt_analysis.py] Automated Score Extraction was successful and used Llama3.2:3b.")
        return int(model_scores[0])
    elif possible_scores:
        logger.warning("[utils/prompt_analysis.py] Automated Score Extraction was failed!")
        return ','.join([f'"{item}"' for item in possible_scores])
    else:
        logger.warning("[utils/prompt_analysis.py] No numerical score found in prompt!")
        return "NONE"