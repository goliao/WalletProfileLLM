from google.cloud import bigquery
import json
import os
from dotenv import load_dotenv

load_dotenv()

def query_bigquery_to_json(query, project_id=None):
    """
    Execute a BigQuery query and return results as JSON.
    
    Args:
        query (str): The SQL query to execute
        project_id (str, optional): The GCP project ID. If None, will use default project.
    
    Returns:
        list: List of dictionaries containing query results
    """
    try:
        # Initialize the BigQuery client
        client = bigquery.Client(project=project_id)
        
        # Execute the query
        query_job = client.query(query)
        
        # Convert results to a list of dictionaries
        results = []
        for row in query_job:
            # Convert row to dictionary
            row_dict = dict(row.items())
            results.append(row_dict)
        
        return results
    
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        if "Access Denied" in str(e):
            print("\nPermission Error: You need to:")
            print("1. Make sure you have the 'BigQuery User' role in your project")
            print("2. Go to IAM & Admin in Google Cloud Console")
            print("3. Add your account with the 'BigQuery User' role")
        raise

def save_results_to_file(results, output_file):
    """
    Save query results to a JSON file.
    
    Args:
        results (list): List of dictionaries containing query results
        output_file (str): Path to output JSON file
    """
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving results to file: {str(e)}")
        raise

if __name__ == "__main__":
    # Exact query from table explorer
    query = """
    SELECT
      *
    FROM
      `bigquery-public-data.crypto_ethereum.transactions`
    LIMIT 10
    """
    
    # Use your project ID to run the query
    project_id = os.getenv("PROJECT_ID")
    
    try:
        print("Executing query...")
        # Execute query and get results
        results = query_bigquery_to_json(query, project_id)
        
        # Print results to console
        print("\nQuery results:")
        print(json.dumps(results, indent=2))
        
        # Save results to file
        save_results_to_file(results, "ethereum_transactions.json")
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}") 