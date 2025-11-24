import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mcp_server_weaviate.server import main

sys.exit(main())  # type: ignore[call-arg]