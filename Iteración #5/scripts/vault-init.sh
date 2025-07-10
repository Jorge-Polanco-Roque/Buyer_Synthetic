#!/bin/bash

# ===============================================
# Vault Initialization Script for Buyer Synthetic™
# ===============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔐 Initializing HashiCorp Vault${NC}"
echo -e "${BLUE}=================================${NC}"

# Configuration
VAULT_ADDR="http://localhost:8200"
INIT_FILE="vault-init.json"

# Check if Vault is running
if ! curl -s -f "$VAULT_ADDR/v1/sys/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Vault is not running on $VAULT_ADDR${NC}"
    echo -e "${YELLOW}Start Vault with: docker-compose --profile vault up -d${NC}"
    exit 1
fi

# Check if Vault is already initialized
if vault status -address="$VAULT_ADDR" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Vault is already initialized${NC}"
    exit 0
fi

echo -e "${YELLOW}🚀 Initializing Vault...${NC}"

# Initialize Vault
INIT_RESPONSE=$(vault operator init -address="$VAULT_ADDR" -key-shares=1 -key-threshold=1 -format=json)

# Save initialization data
echo "$INIT_RESPONSE" > "$INIT_FILE"
chmod 600 "$INIT_FILE"

# Extract keys and token
UNSEAL_KEY=$(echo "$INIT_RESPONSE" | jq -r '.unseal_keys_b64[0]')
ROOT_TOKEN=$(echo "$INIT_RESPONSE" | jq -r '.root_token')

echo -e "${GREEN}✅ Vault initialized successfully${NC}"

# Unseal Vault
echo -e "${YELLOW}🔓 Unsealing Vault...${NC}"
vault operator unseal -address="$VAULT_ADDR" "$UNSEAL_KEY"

echo -e "${GREEN}✅ Vault unsealed successfully${NC}"

# Login with root token
export VAULT_TOKEN="$ROOT_TOKEN"
vault auth -address="$VAULT_ADDR" "$ROOT_TOKEN"

# Enable KV v2 secrets engine
echo -e "${YELLOW}🔧 Configuring secrets engine...${NC}"
vault secrets enable -address="$VAULT_ADDR" -path=kv kv-v2

# Create policies
echo -e "${YELLOW}📝 Creating policies...${NC}"

# Application policy
cat > buyer-synthetic-policy.hcl << EOF
# Buyer Synthetic Application Policy
path "kv/data/buyer-synthetic/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "kv/metadata/buyer-synthetic/*" {
  capabilities = ["list", "read", "delete"]
}
EOF

vault policy write -address="$VAULT_ADDR" buyer-synthetic-policy buyer-synthetic-policy.hcl

# Enable userpass auth method
echo -e "${YELLOW}🔐 Setting up authentication...${NC}"
vault auth enable -address="$VAULT_ADDR" userpass

# Create application user
vault write -address="$VAULT_ADDR" auth/userpass/users/buyer-synthetic \\
    password="buyer-synthetic-password" \\
    policies="buyer-synthetic-policy"

# Store some initial secrets
echo -e "${YELLOW}🗄️  Setting up initial secrets...${NC}"

# Example API keys (replace with real values)
vault kv put -address="$VAULT_ADDR" kv/buyer-synthetic/api-keys \\
    openai_api_key="your_openai_api_key_here" \\
    anthropic_api_key="your_anthropic_api_key_here"

# Database configuration
vault kv put -address="$VAULT_ADDR" kv/buyer-synthetic/database \\
    host="localhost" \\
    port="5432" \\
    database="buyer_synthetic" \\
    username="app_user" \\
    password="secure_password"

# Application configuration
vault kv put -address="$VAULT_ADDR" kv/buyer-synthetic/app-config \\
    secret_key="your_secret_key_here" \\
    encryption_key="your_encryption_key_here" \\
    jwt_secret="your_jwt_secret_here"

echo -e "${GREEN}🎉 Vault setup completed successfully!${NC}"
echo -e "${BLUE}=================================${NC}"
echo -e "${YELLOW}📋 Important Information:${NC}"
echo -e "  Vault Address: $VAULT_ADDR"
echo -e "  Root Token: $ROOT_TOKEN"
echo -e "  Unseal Key: $UNSEAL_KEY"
echo -e "  App User: buyer-synthetic"
echo -e "  App Password: buyer-synthetic-password"
echo ""
echo -e "${RED}⚠️  IMPORTANT: Save the information above securely!${NC}"
echo -e "${YELLOW}   Initialization data saved to: $INIT_FILE${NC}"
echo ""
echo -e "${BLUE}🌐 Access Vault UI at: $VAULT_ADDR${NC}"
echo ""
echo -e "${YELLOW}📝 Environment Variables:${NC}"
echo "export VAULT_ADDR=$VAULT_ADDR"
echo "export VAULT_TOKEN=$ROOT_TOKEN"
echo ""
echo -e "${YELLOW}🐳 For Docker Compose:${NC}"
echo "Add to your .env file:"
echo "VAULT_ENABLED=true"
echo "VAULT_ADDR=$VAULT_ADDR"
echo "VAULT_TOKEN=$ROOT_TOKEN"