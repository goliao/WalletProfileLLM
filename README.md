# WalletProfileLLM


# Web3 Wallet Profiler LLM Chatbot Specification

## Overview
The Web3 Wallet Profiler is a compliance-focused tool designed to allow users to query transaction activities of Ethereum wallets using natural language. It leverages Google BigQuery's public Ethereum dataset (`bigquery-public-data.crypto_ethereum.transactions`) as the primary data source and provides a user-friendly chatbot interface for interaction. The system is built with Python as the backend and includes a frontend chatbot window for seamless user interaction.

## Key Points
- **Purpose**: Enables compliance teams to analyze Ethereum wallet transaction activities, such as frequency and amounts, over specific periods.
- **Functionality**: Users can ask questions like “What’s the average transaction frequency?” or “Are there large transactions above a threshold?” in natural language.
- **Technology**: Uses Python for the backend, BigQuery for data, and a web-based chatbot for the frontend.
- **Compliance**: Supports identifying transactions that may require Suspicious Activity Reports (SARs) based on thresholds.
- **Limitations**: Relies on public dataset accuracy and may have slight data update delays.

## What the App Does
The app allows you to type questions about an Ethereum wallet’s transactions, like how often it sends money or if it’s made any big transfers recently. It pulls this information from a public database on Google BigQuery, processes it, and answers in plain English through a chat window. It’s designed to help people in compliance roles spot unusual activity that might need reporting.

## How It Works
You enter a wallet address and a question, like “How much Ether did this wallet send last month?” The app uses a language model to understand your question, fetches the relevant data from BigQuery, and sends back an answer, such as “The wallet sent 10.5 Ether.” The chat interface makes it easy to ask follow-up questions.

## Compliance Features
The app can flag transactions above a certain amount, which might indicate suspicious activity needing a SAR. For example, you could ask, “Show me transactions over 10 Ether,” and it will list them, helping you decide if further investigation is needed.

---

# Detailed Specification

## Introduction
The Web3 Wallet Profiler LLM Chatbot is designed to assist compliance professionals in analyzing Ethereum wallet transaction activities. By integrating natural language processing with blockchain data analytics, it provides an intuitive interface for querying transaction details, such as average frequency, total amounts transferred, and large transactions that may trigger regulatory scrutiny. This specification outlines the architecture, functionality, and technical details required to build the application.

## Architecture

