import numpy as np 
from pysentimiento import create_analyzer

from utils.logger import *
from utils.csv_file import * 

class PYSentimiento:
    def __init__(self, file_path, file_name):
        """
        Initialize the CSVFile with file path, file name and column names for the PYSentimiento Analysis.
        :param file_path (str): Directory where the CSV file will be saved.
        :param file_name (str): Name of the CSV file.
        """
        self.columns = ["RESPONSE", "POLARITY_PROB", "POLARITY", "EMOTION_PROB", "EMOTION", "IRONY_PROB", "IRONY"]
        self.csv_file = CSVFile(file_path, file_name, self.columns, False)

    
    def calculate_averages(self, all_rows):
        def extract_probabilities(rows, index):
            return [row[index] for row in rows]

        def average_probas(probas_list):
            keys = probas_list[0].keys()
            arr = np.array([[p[k] for k in keys] for p in probas_list])
            return {k: np.mean(arr[:,i]) for i, k in enumerate(keys)}
        
        def get_dominant(probas_dict):
            return max(probas_dict.items(), key=lambda x: x[1])[0]

        sentiment_probas = extract_probabilities(all_rows, 1)
        emotion_probas = extract_probabilities(all_rows, 3)
        irony_probas = extract_probabilities(all_rows, 5)

        avg_sentiment = average_probas(sentiment_probas)
        avg_emotion = average_probas(emotion_probas)
        avg_irony = average_probas(irony_probas)
        
        return [
            avg_sentiment, get_dominant(avg_sentiment),
            avg_emotion, get_dominant(avg_emotion),
            avg_irony, get_dominant(avg_irony)
        ]


    def perform_analysis(self, statements):
        """
        Performs Sentiment, Emotion and Irony Analysis and saves it in the CSVFile. 
        :param statements (list[str]): List of Statements, that should be analyzed
        """
        logger.info(f"[utils/sentiment_analysis.py] Initializing PYSentimiento Analsis.")
        
        sentiment_analyzer = create_analyzer(task="sentiment", lang="en")
        emotion_analyzer = create_analyzer(task="emotion", lang="en")
        irony_analyzer = create_analyzer(task="irony", lang="en")

        all_rows = []

        for idx, statement in enumerate(statements, start=1):
            try:
                current_row = []
                current_row.append(statement)

                result_sentiment = sentiment_analyzer.predict(statement)
                current_row.append(result_sentiment.probas)
                current_row.append(result_sentiment.output)

                result_emotion = emotion_analyzer.predict(statement)
                current_row.append(result_emotion.probas)
                current_row.append(result_emotion.output)

                result_irony = irony_analyzer.predict(statement)
                current_row.append(result_irony.probas)
                current_row.append(result_irony.output)

                self.csv_file.add_row(current_row)
                all_rows.append(current_row)
            except Exception as e:
                logger.error(f"[utils/sentiment_analysis.py] Error occurred during PYSentimiento Analysis: {str(e)}!")

        average = self.calculate_averages(all_rows)
        average = ["AVERAGE RESPONSE"] + average
        self.csv_file.add_row(average)

        logger.info(f"[utils/sentiment_analysis.py] Completed PYSentimiento Analysis!")