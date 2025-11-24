# mcp-server-weaviate

## 🛠️ Tools

### 1. **test_connection**
Test connection to Weaviate server and get server information (version, hostname, available modules).

### 2. **list_collections**
List all available collections in Weaviate with record counts and sample properties.

### 3. **near_text_search**
Perform semantic/vector search in a collection.
- **Parameters:**
  - `collection_name` (required): Name of the collection to search in
  - `query_text` (required): Text query to search for semantically similar results
  - `limit` (optional): Maximum number of results to return (default: 5)

### 4. **keyword_search**
Perform keyword search (BM25) in a collection.
- **Parameters:**
  - `collection_name` (required): Name of the collection to search in
  - `query_text` (required): Keywords to search for using BM25 algorithm
  - `limit` (optional): Maximum number of results to return (default: 5)

### 5. **hybrid_search**
Perform hybrid search (combination of keyword and vector search) in a collection.
- **Parameters:**
  - `collection_name` (required): Name of the collection to search in
  - `query_text` (required): Text query for hybrid search
  - `limit` (optional): Maximum number of results to return (default: 5)
  - `alpha` (optional): Balance between keyword (0) and vector (1) search (default: 0.5)
    - `0.0` = keyword-only search
    - `0.5` = balanced hybrid search
    - `1.0` = vector-only search

## 🔧 Usage

```json
{
  "mcpServers": {
    "weaviate": {
      "args": [
        "--directory",
        "/absolute/path/to/mcp-server-weaviate",
        "run",
        "mcp_server_weaviate",
        "--weaviate-http-port",
        "<weaviate-http-port>",
        "--weaviate-grpc-port",
        "<weaviate-grpc-port>"
      ],
      "command": "uv",
      "disabled": false
    }
  }
}
```

## Reference

[python-sdk](https://github.com/modelcontextprotocol/python-sdk)

[servers](https://github.com/modelcontextprotocol/servers)

[weaviate](https://docs.weaviate.io/weaviate)

[squad-explorer](https://rajpurkar.github.io/SQuAD-explorer/)

[squad-dataset](https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v1.1.json)

[iteam1/mcp-server-hello](https://github.com/iteam1/mcp-server-hello)

[neo4j-contrib/mcp-neo4j-data-modeling](https://github.com/neo4j-contrib/mcp-neo4j/tree/main/servers/mcp-neo4j-data-modeling)

[blazickjp/arxiv-mcp-server](https://github.com/blazickjp/arxiv-mcp-server)