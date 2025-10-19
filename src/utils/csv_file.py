import os
import csv 

from utils.logger import *

class CSVFile:
    def __init__(self, file_path, file_name, columns, load):
        """
        Initialize the CSVFile with file path, file name and column names. 
        :param file_path (str): Directory where the CSV file will be saved.
        :param file_name (str): Name of the CSV file.
        :param columns (list[str]): List of the column names. 
        :param load (bool): Boolean specifying, whether an existing CSV File should be loaded or a new one should be created. 
        """
        self.file_path = file_path
        self.file_name = file_name
        self.columns = columns
        self.rows = []
        self.full_path = os.path.join(self.file_path, self.file_name)

        if load:
            if not os.path.exists(self.full_path):
                logger.error(f"CSV file '{self.full_path}' does not exist!")
            else:
                self.load_from_file()
        else:
            if os.path.exists(self.full_path):
                logger.error(f"CSV file '{self.full_path}' already exists!")
            else:
                self.save_to_file()

    def get_amount_rows(self):
        return len(self.rows)

    def get_full_path(self):
        return self.full_path

    def load_from_file(self):
        """
        Load data from the existing CSV file.
        """
        with open(self.full_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader, None)
            if header != self.columns:
                logger.error(f"[utils/csv_file.py] CSV header does not match expected columns. Found: {header}, Expected: {self.columns}!")
            self.rows = [row for row in reader]

    def get_cell(self, row_index, column_name):
        """
        Get a specific cell value from the CSV file.

        :param row_index (int): Index of the row to retrieve from.
        :param column_name (str): Name of the column whose value is needed.

        :return: int/str: The value of the specified cell.
                 None if the index or column name is invalid.
        """
        if column_name not in self.columns:
            logger.error(f"[utils/csv_file.py] Column Name '{column_name}' does not exist. Available Columns: {self.columns}!")
        if row_index < 0 or row_index >= len(self.rows):
            logger.error(f"[utils/csv_file.py] Row Index {row_index} is out of Range. Valid Range: 0 to {len(self.rows) - 1}!")

        column_index = self.columns.index(column_name)
        
        return self.rows[row_index][column_index]

    def add_row(self, row):
        """
        Add a row to the CSV file.
        :param row (list[int/str]): List of values corresponding to the columns.
        """
        if len(row) != len(self.columns):
            logger.error(f"[utils/csv_file.py] Row Length {len(row)} does not match the Number of Columns {len(self.columns)}!")

        self.rows.append(row)
        self.save_to_file()

    def save_to_file(self):
        """
        Save the current data to the CSV file.
        """
        os.makedirs(self.file_path, exist_ok=True)

        with open(os.path.join(self.file_path, self.file_name), mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(self.columns)
            writer.writerows(self.rows)

def create_benchmark_file(file_path, file_name, tier):
    """
    Creating the Benchmark CSV File with file path, file name and column names. 
    :param file_path (str): Directory where the CSV file will be saved.
    :param file_name (str): Name of the CSV file.
    :param tier (int): Corresponding Benchmark Tier (1,2,3). 
    """
    if tier == 1:
        columns = ["SCENARIO_ID", "INFORMATION_TYPE", "SCENARIO_TEXT", "CHATBOT_RESPONSE", "EVALUATED_SCORE", "CIAS"]
        benchmark_file = CSVFile(file_path, file_name, columns, False)
        logger.info(f"[utils/csv_file.py] Successfully created Tier 1 Benchmark File '{benchmark_file.get_full_path()}'.")
        return benchmark_file

    if tier == 2:
        columns = ["SCENARIO_ID", "INFORMATION_TYPE", "RECIPIENT", "USE", "STATEMENT_ID", "STATEMENT", "CHATBOT_RESPONSE", "EVALUATED_SCORE", "CIAS"] 
        benchmark_file = CSVFile(file_path, file_name, columns, False)        
        logger.info(f"[utils/csv_file.py] Successfully created Tier 2 Benchmark File '{benchmark_file.get_full_path()}'.")
        return benchmark_file
    
    if tier == 3:
        columns = ["SCENARIO_ID", "INFORMATION_TYPE", "RELATIONSHIP_AND_INCENTIVE", "STATEMENT_ID", "STATEMENT", "CHATBOT_RESPONSE", "EVALUATED_SCORE", "CIAS"]
        benchmark_file = CSVFile(file_path, file_name, columns, False) 
        logger.info(f"[utils/csv_file.py] Successfully created Tier 3 Benchmark File '{benchmark_file.get_full_path()}'.")
        return benchmark_file

    logger.error(f"[utils/csv_file.py] Chosen Benchmark Tier does not exist. Chosen: {tier}, Expected: 1,2,3!")

def create_benchmark_results_file(file_path, file_name, tier):
    """
    Creating the Benchmark Results CSV File with file path, file name and column names. 
    :param file_path (str): Directory where the CSV file will be saved.
    :param file_name (str): Name of the CSV file.
    :param tier (int): Corresponding Benchmark Tier (1,2,3). 
    """
    if tier == 1:
        columns = ["SCENARIO_ID", "INFORMATION_TYPE", "VARIANT-1_CIAS", "VARIANT-2_CIAS", "VARIANT-3_CIAS", "AVERAGE_CIAS"]
        benchmark_result_file = CSVFile(file_path, file_name, columns, False)
        logger.info(f"[utils/csv_file.py] Successfully created Tier 1 Benchmark Results File '{benchmark_result_file.get_full_path()}'.")
        return benchmark_result_file

    if tier == 2:
        columns = ["SCENARIO_ID", "INFORMATION_TYPE", "RECIPIENT", "USE", "VARIANT-1_CIAS", "VARIANT-2_CIAS", "VARIANT-3_CIAS", "AVERAGE_CIAS"]
        benchmark_result_file = CSVFile(file_path, file_name, columns, False)
        logger.info(f"[utils/csv_file.py] Successfully created Tier 2 Benchmark Results File '{benchmark_result_file.get_full_path()}'.")
        return benchmark_result_file
    
    if tier == 3:
        columns = ["SCENARIO_ID", "INFORMATION_TYPE", "RELATIONSHIP_AND_INCENTIVE", "VARIANT-1_CIAS", "VARIANT-2_CIAS", "VARIANT-3_CIAS", "AVERAGE_CIAS"]
        benchmark_result_file = CSVFile(file_path, file_name, columns, False)
        logger.info(f"[utils/csv_file.py] Successfully created Tier 3 Benchmark Results File '{benchmark_result_file.get_full_path()}'.")
        return benchmark_result_file

def load_benchmark_file(file_path, file_name, tier):
    """
    Loading the Benchmark CSV File with file path, file name and column names. 
    :param file_path (str): Directory where the CSV file will be saved.
    :param file_name (str): Name of the CSV file.
    :param tier (int): Corresponding Benchmark Tier (1,2,3). 
    """
    if tier == 1:
        columns = ["SCENARIO_ID", "INFORMATION_TYPE", "SCENARIO_TEXT", "CHATBOT_RESPONSE", "EVALUATED_SCORE", "CIAS"]
        benchmark_file = CSVFile(file_path, file_name, columns, True)
        logger.info(f"[utils/csv_file.py] Successfully loaded Tier 1 Benchmark File '{benchmark_file.get_full_path()}'.")
        return benchmark_file

    if tier == 2:
        columns = ["SCENARIO_ID", "INFORMATION_TYPE", "RECIPIENT", "USE", "STATEMENT_ID", "STATEMENT", "CHATBOT_RESPONSE", "EVALUATED_SCORE", "CIAS"] 
        benchmark_file = CSVFile(file_path, file_name, columns, True)        
        logger.info(f"[utils/csv_file.py] Successfully loaded Tier 2 Benchmark File '{benchmark_file.get_full_path()}'.")
        return benchmark_file
    
    if tier == 3:
        columns = ["SCENARIO_ID", "INFORMATION_TYPE", "RELATIONSHIP_AND_INCENTIVE", "STATEMENT_ID", "STATEMENT", "CHATBOT_RESPONSE", "EVALUATED_SCORE", "CIAS"] 
        benchmark_file = CSVFile(file_path, file_name, columns, True) 
        logger.info(f"[utils/csv_file.py] Successfully loaded Tier 3 Benchmark File '{benchmark_file.get_full_path()}'.")
        return benchmark_file

    logger.error(f"[utils/csv_file.py] Chosen Benchmark Tier does not exist. Chosen: {tier}, Expected: 1,2,3!")

def load_benchmark_results_file(file_path, file_name, tier):
    """
    Loading the Benchmark CSV Results File with file path, file name and column names.
    :param file_path (str): Directory where the CSV file will be saved.
    :param file_name (str): Name of the CSV file.
    :param tier (int): Corresponding Benchmark Tier (1,2,3). 
    :param human (bool): Whether the Human Baseline should be loaded or not. 
    """
    if tier == 1:
        columns = ["SCENARIO_ID", "INFORMATION_TYPE", "CIAS"]
        human_result_file = CSVFile(file_path, file_name, columns, True)
        logger.info(f"[utils/csv_file.py] Successfully loaded Tier 1 Human Results File '{human_result_file.get_full_path()}'.")
        return human_result_file
        
    if tier == 2: 
        columns = ["SCENARIO_ID", "INFORMATION_TYPE", "RECIPIENT", "USE", "CIAS"]
        human_result_file = CSVFile(file_path, file_name, columns, True)
        logger.info(f"[utils/csv_file.py] Successfully loaded Tier 2 Human Results File '{human_result_file.get_full_path()}'.")
        return human_result_file
        
    if tier == 3: 
        columns = ["SCENARIO_ID", "INFORMATION_TYPE", "RELATIONSHIP_AND_INCENTIVE", "CIAS"]
        human_result_file = CSVFile(file_path, file_name, columns, True)
        logger.info(f"[utils/csv_file.py] Successfully loaded Tier 3 Human Results File '{human_result_file.get_full_path()}'.")
        return human_result_file