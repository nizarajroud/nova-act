import os
from dotenv import load_dotenv

load_dotenv()

print(f"NOVA_ACT_API_KEY: {os.getenv('NOVA_ACT_API_KEY')}")
print(f"NOVA_ACT_SKIP_PLAYWRIGHT_INSTALL: {os.getenv('NOVA_ACT_SKIP_PLAYWRIGHT_INSTALL')}")
