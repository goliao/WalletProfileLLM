from mcp.server.fastmcp import FastMCP
from google.cloud import bigquery
import json
import os
from dotenv import load_dotenv
from decimal import Decimal
from datetime import datetime

load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID")

mcp = FastMCP()

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

@mcp.tool()
def get_latest_transactions(wallet_id: str) -> list:
    """Get all the latest transactions for a given wallet address
    Args:
        wallet_id (str): The Ethereum wallet address to query
    Returns:
        list: A list of dictionaries containing the transaction details
    """
    return get_transactions_from_bigquery(wallet_id)

if __name__ == "__main__":
    mcp.run()