### Backend
- **Language**: Python
- **Framework**: FastAPI (preferred for asynchronous support and performance; Flask as an alternative)
- **Data Source**: Google BigQuery’s `bigquery-public-data.crypto_ethereum.transactions` table, which includes fields like:
  - `block_number`
  - `transaction_hash`
  - `from_address`
  - `to_address`
  - `value` (in Wei)
  - `block_timestamp`
  - Full schema details available at [Google Cloud Blog](https://cloud.google.com/blog/products/data-analytics/ethereum-bigquery-public-dataset-smart-contract-analytics)
- **LLM Integration**: External Large Language Model API (e.g., OpenAI GPT, Google PaLM) for:
  - Parsing user queries to extract wallet address, time period, query type, and transaction direction (sent/received).
  - Generating natural language responses from query results.
- **Libraries**:
  - `google-cloud-bigquery`: For querying BigQuery.
  - `fastapi`: For API endpoints.
  - `pydantic`: For data validation.
  - `openai` or `google-generativeai`: For LLM integration.
  - `python-dateutil`: For parsing date expressions.

### Frontend
- **Interface**: A web-based chatbot window for user input and response display.
- **Technologies**: HTML, CSS, JavaScript, with React for a dynamic UI.
- **Styling**: Tailwind CSS via CDN for responsive design.
- **Functionality**:
  - Input fields for wallet address and question.
  - Real-time display of responses.
  - Basic error messages for invalid inputs.

### Integration
- **API Endpoints**:
  - **POST /query**: Receives user queries and returns answers.
    - **Request Body**:
      ```json
      {
        "wallet_address": "0x123...",
        "question": "What's the total Ether sent in the last month?"
      }
      ```
    - **Response**:
      ```json
      {
        "answer": "The total Ether sent from wallet 0x123... in the last month is 5.2 ETH."
      }
      ```
  - **GET /health**: Returns 200 OK for system health checks.
- **LLM API**: Called by the backend to process natural language inputs and outputs.

## Functionality

### User Input
Users provide:
- An Ethereum wallet address (e.g., `0x123...`).
- A natural language question about transaction activities over a specified period.
- Example Questions:
  - “What’s the average transaction frequency for wallet 0x123... over the last month?”
  - “How much total Ether was received by wallet 0x123... in 2024?”
  - “List transactions greater than 10 ETH from wallet 0x123... in the last 3 months.”

### Backend Processing
The backend processes queries in four steps:

1. **Parse User Input**:
   - The LLM extracts:
     - Wallet address
     - Time period (e.g., “last month” → start/end dates)
     - Query type (e.g., “average_frequency”, “total_amount”, “large_transactions”)
     - Direction (“sent” or “received”)
   - **LLM Prompt Example**:
     ```
     You are a blockchain transaction analyst. For the question: [user_question], extract:
     - Wallet address
     - Time period (convert to start_date and end_date in YYYY-MM-DD format)
     - Query type (average_frequency, total_amount, large_transactions)
     - Direction (sent, received)
     Return JSON: {"wallet_address": "", "start_date": "", "end_date": "", "query_type": "", "direction": ""}
     ```
   - **Example Output**:
     ```json
     {
       "wallet_address": "0x123...",
       "start_date": "2025-03-12",
       "end_date": "2025-04-12",
       "query_type": "total_amount",
       "direction": "sent"
     }
     ```

2. **Generate SQL Query**:
   - Based on the parsed components, generate SQL queries for BigQuery.
   - **Query Templates**:
     - **Average Transaction Frequency**:
       ```sql
       SELECT AVG(daily_tx_count) AS avg_frequency
       FROM (
         SELECT DATE(block_timestamp) AS date, COUNT(*) AS daily_tx_count
         FROM `bigquery-public-data.crypto_ethereum.transactions`
         WHERE {direction}_address = @wallet_address
           AND block_timestamp >= @start_date
           AND block_timestamp < @end_date
         GROUP BY date
       )
       ```
     - **Total Ether Transferred**:
       ```sql
       SELECT SUM(value) / POW(10, 18) AS total_ether
       FROM `bigquery-public-data.crypto_ethereum.transactions`
       WHERE {direction}_address = @wallet_address
         AND block_timestamp >= @start_date
         AND block_timestamp < @end_date
       ```
     - **Large Transactions**:
       ```sql
       SELECT transaction_hash, value / POW(10, 18) AS ether_amount, block_timestamp
       FROM `bigquery-public-data.crypto_ethereum.transactions`
       WHERE {direction}_address = @wallet_address
         AND value > @threshold
         AND block_timestamp >= @start_date
         AND block_timestamp < @end_date
       ORDER BY value DESC
       ```
   - Parameters (e.g., `@wallet_address`, `@start_date`) are sanitized to prevent SQL injection.

3. **Execute Query**:
   - Use `google-cloud-bigquery` to run the query.
   - Convert time periods to timestamps (e.g., “last month” → `TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 MONTH)`).
   - Handle Wei-to-Ether conversion (divide by 10^18).

4. **Generate Response**:
   - Process results (e.g., format numbers, handle null cases).
   - Use templated responses for clarity:
     - Average frequency: “The average daily transaction frequency is {value} transactions.”
     - Total amount: “The total Ether {direction} is {value} ETH.”
     - Large transactions: “Found {count} transactions above {threshold} ETH: {details}.”
   - Optionally, use the LLM for more conversational responses.

### Frontend Display
- The chatbot window displays the response in real-time.
- Supports basic formatting (e.g., lists for large transactions).
- Includes an input area for new questions and a history of previous interactions.

## Compliance Features
- **SARs Triggering**:
  - Identify transactions exceeding a configurable threshold (e.g., 10 ETH).
  - Example Query:
    ```sql
    SELECT transaction_hash, value / POW(10, 18) AS ether_amount, block_timestamp
    FROM `bigquery-public-data.crypto_ethereum.transactions`
    WHERE from_address = @wallet_address
      AND value > @sars_threshold
      AND block_timestamp >= @start_date
      AND block_timestamp < @end_date
    ```
  - Results can be flagged with a warning: “This transaction may require SAR filing.”
- **Audit Logging**:
  - Log queries and results for compliance records (optional, configurable).

## Security and Compliance Considerations
- **Access Control**:
  - Implement user authentication (e.g., OAuth) to restrict access.
- **Data Security**:
  - Sanitize inputs to prevent SQL injection.
  - Encrypt API communications with HTTPS.
- **Regulatory Compliance**:
  - Ensure adherence to data privacy laws (e.g., GDPR, CCPA) if storing user data.
- **BigQuery Costs**:
  - Optimize queries to minimize data scanned, reducing costs.
  - Example: Use date partitioning and limit columns selected.

## Deployment
- **Backend**:
  - Deploy on Google Cloud Run for scalability and BigQuery integration.
  - Alternative: AWS Lambda or Heroku.
- **Frontend**:
  - Host on Netlify or Vercel for static assets.
  - Bundle with backend if using a single server.
- **CI/CD**:
  - Use GitHub Actions for automated testing and deployment.

## Dependencies
- **Backend**:
  - `google-cloud-bigquery==3.11.0`
  - `fastapi==0.100.0`
  - `uvicorn==0.22.0`
  - `pydantic==2.0.2`
  - `openai==1.30.0` (or equivalent)
  - `python-dateutil==2.8.2`
- **Frontend**:
  - React (`https://cdn.jsdelivr.net/npm/react@18.2.0`)
  - Tailwind CSS (`https://cdn.tailwindcss.com`)
  - Axios for API calls (`https://cdn.jsdelivr.net/npm/axios@1.4.0`)

## Example Workflow
1. **User Input**:
   - Enters: “For wallet 0x123..., list transactions over 5 ETH in the last 3 months.”
2. **Backend**:
   - LLM parses: `{"wallet_address": "0x123...", "start_date": "2025-01-12", "end_date": "2025-04-12", "query_type": "large_transactions", "direction": "sent"}`
   - Generates SQL:
     ```sql
     SELECT transaction_hash, value / POW(10, 18) AS ether_amount, block_timestamp
     FROM `bigquery-public-data.crypto_ethereum.transactions`
     WHERE from_address = '0x123...'
       AND value > 5000000000000000000
       AND block_timestamp >= '2025-01-12'
       AND block_timestamp < '2025-04-12'
     ORDER BY value DESC
     ```
   - Executes query, gets results: 2 transactions (6.2 ETH, 5.8 ETH).
   - Responds: “Found 2 transactions above 5 ETH: 6.2 ETH on 2025-02-10, 5.8 ETH on 2025-03-15.”
3. **Frontend**:
   - Displays: “Found 2 transactions above 5 ETH: 6.2 ETH on 2025-02-10, 5.8 ETH on 2025-03-15.”

## Sample Code

### Backend (FastAPI)
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import bigquery
from dateutil.parser import parse
import openai
import re

app = FastAPI()

# BigQuery client
client = bigquery.Client()

# LLM client (example with OpenAI)
openai.api_key = "your-api-key"

class QueryRequest(BaseModel):
    wallet_address: str
    question: str

def validate_address(address: str) -> bool:
    return bool(re.match(r'^0x[a-fA-F0-9]{40}$', address))

def parse_query(question: str) -> dict:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Extract wallet address, time period (as start_date and end_date in YYYY-MM-DD), query type (average_frequency, total_amount, large_transactions), and direction (sent, received) from the question. Return JSON."},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content

@app.post("/query")
async def process_query(request: QueryRequest):
    if not validate_address(request.wallet_address):
        raise HTTPException(status_code=400, detail="Invalid wallet address")

    # Parse question with LLM
    parsed = parse_query(request.question)
    if not parsed:
        raise HTTPException(status_code=400, detail="Could not understand the question")

    # Generate SQL based on query type
    query_templates = {
        "average_frequency": """
            SELECT AVG(daily_tx_count) AS result
            FROM (
                SELECT DATE(block_timestamp) AS date, COUNT(*) AS daily_tx_count
                FROM `bigquery-public-data.crypto_ethereum.transactions`
                WHERE {direction}_address = @wallet_address
                  AND block_timestamp >= @start_date
                  AND block_timestamp < @end_date
                GROUP BY date
            )
        """,
        "total_amount": """
            SELECT SUM(value) / POW(10, 18) AS result
            FROM `bigquery-public-data.crypto_ethereum.transactions`
            WHERE {direction}_address = @wallet_address
              AND block_timestamp >= @start_date
              AND block_timestamp < @end_date
        """,
        "large_transactions": """
            SELECT transaction_hash, value / POW(10, 18) AS ether_amount, block_timestamp
            FROM `bigquery-public-data.crypto_ethereum.transactions`
            WHERE {direction}_address = @wallet_address
              AND value > @threshold
              AND block_timestamp >= @start_date
              AND block_timestamp < @end_date
            ORDER BY value DESC
        """
    }

    direction = parsed["direction"]
    query_type = parsed["query_type"]
    sql = query_templates.get(query_type).format(direction=direction)

    # Execute query
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("wallet_address", "STRING", request.wallet_address),
            bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", parsed["start_date"]),
            bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", parsed["end_date"]),
            bigquery.ScalarQueryParameter("threshold", "FLOAT64", parsed.get("threshold", 0))
        ]
    )
    query_job = client.query(sql, job_config=job_config)
    results = query_job.result()

    # Format response
    if query_type == "large_transactions":
        transactions = [f"{row.ether_amount} ETH on {row.block_timestamp}" for row in results]
        answer = f"Found {len(transactions)} transactions: {', '.join(transactions)}."
    else:
        result = next(results).result
        answer = f"The {query_type.replace('_', ' ')} is {result} {'transactions/day' if query_type == 'average_frequency' else 'ETH'}."

    return {"answer": answer}

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
    <script src="https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/react-dom@18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios@1.4.0/dist/axios.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.2/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
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
- **Natural Language Understanding**:
  - The LLM may misinterpret complex or ambiguous questions. Fallback mechanisms (e.g., “Please clarify”) are included.
