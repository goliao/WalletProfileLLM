from bigquery_client import bigquery_client, BigQueryQueryTooLarge
from crypto_queries import CryptoQueries
from typing import List, Dict, Any, Optional
from datetime import datetime

class CryptoClient:
    # Class constants for default values
    DEFAULT_DAYS_TO_LOOK_BACK = 100
    DEFAULT_TRANSACTION_LIMIT = 100
    MAX_DAYS_TO_LOOK_BACK = 500
    MAX_TRANSACTION_LIMIT = 500

    def __init__(self):
        self.days_to_look_back = self.DEFAULT_DAYS_TO_LOOK_BACK
        self.transaction_limit = self.DEFAULT_TRANSACTION_LIMIT

    def _validate_limits(self, days: int, limit: int) -> tuple[int, int]:
        """
        Validate and cap the days and limit parameters to their maximum values.
        
        Args:
            days (int): Number of days to look back
            limit (int): Maximum number of transactions
            
        Returns:
            tuple[int, int]: Validated days and limit values
        """
        return (
            min(days, self.MAX_DAYS_TO_LOOK_BACK),
            min(limit, self.MAX_TRANSACTION_LIMIT)
        )

    async def _execute_safe_query(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """
        Execute a query with size checking and error handling.
        
        Args:
            query (str): The SQL query to execute
            
        Returns:
            Optional[List[Dict[str, Any]]]: Query results or None if query is too large
            
        Raises:
            BigQueryQueryTooLarge: If the query would process too much data
        """
        try:
            return await bigquery_client.execute_query(query)
        except BigQueryQueryTooLarge as e:
            print(f"Warning: {str(e)}")
            raise

    async def get_usdc_transactions(self, wallet_id: str, days: int = DEFAULT_DAYS_TO_LOOK_BACK, limit: int = DEFAULT_TRANSACTION_LIMIT) -> List[Dict[str, Any]]:
        """
        Get USDC token transfers for a given wallet address.
        
        Args:
            wallet_id (str): The Ethereum wallet address to query
            days (int, optional): Number of days to look back. Defaults to DEFAULT_DAYS_TO_LOOK_BACK.
            limit (int, optional): Maximum number of transactions to return. Defaults to DEFAULT_TRANSACTION_LIMIT.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing transaction details
            
        Raises:
            BigQueryQueryTooLarge: If the query would process too much data
        """
        days, limit = self._validate_limits(days, limit)
        query = CryptoQueries.format_query(CryptoQueries.USDC_TRANSACTIONS,
            token_address=CryptoQueries.USDC_TOKEN_ADDRESS,
            wallet_id=wallet_id,
            days=days,
            limit=limit
        )
        
        transactions = await self._execute_safe_query(query)
        return transactions

    async def get_eth_transfers(self, wallet_id: str, days: int = DEFAULT_DAYS_TO_LOOK_BACK, limit: int = DEFAULT_TRANSACTION_LIMIT) -> List[Dict[str, Any]]:
        """
        Get ETH transfers for a given wallet address.
        
        Args:
            wallet_id (str): The Ethereum wallet address to query
            days (int, optional): Number of days to look back. Defaults to DEFAULT_DAYS_TO_LOOK_BACK.
            limit (int, optional): Maximum number of transactions to return. Defaults to DEFAULT_TRANSACTION_LIMIT.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing ETH transfer details
            
        Raises:
            BigQueryQueryTooLarge: If the query would process too much data
        """
        days, limit = self._validate_limits(days, limit)
        query = CryptoQueries.format_query(CryptoQueries.ETH_TRANSFERS,
            wallet_id=wallet_id,
            days=days,
            limit=limit
        )
        
        transfers = await self._execute_safe_query(query)            
        return transfers

    async def get_top_tokens(self, wallet_id: str, days: int = DEFAULT_DAYS_TO_LOOK_BACK, limit: int = DEFAULT_TRANSACTION_LIMIT) -> List[Dict[str, Any]]:
        """
        Get top tokens by volume for a given wallet.
        
        Args:
            wallet_id (str): The Ethereum wallet address to query
            days (int, optional): Number of days to look back. Defaults to DEFAULT_DAYS_TO_LOOK_BACK.
            limit (int, optional): Number of top tokens to return. Defaults to DEFAULT_TRANSACTION_LIMIT.

        Returns:
            List[Dict[str, Any]]: List of top tokens with transaction counts and volumes
            
        Raises:
            BigQueryQueryTooLarge: If the query would process too much data
        """
        days, limit = self._validate_limits(days, limit)
        query = CryptoQueries.format_query(CryptoQueries.TOP_TOKENS,
            wallet_id=wallet_id,
            days=days,
            limit=limit
        )
        
        return await self._execute_safe_query(query)

    async def get_sol_transfers(self, wallet_id: str, days: int = 10, limit: int = DEFAULT_TRANSACTION_LIMIT) -> List[Dict[str, Any]]:
        """
        Get SOL transfers for a given wallet address.
        
        Args:
            wallet_id (str): The Ethereum wallet address to query
            days (int, optional): Number of days to look back. Defaults to DEFAULT_DAYS_TO_LOOK_BACK.
            limit (int, optional): Maximum number of transactions to return. Defaults to DEFAULT_TRANSACTION_LIMIT.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing SOL transfer details
            
        Raises:
            BigQueryQueryTooLarge: If the query would process too much data
        """
        days, limit = self._validate_limits(days, limit)
        query = CryptoQueries.format_query(CryptoQueries.SOL_TRANSFERS,
            wallet_id=wallet_id,
            days=days,
            limit=limit
        )
        return await self._execute_safe_query(query)

    async def get_wallet_info(self, wallet_id: str, days: int = DEFAULT_DAYS_TO_LOOK_BACK, limit: int = DEFAULT_TRANSACTION_LIMIT) -> Dict[str, Any]:
        """
        Get basic information about a wallet.
        
        Args:
            wallet_id (str): The Ethereum wallet address
            days (int, optional): Number of days to look back. Defaults to DEFAULT_DAYS_TO_LOOK_BACK.
            limit (int, optional): Maximum number of transactions to return. Defaults to DEFAULT_TRANSACTION_LIMIT.
            
        Returns:
            Dict[str, Any]: Dictionary containing wallet information including:
                - first_seen: First transaction timestamp
                - total_transactions: Total number of transactions
                - is_contract: Whether the address is a contract
        """
        days, limit = self._validate_limits(days, limit)
        query = CryptoQueries.format_query(CryptoQueries.WALLET_INFO,
            wallet_id=wallet_id,
            days=days,
            limit=limit
        )
        result = await self._execute_safe_query(query)
        return result[0] if result else {
            'first_seen': None,
            'total_transactions': 0,
            'is_contract': False
        }

# Create a singleton instance
crypto_client = CryptoClient() 