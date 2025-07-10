"""
Environment Manager for Buyer Synthetic™
Handles environment variables across different deployment environments.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union
from enum import Enum
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Supported environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class EnvironmentManager:
    """
    Manages environment variables with support for multiple environments
    and secure fallbacks to Vault.
    """

    def __init__(self, environment: Optional[str] = None):
        """
        Initialize environment manager.
        
        Args:
            environment: Force specific environment, otherwise auto-detect
        """
        self.base_dir = Path(__file__).parent.parent.parent.parent
        self.environment = self._detect_environment(environment)
        self._load_environment_files()
        self._validate_critical_vars()

    def _detect_environment(self, forced_env: Optional[str] = None) -> Environment:
        """Detect current environment from various sources."""
        if forced_env:
            return Environment(forced_env)
        
        # Check environment variable
        env_var = os.getenv("ENVIRONMENT", os.getenv("ENV", "development")).lower()
        
        # Check for common CI/deployment indicators
        if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
            return Environment.TESTING
        elif os.getenv("KUBERNETES_SERVICE_HOST"):
            return Environment.PRODUCTION if "prod" in os.getenv("NAMESPACE", "") else Environment.STAGING
        elif os.getenv("DOCKER_ENV"):
            return Environment(os.getenv("DOCKER_ENV"))
        
        try:
            return Environment(env_var)
        except ValueError:
            logger.warning(f"Unknown environment '{env_var}', defaulting to development")
            return Environment.DEVELOPMENT

    def _load_environment_files(self):
        """Load environment files in order of precedence."""
        env_files = [
            self.base_dir / f".env.{self.environment.value}",  # Environment-specific
            self.base_dir / ".env.local",                      # Local overrides
            self.base_dir / ".env",                            # Default
        ]
        
        loaded_files = []
        for env_file in env_files:
            if env_file.exists():
                load_dotenv(env_file, override=True)
                loaded_files.append(str(env_file))
                logger.debug(f"Loaded environment file: {env_file}")
        
        if loaded_files:
            logger.info(f"Environment files loaded: {loaded_files}")
        else:
            logger.warning("No environment files found, using system environment only")

    def _validate_critical_vars(self):
        """Validate that critical environment variables are set."""
        critical_vars = {
            Environment.PRODUCTION: [
                "SECRET_KEY",
                "DATABASE_URL",
            ],
            Environment.STAGING: [
                "DATABASE_URL",
            ],
            Environment.DEVELOPMENT: [],
            Environment.TESTING: []
        }
        
        missing_vars = []
        required_vars = critical_vars.get(self.environment, [])
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise EnvironmentError(
                f"Missing critical environment variables for {self.environment}: {missing_vars}"
            )

    def get(self, key: str, default: Any = None, required: bool = False) -> Any:
        """
        Get environment variable with type conversion and validation.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            required: Raise error if not found and no default
            
        Returns:
            Environment variable value with appropriate type conversion
        """
        value = os.getenv(key, default)
        
        if required and value is None:
            raise EnvironmentError(f"Required environment variable '{key}' not found")
        
        return self._convert_type(value)

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable."""
        value = os.getenv(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")

    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer environment variable."""
        try:
            return int(os.getenv(key, default))
        except (ValueError, TypeError):
            logger.warning(f"Invalid integer value for {key}, using default: {default}")
            return default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get float environment variable."""
        try:
            return float(os.getenv(key, default))
        except (ValueError, TypeError):
            logger.warning(f"Invalid float value for {key}, using default: {default}")
            return default

    def get_list(self, key: str, separator: str = ",", default: Optional[list] = None) -> list:
        """Get list from comma-separated environment variable."""
        if default is None:
            default = []
        
        value = os.getenv(key)
        if not value:
            return default
        
        return [item.strip() for item in value.split(separator) if item.strip()]

    def get_dict(self, key: str, default: Optional[dict] = None) -> dict:
        """Get dictionary from JSON environment variable."""
        if default is None:
            default = {}
        
        value = os.getenv(key)
        if not value:
            return default
        
        try:
            import json
            return json.loads(value)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON value for {key}, using default")
            return default

    def _convert_type(self, value: Any) -> Any:
        """Convert string values to appropriate types."""
        if not isinstance(value, str):
            return value
        
        # Boolean conversion
        if value.lower() in ("true", "false"):
            return value.lower() == "true"
        
        # Number conversion
        if value.isdigit():
            return int(value)
        
        try:
            return float(value)
        except ValueError:
            pass
        
        return value

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION

    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.environment == Environment.STAGING

    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == Environment.TESTING

    def get_database_url(self) -> str:
        """Get database URL with environment-specific defaults."""
        db_urls = {
            Environment.DEVELOPMENT: "postgresql://dev_user:dev_pass@localhost:5432/buyer_synthetic_dev",
            Environment.TESTING: "postgresql://test_user:test_pass@localhost:5432/buyer_synthetic_test",
            Environment.STAGING: "postgresql://staging_user:staging_pass@staging-db:5432/buyer_synthetic_staging",
            Environment.PRODUCTION: os.getenv("DATABASE_URL", "")
        }
        
        return os.getenv("DATABASE_URL", db_urls.get(self.environment, ""))

    def get_redis_url(self) -> str:
        """Get Redis URL with environment-specific defaults."""
        redis_urls = {
            Environment.DEVELOPMENT: "redis://localhost:6379/1",
            Environment.TESTING: "redis://localhost:6379/2",
            Environment.STAGING: "redis://staging-redis:6379/0",
            Environment.PRODUCTION: "redis://prod-redis:6379/0"
        }
        
        return os.getenv("REDIS_URL", redis_urls.get(self.environment, "redis://localhost:6379/0"))

    def get_vault_config(self) -> Dict[str, Any]:
        """Get Vault configuration."""
        return {
            "enabled": self.get_bool("VAULT_ENABLED", default=self.is_production()),
            "addr": self.get("VAULT_ADDR", "http://localhost:8200"),
            "token": self.get("VAULT_TOKEN"),
            "mount_point": self.get("VAULT_MOUNT_POINT", "kv"),
        }

    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration."""
        return {
            "openai_api_key": self.get("OPENAI_API_KEY"),
            "default_model": self.get("DEFAULT_MODEL", "gpt-4"),
            "temperature": self.get_float("TEMPERATURE", 0.7),
            "max_tokens": self.get_int("MAX_TOKENS", 2000),
        }

    def get_app_config(self) -> Dict[str, Any]:
        """Get application configuration."""
        return {
            "environment": self.environment.value,
            "debug": self.get_bool("DEBUG", default=self.is_development()),
            "log_level": self.get("LOG_LEVEL", "DEBUG" if self.is_development() else "INFO"),
            "secret_key": self.get("SECRET_KEY"),
            "min_sample_size": self.get_int("MIN_SAMPLE_SIZE", 100),
            "max_sample_size": self.get_int("MAX_SAMPLE_SIZE", 1000),
            "default_sample_size": self.get_int("DEFAULT_SAMPLE_SIZE", 300),
        }

    def export_env_dict(self) -> Dict[str, str]:
        """Export current environment as dictionary."""
        return dict(os.environ)

    def print_config_summary(self):
        """Print configuration summary for debugging."""
        print(f"\n🔧 Environment Configuration Summary")
        print(f"====================================")
        print(f"Environment: {self.environment.value}")
        print(f"Debug Mode: {self.get_bool('DEBUG')}")
        print(f"Log Level: {self.get('LOG_LEVEL', 'INFO')}")
        print(f"Vault Enabled: {self.get_bool('VAULT_ENABLED')}")
        print(f"Database: {self.get_database_url()}")
        print(f"Redis: {self.get_redis_url()}")
        print(f"API Model: {self.get('DEFAULT_MODEL', 'gpt-4')}")
        print("====================================\n")


# Global instance
env_manager = EnvironmentManager()


def get_env_manager() -> EnvironmentManager:
    """Get global environment manager instance."""
    return env_manager


# Convenience functions
def get_environment() -> Environment:
    """Get current environment."""
    return env_manager.environment


def is_development() -> bool:
    """Check if running in development."""
    return env_manager.is_development()


def is_production() -> bool:
    """Check if running in production."""
    return env_manager.is_production()


def is_staging() -> bool:
    """Check if running in staging."""
    return env_manager.is_staging()


def get_config() -> Dict[str, Any]:
    """Get full application configuration."""
    return {
        **env_manager.get_app_config(),
        **env_manager.get_api_config(),
        "vault": env_manager.get_vault_config(),
        "database_url": env_manager.get_database_url(),
        "redis_url": env_manager.get_redis_url(),
    }