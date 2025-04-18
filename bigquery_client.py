from google.cloud import bigquery
import os
from dotenv import load_dotenv

class BigQueryQueryTooLarge(Exception):
    """Exception raised when a BigQuery query would process too much data."""
    pass

class BigQueryClient:
    def __init__(self):
        load_dotenv()
        self.project_id = os.getenv("PROJECT_ID")
        self.client = bigquery.Client(project=self.project_id)
        self.max_query_size_gb = 300  # Maximum allowed query size in GB
    
    async def execute_query(self, query: str) -> list:
        """
        Execute a BigQuery query asynchronously.
        
        Args:
            query (str): The SQL query to execute
            
        Returns:
            list: List of dictionaries containing query results
            
        Raises:
            BigQueryQueryTooLarge: If the query would process more than max_query_size_gb GB
        """
        # First check the query size
        usage = await self.estimate_query_usage(query)
        if usage > self.max_query_size_gb:
            raise BigQueryQueryTooLarge(
                f"Query would process {usage:.2f} GB, which exceeds the maximum allowed size of {self.max_query_size_gb} GB"
            )
        
        print(f"Query usage: {usage:.2f} GB")
        query_job = self.client.query(query)
        results = []
        
        # Convert results to list of dictionaries
        for row in query_job:
            results.append(dict(row.items()))
        
        return results

    async def estimate_query_usage(self, query: str) -> float:
        """
        Estimate the data usage of a BigQuery query asynchronously.
        
        Args:
            query (str): The SQL query to estimate usage for
            
        Returns:
            float: Estimated data usage in GB
        """
        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        job = self.client.query(query, job_config=job_config)
        return job.total_bytes_processed / 1_000_000_000  # GB

# Create a singleton instance
bigquery_client = BigQueryClient() 