from google.cloud import bigquery
import json
import os
from dotenv import load_dotenv
from decimal import Decimal
from datetime import datetime

load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID")

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
            
            # Convert non-JSON-serializable values
            for key, value in row_dict.items():
                if isinstance(value, Decimal):
                    row_dict[key] = float(value)
                elif isinstance(value, datetime):
                    row_dict[key] = value.isoformat()
            
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

def get_transactions_from_bigquery(wallet_id):
    """
    Get USDC token transfers for a given wallet address.
    
    Args:
        wallet_id (str): The Ethereum wallet address to query

    Returns:
        list: List of dictionaries containing query results
    """
    client = bigquery.Client(project=PROJECT_ID)
    query = f"""
            SELECT 
            block_timestamp,
            from_address,
            to_address,
            token_address,
            value,
            transaction_hash
            FROM 
            bigquery-public-data.crypto_ethereum.token_transfers
            WHERE 
            token_address = LOWER('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48')  -- USDC
            AND (
                from_address = '{wallet_id}' 
                OR to_address = '{wallet_id}'
            )
            AND block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 100 DAY)
            ORDER BY 
            block_timestamp DESC
            LIMIT 100;
    """
    query_job = client.query(query)
    
    # Convert results to list of dictionaries
    transactions = []
    for row in query_job:
        transactions.append(dict(row.items()))
    
    # Print results in a readable format
    print("\nRecent USDC Transactions (Last 100 days):")
    print("-" * 80)
    for tx in transactions:
        # Convert value from base units to USDC (6 decimals)
        usdc_value = float(tx['value']) / 1e6
        print(f"Transaction Hash: {tx['transaction_hash']}")
        print(f"From: {tx['from_address']}")
        print(f"To: {tx['to_address']}")
        print(f"Value: {usdc_value:.2f} USDC")
        print(f"Timestamp: {tx['block_timestamp']}")
        print("-" * 80)
    
    return transactions

