# Web3 Wallet Profiler MCP Server

## Overview
This project provides a Python-based MCP (Model Context Protocol) server for analyzing and profiling Ethereum wallet transactions. It enables natural language queries about wallet activity by leveraging Google BigQuery, designed to help users understand wallet behaviors and transaction patterns.

## Features
- Analyze Ethereum wallet transactions using natural language queries
- Retrieve transaction history, token distributions, and behavioral patterns
- Integrates with Claude Desktop/Code for interactive analysis
- Uses Google BigQuery as the blockchain data backend

## Project Structure
- `mcp_server.py`: Main entry point for the MCP server
- `bigquery_client.py`: Handles BigQuery queries and data access
- `crypto_client.py`, `crypto_queries.py`, `query_bigquery.py`: Utility modules for blockchain data processing
- `.env`, `.env.example`: Environment variable configuration
- `requirements.txt`, `uv.lock`, `pyproject.toml`: Dependency management files
- `LICENSE`, `README.md`: Project documentation and license

## Requirements
- Python 3.11 or higher (see `.python-version`)
- [uv](https://github.com/astral-sh/uv) for dependency management
- Google Cloud account with BigQuery access
- Claude Desktop or Claude Code
- The following Python dependencies (see `requirements.txt`):
  - google-cloud-bigquery
  - python-dotenv

## Setup
1. Clone the repository and navigate to the project directory
2. Install dependencies using `uv` (reads from `.python-version` and `uv.lock`)
3. Authenticate with Google Cloud using Application Default Credentials for BigQuery access
4. Configure environment variables in a `.env.local` file (see `.env.example` for required keys)
5. Start the MCP server as configured in Claude Desktop/Code

## Integration
- Add the MCP server as a custom server in Claude Desktop/Code configuration
- Start the server using the provided Python environment and entrypoint
- Restart Claude Desktop/Code to detect the MCP server

## Usage
- Submit Ethereum wallet addresses and natural language questions via Claude Desktop/Code
- The server processes queries, retrieves data from BigQuery, and returns a structured answer

## Troubleshooting
- Ensure Google Cloud authentication is successful and the correct project is set
- Check that the MCP server is running and reachable from Claude Desktop/Code
- Adjust the MCP server port in your environment variables if port conflicts occur
- Validate wallet addresses before submitting queries

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Notes
- Only the Python-based MCP server and supporting modules are maintained in this repository
- No frontend or FastAPI components are implemented
- No unused or legacy components are required for operation
- For Google BigQuery setup, refer to official documentation
