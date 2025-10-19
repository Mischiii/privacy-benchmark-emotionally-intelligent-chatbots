# Steps Before Starting the Script:
# 1. Start Google Chrome with Remote Debugging:
#       /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome-debug" (on Mac)
# 2. Open the Chat Page you want to interact with and close all other Tabs!
# Once the page is open and the chatbot is visible, you can run this script. 

from playwright.sync_api import sync_playwright
import time

from ..logger import * 

def prompts_character_ai(prompts):
    """
    Sends several prompts to character.ai and saves the prompt and response in an array. 

    :param prompts (list[str]): Prompts that should be sended to character.ai. 
    :return (list[list[str,str], list[str,str]]): List of Lists, which contain the prompt as first element and the response as second.
    """
    responses = []

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        default_context = browser.contexts[0]
        page = default_context.pages[0]

        page.wait_for_selector("textarea", timeout=10000)

        # Select Bot Response DIV 
        character_selector = 'div[data-testid="completed-message"].bg-surface-elevation-2'

        for idx, prompt in enumerate(prompts, start=1):
            logger.info(f"[utils/chatbot_interactions/character_ai_interaction.py] Start Chatbot Interaction for Prompt {idx}.")

            initial_count = page.locator(character_selector).count()
                
            page.fill("textarea", prompt)
            page.press("textarea", "Enter")
            time.sleep(25)

            all_responses = page.locator(character_selector).all_text_contents()
            
            if len(all_responses) > initial_count:
                # On character.ai the first message in the DOM is the newest
                response = all_responses[0].strip()
                responses.append([prompt, response])
                logger.info(f"[utils/chatbot_interactions/character_ai_interaction.py] Chatbot Interaction for Prompt {idx} was successful.")
            else:
                logger.warning(f"[utils/chatbot_interactions/character_ai_interaction.py] Chatbot Interaction for Prompt {idx} failed!")
                responses.append([prompt, "NONE"])

            time.sleep(5)

    return responses