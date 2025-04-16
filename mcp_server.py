from mcp.server.fastmcp import FastMCP
from crypto_client import crypto_client, BigQueryQueryTooLarge, CryptoClient
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID")

mcp = FastMCP()

@mcp.tool()
async def get_latest_transactions(
    wallet_id: str, 
    days: Optional[int] = None, 
    limit: Optional[int] = None
) -> list:
    """Get all the latest USDC transactions for a given wallet address
    Args:
        wallet_id (str): The Ethereum wallet address to query
        days (int, optional): Number of days to look back. Defaults to None.
        limit (int, optional): Maximum number of transactions to return. Defaults to None.
    Returns:
        list: A list of dictionaries containing the transaction details
    Raises:
        BigQueryQueryTooLarge: If the query would process too much data
    """
    try:
        kwargs = {}
        if days is not None:
            kwargs["days"] = days
        if limit is not None:
            kwargs["limit"] = limit
        return await crypto_client.get_usdc_transactions(wallet_id, **kwargs)
    except BigQueryQueryTooLarge as e:
        return {"error": str(e), "suggestion": "Try reducing the time window or using a more specific query"}

@mcp.tool()
async def get_wallet_info(
    wallet_id: str, 
    days: Optional[int] = None, 
    limit: Optional[int] = None
) -> dict:
    """Get basic information about a wallet
    Args:
        wallet_id (str): The Ethereum wallet address to query
        days (int, optional): Number of days to look back. Defaults to None.
        limit (int, optional): Maximum number of transactions to return. Defaults to None.
    Returns:
        dict: A summary of the wallet's information including first seen, total transactions, and contract status
    Raises:
        BigQueryQueryTooLarge: If the query would process too much data
    """
    try:
        kwargs = {}
        if days is not None:
            kwargs["days"] = days
        if limit is not None:
            kwargs["limit"] = limit
        return await crypto_client.get_wallet_info(wallet_id, **kwargs)
    except BigQueryQueryTooLarge as e:
        return {"error": str(e), "suggestion": "Try reducing the time window or using a more specific query"}

@mcp.tool()
async def get_top_tokens(
    wallet_id: str, 
    days: Optional[int] = None, 
    limit: Optional[int] = None
) -> list:
    """Get top tokens by volume for a given wallet
    Args:
        wallet_id (str): The Ethereum wallet address to query
        days (int, optional): Number of days to look back. Defaults to None.
        limit (int, optional): Number of top tokens to return. Defaults to None.
    Returns:
        list: List of top tokens with transaction counts and volumes
    Raises:
        BigQueryQueryTooLarge: If the query would process too much data
    """
    try:
        kwargs = {}
        if days is not None:
            kwargs["days"] = days
        if limit is not None:
            kwargs["limit"] = limit
        return await crypto_client.get_top_tokens(wallet_id, **kwargs)
    except BigQueryQueryTooLarge as e:
        return {"error": str(e), "suggestion": "Try reducing the time window or using a more specific query"}

@mcp.tool()
async def get_eth_transfers(
    wallet_id: str, 
    days: Optional[int] = None, 
    limit: Optional[int] = None
) -> list:
    """Get ETH transfers for a given wallet
    Args:
        wallet_id (str): The Ethereum wallet address to query
        days (int, optional): Number of days to look back. Defaults to None.
        limit (int, optional): Maximum number of transactions to return. Defaults to None.
    Returns:
        list: List of ETH transfers with gas costs and direction
    Raises:
        BigQueryQueryTooLarge: If the query would process too much data
    """
    try:
        kwargs = {}
        if days is not None:
            kwargs["days"] = days
        if limit is not None:
            kwargs["limit"] = limit
        return await crypto_client.get_eth_transfers(wallet_id, **kwrgs)
    except BigQueryQueryTooLarge as e:
        return {"error": str(e), "suggestion": "Try reducing the time window or using a more specific query"}

@mcp.tool()
async def get_sol_transfers(
    wallet_id: str, 
    days: Optional[int] = None, 
    limit: Optional[int] = None
) -> list:
    """Get SOL transfers for a given wallet
    Args:
        wallet_id (str): The Solana wallet address to query
        days (int, optional): Number of days to look back. Defaults to None.
        limit (int, optional): Maximum number of transactions to return. Defaults to None.
    Returns:
        list: List of SOL transfers with transaction details
    Raises:
        BigQueryQueryTooLarge: If the query would process too much data
    """
    try:
        kwargs = {}
        if days is not None:
            kwargs["days"] = days
        if limit is not None:
            kwargs["limit"] = limit
        return await crypto_client.get_sol_transfers(wallet_id, **kwargs)
    except BigQueryQueryTooLarge as e:
        return {"error": str(e), "suggestion": "Try reducing the time window or using a more specific query"}

if __name__ == "__main__":
    mcp.run()