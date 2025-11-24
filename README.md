# mcp-server-weaviate

## 🛠️ Tools
- Test connection
- List all available collections
- Near text search
- Keyword search
- Hybrid search with adjustable parameters

## 🔧 Usage

```json
{
  "mcpServers": {
    "weaviate": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/mcp-server-weaviate",
        "run",
        "mcp-server-weaviate",
        "--http-port",
        "${WEAVIATE_HTTP_PORT:-8080}",
        "--grpc-port",
        "${WEAVIATE_GRPC_PORT:-50051}"
      ]
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