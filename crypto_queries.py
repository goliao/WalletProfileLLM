from typing import Dict

class CryptoQueries:
    # USDC token address
    USDC_TOKEN_ADDRESS = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"

    # Base query template for USDC transactions
    USDC_TRANSACTIONS = """
        SELECT 
            block_timestamp,
            from_address,
            to_address,
            token_address,
            CAST(value AS NUMERIC) / 1e6 as value_eth,  -- Convert to USDC
            transaction_hash
        FROM 
            bigquery-public-data.crypto_ethereum.token_transfers
        WHERE 
            token_address = LOWER('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48')  -- USDC
            AND (
                from_address = '{wallet_id}' 
                OR to_address = '{wallet_id}'
            )
            AND block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        ORDER BY 
            block_timestamp DESC
        LIMIT {limit};
    """

    # Query for ETH transfers
    ETH_TRANSFERS = """
        SELECT 
            block_timestamp,
            from_address,
            to_address,
            value / 1e18 as value_eth,  -- Convert from Wei to ETH
            `hash`,
            gas_price / 1e9 as gas_price_gwei,  -- Convert from Wei to Gwei
            receipt_gas_used as gas_used
        FROM 
            bigquery-public-data.crypto_ethereum.transactions
        WHERE 
            (
                from_address = '{wallet_id}' 
                OR to_address = '{wallet_id}'
            )
            AND block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        ORDER BY 
            block_timestamp DESC
        LIMIT {limit};
    """

    SOL_TRANSFERS = """
        SELECT 
            block_timestamp,
            source,
            destination,
            value / 1e9 as value_sol,  -- Convert to SOL
            tx_signature
        FROM 
            `bigquery-public-data.crypto_solana_mainnet_us.Token Transfers`
        WHERE 
            (
                source = '{wallet_id}' 
                OR destination = '{wallet_id}'
            )
            AND block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        ORDER BY 
            block_timestamp DESC
        LIMIT {limit};
    """
    
    # Query for getting top tokens by volume
    TOP_TOKENS = """
    WITH token_metadata AS (
    SELECT 
        LOWER(address) AS address,
        name,
        symbol,
        CAST(decimals AS INT64) AS decimals
    FROM 
        `bigquery-public-data.crypto_ethereum.tokens`
    ),

    filtered_transfers AS (
        SELECT
            token_address,
            LOWER(from_address) AS from_address,
            LOWER(to_address) AS to_address,
            CAST(value AS FLOAT64) AS raw_value,
            block_timestamp
        FROM
            `bigquery-public-data.crypto_ethereum.token_transfers`
        WHERE
            (LOWER(from_address) = '{wallet_id}' OR LOWER(to_address) = '{wallet_id}')
            AND block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
    )

    SELECT 
        ft.token_address,
        tm.name,
        tm.symbol,
        tm.decimals,
        COUNT(*) AS transaction_count,
        SUM(
            CASE 
                WHEN ft.from_address = '{wallet_id}' THEN ft.raw_value / POW(10, tm.decimals)
                ELSE 0 
            END
        ) AS sent,
        SUM(
            CASE 
                WHEN ft.to_address = '{wallet_id}' THEN ft.raw_value / POW(10, tm.decimals)
                ELSE 0 
            END
        ) AS received
    FROM 
        filtered_transfers ft
    LEFT JOIN 
        token_metadata tm
    ON 
        ft.token_address = tm.address
    GROUP BY 
        ft.token_address, tm.name, tm.symbol, tm.decimals
    HAVING
        (sent + received) > 0.001
    ORDER BY 
        (sent + received) DESC
    LIMIT {limit};
    """

    WALLET_INFO = """
        WITH wallet_stats AS (
            SELECT
                MIN(block_timestamp) as first_seen,
                COUNT(*) as total_transactions
            FROM `bigquery-public-data.crypto_ethereum.transactions`
            WHERE from_address = '{wallet_id}' OR to_address = '{wallet_id}' 
            AND block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        ),
        contract_check AS (
            SELECT COUNT(*) > 0 as is_contract
            FROM `bigquery-public-data.crypto_ethereum.contracts`
            WHERE address = '{wallet_id}'
            AND block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        )
        SELECT
            ws.first_seen,
            ws.total_transactions,
            cc.is_contract
        FROM wallet_stats ws, contract_check cc
        LIMIT {limit};
    """

    @classmethod
    def format_query(cls, query_template: str, **kwargs) -> str:
        """
        Format a query with the given parameters.
        
        Args:
            query_template (str): The query template to format
            **kwargs: Named parameters to use in formatting
            
        Returns:
            str: Formatted SQL query
        """
        return query_template.format(**kwargs) 