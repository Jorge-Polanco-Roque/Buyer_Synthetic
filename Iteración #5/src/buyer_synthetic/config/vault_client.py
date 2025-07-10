"""
HashiCorp Vault client for secure secrets management.
"""

import os
import hvac
from typing import Dict, Optional, Any
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)


class VaultClient:
    """
    HashiCorp Vault client for managing secrets securely.
    """

    def __init__(
        self,
        vault_url: str = "http://localhost:8200",
        vault_token: Optional[str] = None,
        mount_point: str = "kv",
    ):
        """
        Initialize Vault client.

        Args:
            vault_url: Vault server URL
            vault_token: Vault authentication token
            mount_point: KV secrets engine mount point
        """
        self.vault_url = vault_url
        self.mount_point = mount_point
        self.client = hvac.Client(url=vault_url)
        
        # Authenticate with token if provided
        if vault_token:
            self.client.token = vault_token
        else:
            # Try to get token from environment
            env_token = os.getenv("VAULT_TOKEN")
            if env_token:
                self.client.token = env_token
            else:
                logger.warning("No Vault token provided. Authentication required.")

    def is_authenticated(self) -> bool:
        """Check if client is authenticated with Vault."""
        try:
            return self.client.is_authenticated()
        except Exception as e:
            logger.error(f"Failed to check Vault authentication: {e}")
            return False

    def authenticate_with_userpass(self, username: str, password: str) -> bool:
        """
        Authenticate with username/password method.

        Args:
            username: Username for authentication
            password: Password for authentication

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            response = self.client.auth.userpass.login(
                username=username,
                password=password
            )
            self.client.token = response["auth"]["client_token"]
            logger.info(f"Successfully authenticated user: {username}")
            return True
        except Exception as e:
            logger.error(f"Failed to authenticate with userpass: {e}")
            return False

    def store_secret(
        self, 
        path: str, 
        secret_data: Dict[str, Any],
        version: Optional[int] = None
    ) -> bool:
        """
        Store a secret in Vault.

        Args:
            path: Secret path (e.g., 'buyer-synthetic/api-keys')
            secret_data: Dictionary containing secret key-value pairs
            version: Optional version for KV v2 engine

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.is_authenticated():
                logger.error("Not authenticated with Vault")
                return False

            # For KV v2 engine
            response = self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=secret_data,
                mount_point=self.mount_point
            )
            
            logger.info(f"Successfully stored secret at path: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to store secret at {path}: {e}")
            return False

    def get_secret(self, path: str, version: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve a secret from Vault.

        Args:
            path: Secret path
            version: Optional version for KV v2 engine

        Returns:
            Secret data as dictionary, None if not found or error
        """
        try:
            if not self.is_authenticated():
                logger.error("Not authenticated with Vault")
                return None

            # For KV v2 engine
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                version=version,
                mount_point=self.mount_point
            )
            
            return response["data"]["data"]
        except Exception as e:
            logger.error(f"Failed to retrieve secret from {path}: {e}")
            return None

    def delete_secret(self, path: str) -> bool:
        """
        Delete a secret from Vault.

        Args:
            path: Secret path

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.is_authenticated():
                logger.error("Not authenticated with Vault")
                return False

            self.client.secrets.kv.v2.delete_latest_version_of_secret(
                path=path,
                mount_point=self.mount_point
            )
            
            logger.info(f"Successfully deleted secret at path: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete secret at {path}: {e}")
            return False

    def list_secrets(self, path: str = "") -> Optional[list]:
        """
        List secrets at a given path.

        Args:
            path: Path to list (empty for root)

        Returns:
            List of secret names, None if error
        """
        try:
            if not self.is_authenticated():
                logger.error("Not authenticated with Vault")
                return None

            response = self.client.secrets.kv.v2.list_secrets(
                path=path,
                mount_point=self.mount_point
            )
            
            return response["data"]["keys"]
        except Exception as e:
            logger.error(f"Failed to list secrets at {path}: {e}")
            return None


class SecretManager:
    """
    High-level secrets manager using Vault backend.
    """

    def __init__(self, vault_client: VaultClient):
        """Initialize with Vault client."""
        self.vault = vault_client
        self.app_path = "buyer-synthetic"

    def store_api_key(self, service: str, api_key: str) -> bool:
        """
        Store an API key for a service.

        Args:
            service: Service name (e.g., 'openai', 'anthropic')
            api_key: API key value

        Returns:
            True if successful
        """
        path = f"{self.app_path}/api-keys"
        
        # Get existing keys first
        existing = self.vault.get_secret(path) or {}
        existing[f"{service}_api_key"] = api_key
        
        return self.vault.store_secret(path, existing)

    def get_api_key(self, service: str) -> Optional[str]:
        """
        Retrieve API key for a service.

        Args:
            service: Service name

        Returns:
            API key if found, None otherwise
        """
        path = f"{self.app_path}/api-keys"
        secrets = self.vault.get_secret(path)
        
        if secrets:
            return secrets.get(f"{service}_api_key")
        return None

    def store_database_config(
        self, 
        host: str, 
        port: int, 
        database: str, 
        username: str, 
        password: str
    ) -> bool:
        """
        Store database configuration.

        Args:
            host: Database host
            port: Database port
            database: Database name
            username: Database username
            password: Database password

        Returns:
            True if successful
        """
        path = f"{self.app_path}/database"
        config = {
            "host": host,
            "port": port,
            "database": database,
            "username": username,
            "password": password
        }
        
        return self.vault.store_secret(path, config)

    def get_database_config(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve database configuration.

        Returns:
            Database config dictionary if found
        """
        path = f"{self.app_path}/database"
        return self.vault.get_secret(path)

    def store_app_secrets(self, secrets: Dict[str, str]) -> bool:
        """
        Store application-specific secrets.

        Args:
            secrets: Dictionary of secret key-value pairs

        Returns:
            True if successful
        """
        path = f"{self.app_path}/app-config"
        return self.vault.store_secret(path, secrets)

    def get_app_secrets(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve application secrets.

        Returns:
            Application secrets dictionary if found
        """
        path = f"{self.app_path}/app-config"
        return self.vault.get_secret(path)


def get_secret_manager() -> Optional[SecretManager]:
    """
    Factory function to create configured SecretManager.

    Returns:
        Configured SecretManager instance or None if Vault unavailable
    """
    try:
        vault_url = os.getenv("VAULT_ADDR", "http://localhost:8200")
        vault_token = os.getenv("VAULT_TOKEN")
        
        vault_client = VaultClient(
            vault_url=vault_url,
            vault_token=vault_token
        )
        
        if vault_client.is_authenticated():
            return SecretManager(vault_client)
        else:
            logger.warning("Vault not authenticated, falling back to environment variables")
            return None
    except Exception as e:
        logger.error(f"Failed to initialize Vault client: {e}")
        return None