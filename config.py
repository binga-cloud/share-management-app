import os
from pathlib import Path

# Determine if running in Azure
is_azure = "WEBSITE_INSTANCE_ID" in os.environ


class Config:
    SECRET_KEY = 'your-secret-key'  # Keep this same as before

    # Use different paths for Azure vs local
    if is_azure:
        SQLALCHEMY_DATABASE_URI = 'sqlite:////home/database.db'  # For Azure
    else:
        # For local development (creates database.db in your project folder)
        base_dir = Path(__file__).parent
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{base_dir}/database.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False