from utils.argparser import *
from utils.logger import *
from utils.csv_file import *

import os
import inflect
import numpy as np
import spacy

from keybert import KeyBERT
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sentence_transformers import SentenceTransformer

AMOUNT_TIERS = 3
AMOUNT_VARIANTS = 3

if __name__ == "__main__":   
    args = perform_keyword_extraction() 

    if args.task == "extract-character-keywords":
        logger.info(f"[perform_keyword_extraction.py] Initializing Character Keyword Extraction.")

        kw_model = KeyBERT("all-MiniLM-L6-v2")
        nlp = spacy.load("en_core_web_sm")

        # Establish Paths and File Names
        if not args.enhancement_method_enabled:
            path_conversations = f"conversations/{args.benchmark_bot}/{args.benchmark_character}"
            path_keywords = f"keywords/{args.benchmark_bot}"
            file_name_keywords = f"keywords_{args.benchmark_bot}_{args.benchmark_character}.csv"
        else:
            path_conversations = f"conversations/{args.benchmark_bot}/{args.enhancement_method}"
            path_keywords = f"keywords/{args.benchmark_bot}"
            file_name_keywords = f"keywords_{args.benchmark_bot}_{args.enhancement_method}.csv"

        # Parse Benchmark Files and obtain Chatbot Responses
        chatbot_responses = []

        for tier in range(1, AMOUNT_TIERS + 1):
            for variant in range(1, AMOUNT_VARIANTS + 1):
                if not args.enhancement_method_enabled:
                    file_name_conversation = f"{args.benchmark_bot}_{args.benchmark_character}_tier_{tier}_variant_{variant}_conversation.csv"
                else:
                    file_name_conversation = f"{args.benchmark_bot}_{args.enhancement_method}_tier_{tier}_variant_{variant}_conversation.csv"

                conversation_file = load_benchmark_file(path_conversations, file_name_conversation, tier)
                amount_rows = conversation_file.get_amount_rows()

                for index in range(amount_rows):
                    chatbot_responses.append(conversation_file.get_cell(index, "CHATBOT_RESPONSE"))

        # Create Keyword File and obtain Keywords
        keyword_file = CSVFile(path_keywords, file_name_keywords, ["CHATBOT_RESPONSE", "KEYWORDS"], False)

        for response in chatbot_responses:
            keywords = kw_model.extract_keywords(response, top_n=15)
    
            extracted_keywords = [
                label for (label, score) in keywords
                if any(token.pos_ in "NOUN" for token in nlp(label))
            ]

            keywords_string = ', '.join(extracted_keywords)
            keyword_file.add_row([response, keywords_string])

        logger.info(f"[perform_keyword_extraction.py] Character Keyword Extraction successfully completed.")
    else:
        logger.info(f"[perform_keyword_extraction.py] Start Chatbot Keywords Summary.")

        p = inflect.engine()

        keyword_count = {}
        unique_keyword_count = {}
        
        # Establish Paths and File Names 
        path_keywords = f"keywords/{args.benchmark_bot}"
        file_name_summary = f"summary_keywords_{args.benchmark_bot}.csv"
        file_name_summary_trends = f"summary_keywords_{args.benchmark_bot}_top10_trends.csv"

        file_names = [f"keywords_{args.benchmark_bot}_emilia.csv",
                 f"keywords_{args.benchmark_bot}_matteo.csv",
                 f"keywords_{args.benchmark_bot}_ms_smith.csv",
                 f"keywords_{args.benchmark_bot}_satoru_gojo.csv",
                 f"keywords_{args.benchmark_bot}_cot.csv",
                 f"keywords_{args.benchmark_bot}_self-defense.csv",
                 f"keywords_{args.benchmark_bot}_self-defense-proxy.csv"]

        for file_name in file_names:
            current_CSV = CSVFile(path_keywords, file_name, ["CHATBOT_RESPONSE", "KEYWORDS"], True)
            amount_rows = current_CSV.get_amount_rows()
            
            for index in range(amount_rows):
                current_keyword_string = current_CSV.get_cell(index, "KEYWORDS")
                current_keywords = [keyword.strip() for keyword in current_keyword_string.split(',')]
                current_keywords = list(set(current_keywords))
                
                for keyword in current_keywords:
                    if keyword == "":
                        continue
                    
                    if keyword in keyword_count:
                        keyword_count[keyword] += 1
                    else:
                        keyword_count[keyword] = 1 

        filtered_keyword_count = {k: v for k, v in keyword_count.items() if v >= 20} # Removing Noise
        sorted_keyword_count = dict(sorted(filtered_keyword_count.items(), key=lambda item: item[1], reverse=True))

        # Filter Forbidden Keywords from Keywords Count
        forbidden_keywords_file = CSVFile("utils", "forbidden_keywords.csv", ["FORBIDDEN_KEYWORDS"], True)
        
        for index in range(forbidden_keywords_file.get_amount_rows()):
            forbidden_keyword = forbidden_keywords_file.get_cell(index, "FORBIDDEN_KEYWORDS")

            if forbidden_keyword in sorted_keyword_count:
                sorted_keyword_count.pop(forbidden_keyword, None)

            if p.plural(forbidden_keyword) in sorted_keyword_count:
                sorted_keyword_count.pop(p.plural(forbidden_keyword), None)

        logger.info(f"[perform_keyword_extraction.py] Filtering Forbidden Keywords completed successfully.")

        file_summary = CSVFile(path_keywords, file_name_summary, ["KEYWORD", "FREQUENCY"], False)

        for key, value in sorted_keyword_count.items():
            file_summary.add_row([key, value])

        logger.info(f"[perform_keyword_extraction.py] Successfully created Chatbot Keyword Summary File.")

        # Perform K-Means Clustering
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        
        data = sorted_keyword_count
        keys = list(data.keys())
        weights = np.array([data[key] for key in keys])

        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(keys)
        weighted_embeddings = np.repeat(embeddings, weights, axis=0)
        kmeans = KMeans(n_clusters=10, random_state=0)
        labels = kmeans.fit_predict(weighted_embeddings)

        cluster_dict = {}
        for key, weight in zip(keys, weights):
            idx = keys.index(key)
            label = labels[np.where(weighted_embeddings == embeddings[idx])[0][0]]
            cluster_dict.setdefault(label, []).append((key, weight))

        cluster_summary = {}
        for label, items in cluster_dict.items():
            items_sorted = sorted(items, key=lambda x: x[1], reverse=True)
            top_keywords = [item[0] for item in items_sorted[:5]]
            cluster_label = '_'.join(top_keywords)
            
            total_weight = sum(weight for _, weight in items)
            cluster_summary[cluster_label] = {
                'total_weight': total_weight,
                'items': items_sorted
            }

        sorted_cluster_summary = dict(sorted(cluster_summary.items(), key=lambda x: x[1]['total_weight'], reverse=True))
        file_summary_trends = CSVFile(path_keywords, file_name_summary_trends, ["TREND", "CLUSTER_SIZE / FREQUENCY"], False)

        for key, value in sorted_cluster_summary.items():
            file_summary_trends.add_row([key,  value['total_weight']])
        
        logger.info(f"[perform_keyword_extraction.py] Successfully extracted Chatbot Response Trends.")
        logger.info(f"[perform_keyword_extraction.py] Chatbot Keyword Summary successfully completed.")