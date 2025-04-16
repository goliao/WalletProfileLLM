# Web3 Wallet Profiler LLM Chatbot Specification

## Key Points
- **Purpose**: It seems likely that this tool can help compliance teams analyze Ethereum wallet transactions using simple questions.
- **Technology**: Uses OpenAI’s language model and a special server to understand and query blockchain data.
- **Features**: You can ask about transaction patterns or flag large transfers that might need reporting.
- **Limitations**: The system depends on public data, which might have slight delays or require technical setup.

## What Is It?
This is a chatbot that lets you ask questions about an Ethereum wallet’s activities, like how much money it sent or if it made any big transactions. It’s built to help people in compliance roles keep an eye on wallet behavior.

## How Does It Work?
You type in a wallet address and a question, like “How many transactions did this wallet make last week?” The chatbot uses OpenAI’s tech to understand your question, checks the blockchain data structure, pulls the right information, and gives you a clear answer in plain English.

## Why Is It Useful for Compliance?
It can spot transactions that might be suspicious, like ones over a certain amount, which could need a report. It’s designed to make it easier to dig into wallet activities without needing to be a tech expert.

---

# Comprehensive Specification for Web3 Wallet Profiler LLM Chatbot

## Overview
The Web3 Wallet Profiler LLM Chatbot is a specialized tool crafted to assist compliance professionals in analyzing Ethereum wallet transaction activities through natural language queries. It integrates Google BigQuery’s public Ethereum dataset ([BigQuery Ethereum](https://cloud.google.com/bigquery/public-data/ethereum-blockchain)) with OpenAI’s GPT-4 model for query processing and ergut’s mcp-bigquery-server for schema inspection and query execution ([ergut’s MCP Server](https://github.com/ergut/mcp-bigquery-server)). The system features a user-friendly web-based chatbot interface built with React, enabling users to ask questions about transaction frequency, amounts, and patterns, while supporting compliance tasks like identifying transactions that may require Suspicious Activity Reports (SARs).

## Introduction
This specification details the architecture, functionality, and implementation of the Web3 Wallet Profiler LLM Chatbot, tailored for compliance use. By combining OpenAI’s natural language processing capabilities with ergut’s mcp-bigquery-server, the chatbot can dynamically understand the structure of blockchain data and answer complex questions about Ethereum wallet activities. The backend is built with Python and FastAPI, ensuring robust API handling, while the frontend provides an intuitive chat experience.

## Setup with Claude Desktop
go to the following location: ~/Library/Application Support/Claude/claude_desktop_config.json
and add the following definition to your mcp servers: 
```
{
    "mcpServers": {
      ...
        "tokens": {
            "command": "uv",
            "args": [
                "--directory",
                "~/WalletProfileLLM",
                "run",
                "mcp_server.py"
            ]
        }
    }
}
```

## Architecture

### Backend
- **Language**: Python
- **Framework**: FastAPI for efficient API endpoints
- **Data Source**: Google BigQuery’s `bigquery-public-data.crypto_ethereum.transactions` table, containing fields like `block_number`, `transaction_hash`, `from_address`, `to_address`, `value` (in Wei), and `block_timestamp`
- **MCP Integration**:
  - **Server**: ergut’s mcp-bigquery-server, providing tools like `describe-table` for schema inspection and `execute-query` for running SQL queries
  - **Client**: Embedded in the backend to communicate with the MCP server via WebSocket
- **LLM Integration**: OpenAI’s GPT-4 for parsing queries, generating SQL, and formatting responses
- **Libraries**:
  - `fastapi==0.100.0`: API framework
  - `pydantic==2.0.2`: Data validation
  - `openai==1.30.0`: LLM integration
  - `websocket-client==1.6.2`: MCP server communication
  - `json`: Schema and result handling

### Frontend
- **Interface**: Web-based chatbot window
- **Technologies**: React for dynamic UI, Tailwind CSS via CDN for styling, Axios for API calls
- **Functionality**:
  - Input fields for wallet address and question
  - Real-time response display
  - Error handling for invalid inputs

### MCP Server
- **Server**: ergut’s mcp-bigquery-server
- **Purpose**: Enables the LLM to inspect BigQuery table schemas and execute queries dynamically
- **Configuration**: Requires Node.js 14+, Google Cloud CLI, GCP project ID, location, and a service account with `roles/bigquery.user` permissions

### Integration
- **API Endpoints**:
  - **POST /query**: Accepts wallet address and question, returns natural language answer
    - Request: `{"wallet_address": "0x123...", "question": "Total Ether sent in 2024"}`
    - Response: `{"answer": "The total Ether sent is 50.2 ETH."}`
  - **GET /health**: Returns system status
- **MCP Communication**: Backend uses WebSocket to call MCP tools (`describe-table`, `execute-query`)
- **LLM Interaction**: OpenAI API processes user queries and formats responses

## Functionality

### User Input
Users provide:
- An Ethereum wallet address (e.g., `0x123...`)
- A natural language question, such as:
  - “What’s the average transaction frequency for wallet 0x123... over the last month?”
  - “How much total Ether was received in 2024?”
  - “List transactions over 10 ETH in the last 3 months.”

### Backend Processing
The backend processes queries in four steps:
1. **Schema Inspection**:
   - Calls `describe-table` via ergut’s mcp-bigquery-server to retrieve the schema of `crypto_ethereum.transactions`
   - Example: Retrieves fields like `value` (STRING, Wei), `block_timestamp` (TIMESTAMP)
2. **Query Generation**:
   - Sends schema, wallet address, and question to OpenAI’s GPT-4
   - GPT-4 generates an SQL query and response template
   - Example Prompt:
     ```
     You are a blockchain analyst with access to the BigQuery table schema:
     {schema}
     For the question: {question}
     Generate an SQL query for wallet {wallet_address}.
     Return JSON: {"sql_query": "", "response_template": ""}
     ```
3. **Query Execution**:
   - Submits the SQL query to `execute-query` via the MCP server
   - Handles Wei-to-Ether conversion (divide by 10^18)
4. **Response Formatting**:
   - GPT-4 formats query results into natural language using the response template
   - Example: “The average transaction frequency is 3.5 transactions per day.”

### Frontend Display
- Displays responses in a chat window with user questions and system answers
- Supports basic formatting (e.g., lists for transaction details)
- Maintains query history for user reference

## Compliance Features
- **SARs Triggering**:
  - Identifies transactions above a threshold (e.g., 10 ETH)
  - Example SQL (generated by LLM):
    ```sql
    SELECT transaction_hash, value / POW(10, 18) AS ether_amount, block_timestamp
    FROM `bigquery-public-data.crypto_ethereum.transactions`
    WHERE from_address = '0x123...'
      AND value > 10000000000000000000
      AND block_timestamp >= '2024-01-01'
      AND block_timestamp < '2024-04-01'
    ```
  - Flags results: “This transaction may require SAR filing.”
- **Pattern Detection**:
  - Supports queries for patterns like frequent small transfers, leveraging schema context
- **Audit Logging**:
  - Optionally logs queries and results for compliance records

## Setting Up ergut’s mcp-bigquery-server
1. **Install**:
   - Use Smithery: `npx @smithery/cli install @ergut/mcp-bigquery-server --client claude`
   - Or manually with Node.js 14+ and Google Cloud CLI
2. **Configure**:
   - Provide GCP project ID and location (e.g., `us-central1`)
   - Create a service account with `roles/bigquery.user` permissions
   - Supply the service account key
3. **Run**:
   - Command: `node index.js --project-id your-project --location us-central1 --service-account-key path/to/key.json`
   - Ensure accessibility from the backend (e.g., WebSocket at `ws://localhost:8080`)

## Security and Compliance Considerations
- **MCP Security**:
  - ergut’s server is read-only, minimizing unauthorized access risks
  - 1GB query limit prevents excessive resource usage
- **Data Privacy**:
  - Comply with GDPR/CCPA if storing logs ([GDPR Info](https://gdpr.eu/))
  - Use HTTPS for API and MCP communications
- **Authentication**:
  - Secure MCP server with service account keys
  - Implement OAuth for chatbot access
- **BigQuery Costs**:
  - Optimize queries to reduce scanned data
  - Monitor usage to manage costs ([BigQuery Pricing](https://cloud.google.com/bigquery/pricing))

## Deployment
- **Backend**: Deploy on Google Cloud Run for scalability
- **Frontend**: Host on Netlify or Vercel for static assets
- **MCP Server**: Deploy on Google Cloud Run or similar, ensuring WebSocket support
- **CI/CD**: Use GitHub Actions for automated testing and deployment

## Dependencies
| Component | Dependency | Version | Purpose |
|-----------|------------|---------|---------|
| Backend   | fastapi    | 0.100.0 | API framework |
| Backend   | pydantic   | 2.0.2   | Data validation |
| Backend   | openai     | 1.30.0  | LLM integration |
| Backend   | websocket-client | 1.6.2 | MCP communication |
| Backend   | json       | Built-in | Schema handling |
| Frontend  | React      | 18.2.0  | Dynamic UI |
| Frontend  | Tailwind CSS | Latest | Styling |
| Frontend  | Axios      | Latest  | API calls |

## Example Workflow
| Step | Action | Example |
|------|--------|---------|
| User Input | Submits query | “Total Ether sent by wallet 0x123... in 2024” |
| Schema Inspection | Calls `describe-table` | Retrieves schema: `value`, `block_timestamp` |
| Query Generation | GPT-4 builds SQL | `SELECT SUM(value) / POW(10, 18) FROM ... WHERE from_address = '0x123...'` |
| Query Execution | MCP runs query | Returns 50.2 ETH |
| Response | GPT-4 formats output | “The total Ether sent is 50.2 ETH.” |

## Sample Code

### Backend (FastAPI with MCP)
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import re
import websocket
import json

app = FastAPI()

# LLM client (OpenAI)
openai.api_key = "your-api-key"

# MCP server URL
MCP_SERVER_URL = "ws://localhost:8080"

class QueryRequest(BaseModel):
    wallet_address: str
    question: str

def validate_address(address: str) -> bool:
    return bool(re.match(r'^0x[a-fA-F0-9]{40}$', address))

def call_mcp_tool(tool: str, params: dict) -> dict:
    ws = websocket.WebSocket()
    ws.connect(MCP_SERVER_URL)
    request = {"tool": tool, "params": params}
    ws.send(json.dumps(request))
    response = json.loads(ws.recv())
    ws.close()
    return response

def process_query_with_mcp(question: str, wallet_address: str) -> str:
    # Step 1: Get schema
    schema = call_mcp_tool("describe-table", {
        "dataset": "bigquery-public-data.crypto_ethereum",
        "table": "transactions"
    })

    # Step 2: Generate SQL query with LLM
    prompt = f"""
    You are a blockchain analyst with access to the BigQuery table schema:
    {json.dumps(schema)}
    For the question: {question}
    Generate an SQL query for wallet {wallet_address}.
    Return JSON: {{"sql_query": "", "response_template": ""}}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    query_info = json.loads(response.choices[0].message.content)

    # Step 3: Execute query via MCP
    query_result = call_mcp_tool("execute-query", {
        "query": query_info["sql_query"]
    })

    # Step 4: Format response
    return query_info["response_template"].format(result=query_result["data"])

@app.post("/query")
async def process_query(request: QueryRequest):
    if not validate_address(request.wallet_address):
        raise HTTPException(status_code=400, detail="Invalid wallet address")

    try:
        answer = process_query_with_mcp(request.question, request.wallet_address)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "OK"}
```

### Frontend (React)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Web3 Wallet Profiler</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.2/babel.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/axios/1.4.0/axios.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        const { useState, useEffect } = React;

        const Chatbot = () => {
            const [walletAddress, setWalletAddress] = useState('');
            const [question, setQuestion] = useState('');
            const [messages, setMessages] = useState([]);
            const [isLoading, setIsLoading] = useState(false);

            const handleSubmit = async (e) => {
                e.preventDefault();
                if (!walletAddress || !question) return;

                setMessages([...messages, { text: question, isUser: true }]);
                setIsLoading(true);

                try {
                    const response = await axios.post('/query', {
                        wallet_address: walletAddress,
                        question
                    });
                    setMessages([...messages, { text: question, isUser: true }, { text: response.data.answer, isUser: false }]);
                } catch (error) {
                    setMessages([...messages, { text: question, isUser: true }, { text: 'Error processing query.', isUser: false }]);
                }

                setQuestion('');
                setIsLoading(false);
            };

            return (
                <div className="max-w-2xl mx-auto p-4">
                    <h1 className="text-2xl font-bold mb-4">Web3 Wallet Profiler</h1>
                    <div className="mb-4">
                        <input
                            type="text"
                            value={walletAddress}
                            onChange={(e) => setWalletAddress(e.target.value)}
                            placeholder="Enter wallet address (0x...)"
                            className="w-full p-2 border rounded"
                        />
                    </div>
                    <div className="h-96 overflow-y-auto border p-4 mb-4 rounded">
                        {messages.map((msg, index) => (
                            <div key={index} className={`mb-2 ${msg.isUser ? 'text-right' : 'text-left'}`}>
                                <span className={`inline-block p-2 rounded ${msg.isUser ? 'bg-blue-100' : 'bg-gray-100'}`}>
                                    {msg.text}
                                </span>
                            </div>
                        ))}
                        {isLoading && <div className="text-center">Loading...</div>}
                    </div>
                    <div className="flex">
                        <input
                            type="text"
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            placeholder="Ask about wallet transactions..."
                            className="flex-grow p-2 border rounded-l"
                        />
                        <button
                            onClick={handleSubmit}
                            className="bg-blue-500 text-white p-2 rounded-r"
                            disabled={isLoading}
                        >
                            Send
                        </button>
                    </div>
                </div>
            );
        };

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<Chatbot />);
    </script>
</body>
</html>
```

## Challenges and Considerations
- **LLM Accuracy**: GPT-4 may generate incorrect SQL queries; validation is recommended
- **MCP Stability**: As a developer preview, ergut’s server may have bugs; monitor updates
- **Performance**: Schema inspection adds latency; caching schemas could improve speed
- **Data Freshness**: BigQuery’s dataset may lag by ~4 minutes, suitable for compliance
- **Complex Queries**: Ensure robust handling of joins or aggregations

## Future Enhancements
- **Multi-Table Support**: Query `token_transfers` for ERC-20 analysis
- **Advanced Analytics**: Detect anomalies like wash trading
- **Multi-Chain**: Support other cryptocurrencies in BigQuery
- **Visualization**: Add charts using Recharts for transaction trends

## Conclusion
The Web3 Wallet Profiler LLM Chatbot, powered by OpenAI’s GPT-4 and ergut’s mcp-bigquery-server, offers a robust solution for compliance professionals. It simplifies the analysis of Ethereum wallet transactions through natural language, supports complex queries, and aligns with regulatory needs, making it a valuable tool for blockchain compliance.

## Key Citations
- [Google BigQuery Public Ethereum Dataset](https://cloud.google.com/bigquery/public-data/ethereum-blockchain)
- [ergut’s MCP BigQuery Server Repository](https://github.com/ergut/mcp-bigquery-server)
- [OpenAI API Documentation for Developers](https://platform.openai.com/docs/api-reference)
- [GDPR Compliance Information and Guidelines](https://gdpr.eu/)
- [Google BigQuery Pricing Details](https://cloud.google.com/bigquery/pricing)