- **Performance**:
  - Large datasets may slow queries. Use partitioning and selective column retrieval.
- **BigQuery Costs**:
  - Queries scanning large data volumes can be expensive. Optimize by limiting date ranges and fields.
- **Data Freshness**:
  - The public dataset may have a ~4-minute delay, acceptable for compliance use ([Ethereum ETL](https://ethereum-etl.readthedocs.io/en/latest/google-bigquery/)).
- **Address Validation**:
  - Ensure wallet addresses match the Ethereum format (`0x[a-fA-F0-9]{40}`).
- **Time Zones**:
  - Use UTC timestamps to avoid discrepancies.

## Future Enhancements
- **Token Support**:
  - Query ERC-20/ERC-721 transfers using `token_transfers` table.
  - Example: Total USDT sent by a wallet.
- **Advanced Analytics**:
  - Detect patterns (e.g., frequent small transactions) for enhanced compliance.
- **Multi-Blockchain**:
  - Support other cryptocurrencies in BigQuery (e.g., Bitcoin).
- **Visualization**:
  - Add charts for transaction trends using Recharts or Chart.js.

## Example Queries and Responses
| Question | SQL Query | Response |
|----------|-----------|----------|
| “Average transaction frequency last month” | `SELECT AVG(daily_tx_count) FROM (SELECT DATE(block_timestamp) AS date, COUNT(*) AS daily_tx_count FROM ... WHERE from_address = ...)` | “The average daily transaction frequency is 3.5 transactions.” |
| “Total Ether sent in 2024” | `SELECT SUM(value) / POW(10, 18) FROM ... WHERE from_address = ... AND block_timestamp >= '2024-01-01'` | “The total Ether sent is 50.2 ETH.” |
| “Transactions over 10 ETH last 3 months” | `SELECT transaction_hash, value / POW(10, 18), block_timestamp FROM ... WHERE value > 10000000000000000000` | “Found 2 transactions: 12.1 ETH on 2025-02-10, 10.5 ETH on 2025-03-01.” |

## Key Citations
- [Ethereum BigQuery Public Dataset for Smart Contract Analytics](https://cloud.google.com/blog/products/data-analytics/ethereum-bigquery-public-dataset-smart-contract-analytics)
- [Querying BigQuery Blockchain Dataset Tutorial](https://bitquery.io/blog/querying-bigquery-blockchain-dataset)
- [Ethereum ETL Google BigQuery Documentation](https://ethereum-etl.readthedocs.io/en/latest/google-bigquery/)
- [Full Relational Diagram for Ethereum BigQuery Data](https://medium.com/google-cloud/full-relational-diagram-for-ethereum-public-data-on-google-bigquery-2825fdf0fb0b)
- [Awesome BigQuery Views for Blockchain ETL](https://github.com/blockchain-etl/awesome-bigquery-views)
- [Analyzing Ethereum Transactions with BigQuery](https://www.anyblockanalytics.com/blog/analyse-transactions-with-ethereum-google-bigquery-data-set/)
- [How Ethereum BigQuery Dataset Was Built](https://cloud.google.com/blog/products/data-analytics/ethereum-bigquery-how-we-built-dataset)
- [Six New Cryptocurrencies in BigQuery Datasets](https://cloud.google.com/blog/products/data-analytics/introducing-six-new-cryptocurrencies-in-bigquery-public-datasets-and-how-to-analyze-them)
- [Exploring Public Cryptocurrency Datasets in BigQuery](https://www.cloudskillsboost.google/focuses/8486?parent=catalog)
- [Ethereum Blockchain Data on Kaggle](https://www.kaggle.com/bigquery/ethereum-blockchain)