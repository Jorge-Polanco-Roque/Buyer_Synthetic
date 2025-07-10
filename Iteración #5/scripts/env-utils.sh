#!/bin/bash

# ===============================================
# Environment Management Utilities
# ===============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Help function
show_help() {
    echo -e "${BLUE}Environment Management Utilities${NC}"
    echo -e "${BLUE}=================================${NC}"
    echo ""
    echo "Usage: $0 COMMAND [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  init ENV          Initialize environment file for ENV (dev/staging/prod)"
    echo "  check             Check current environment configuration"
    echo "  validate ENV      Validate environment file"
    echo "  switch ENV        Switch to environment ENV"
    echo "  backup            Backup current environment files"
    echo "  restore BACKUP    Restore from backup"
    echo "  generate-key      Generate secure random key"
    echo "  vault-setup       Setup Vault secrets from .env"
    echo "  compare ENV1 ENV2 Compare two environment configurations"
    echo ""
    echo "Examples:"
    echo "  $0 init dev                    # Create .env.development"
    echo "  $0 check                       # Check current config"
    echo "  $0 validate production         # Validate production env"
    echo "  $0 switch staging              # Switch to staging"
    echo "  $0 generate-key                # Generate secret key"
}

# Initialize environment file
init_env() {
    local env_type="$1"
    local env_file=""
    
    case "$env_type" in
        "dev"|"development")
            env_file=".env.development"
            ;;
        "staging")
            env_file=".env.staging"
            ;;
        "prod"|"production")
            env_file=".env.production"
            ;;
        *)
            echo -e "${RED}❌ Invalid environment type. Use: dev, staging, or prod${NC}"
            exit 1
            ;;
    esac
    
    cd "$PROJECT_ROOT"
    
    if [[ -f "$env_file" ]]; then
        echo -e "${YELLOW}⚠️  File $env_file already exists${NC}"
        read -p "Overwrite? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Cancelled."
            exit 0
        fi
    fi
    
    echo -e "${BLUE}📝 Creating $env_file...${NC}"
    cp .env.example "$env_file"
    
    echo -e "${GREEN}✅ Created $env_file${NC}"
    echo -e "${YELLOW}📋 Please edit $env_file and add your actual values${NC}"
}

# Check current environment
check_env() {
    cd "$PROJECT_ROOT"
    
    echo -e "${BLUE}🔍 Current Environment Status${NC}"
    echo -e "${BLUE}=============================${NC}"
    
    # Check which environment files exist
    echo "Environment files:"
    for env_file in .env .env.development .env.staging .env.production .env.local; do
        if [[ -f "$env_file" ]]; then
            echo -e "  ${GREEN}✅ $env_file${NC}"
        else
            echo -e "  ${RED}❌ $env_file${NC}"
        fi
    done
    
    echo ""
    
    # Check current environment
    if [[ -f ".env" ]]; then
        echo "Current environment variables:"
        echo "  ENVIRONMENT=$(grep '^ENVIRONMENT=' .env 2>/dev/null | cut -d'=' -f2 || echo 'not set')"
        echo "  DEBUG=$(grep '^DEBUG=' .env 2>/dev/null | cut -d'=' -f2 || echo 'not set')"
        echo "  LOG_LEVEL=$(grep '^LOG_LEVEL=' .env 2>/dev/null | cut -d'=' -f2 || echo 'not set')"
        echo "  VAULT_ENABLED=$(grep '^VAULT_ENABLED=' .env 2>/dev/null | cut -d'=' -f2 || echo 'not set')"
    else
        echo -e "${YELLOW}⚠️  No .env file found${NC}"
    fi
    
    echo ""
    
    # Check for sensitive data
    if [[ -f ".env" ]]; then
        echo "Security check:"
        if grep -q "your_.*_here" .env; then
            echo -e "  ${RED}⚠️  Found placeholder values in .env${NC}"
        else
            echo -e "  ${GREEN}✅ No placeholder values found${NC}"
        fi
        
        if grep -q "^OPENAI_API_KEY=sk-" .env; then
            echo -e "  ${GREEN}✅ OpenAI API key configured${NC}"
        else
            echo -e "  ${YELLOW}⚠️  OpenAI API key not configured${NC}"
        fi
    fi
}

# Validate environment file
validate_env() {
    local env_type="$1"
    local env_file=".env.$env_type"
    
    cd "$PROJECT_ROOT"
    
    if [[ ! -f "$env_file" ]]; then
        echo -e "${RED}❌ File $env_file not found${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}🔍 Validating $env_file${NC}"
    
    # Check for required variables
    local required_vars=()
    case "$env_type" in
        "production")
            required_vars=("SECRET_KEY" "DATABASE_URL" "OPENAI_API_KEY")
            ;;
        "staging")
            required_vars=("DATABASE_URL" "OPENAI_API_KEY")
            ;;
        "development")
            required_vars=("OPENAI_API_KEY")
            ;;
    esac
    
    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if ! grep -q "^$var=" "$env_file" || grep -q "^$var=your_.*_here" "$env_file"; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -eq 0 ]]; then
        echo -e "${GREEN}✅ All required variables are configured${NC}"
    else
        echo -e "${RED}❌ Missing or invalid variables:${NC}"
        for var in "${missing_vars[@]}"; do
            echo -e "  ${RED}- $var${NC}"
        done
        exit 1
    fi
    
    # Check for security issues
    if grep -q "password\|secret\|key" "$env_file" | grep -q "123\|password\|admin"; then
        echo -e "${RED}⚠️  Weak passwords/secrets detected${NC}"
    fi
    
    echo -e "${GREEN}✅ Validation completed${NC}"
}

# Switch environment
switch_env() {
    local env_type="$1"
    local source_file=""
    
    case "$env_type" in
        "dev"|"development")
            source_file=".env.development"
            ;;
        "staging")
            source_file=".env.staging"
            ;;
        "prod"|"production")
            source_file=".env.production"
            ;;
        *)
            echo -e "${RED}❌ Invalid environment type${NC}"
            exit 1
            ;;
    esac
    
    cd "$PROJECT_ROOT"
    
    if [[ ! -f "$source_file" ]]; then
        echo -e "${RED}❌ Source file $source_file not found${NC}"
        exit 1
    fi
    
    # Backup current .env if it exists
    if [[ -f ".env" ]]; then
        cp .env ".env.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${YELLOW}📦 Backed up current .env${NC}"
    fi
    
    # Switch to new environment
    cp "$source_file" .env
    echo -e "${GREEN}✅ Switched to $env_type environment${NC}"
    
    # Show summary
    echo "Current environment: $(grep '^ENVIRONMENT=' .env | cut -d'=' -f2)"
}

# Generate secure key
generate_key() {
    local length="${1:-32}"
    local key
    
    if command -v openssl >/dev/null 2>&1; then
        key=$(openssl rand -base64 "$length" | tr -d "=+/" | cut -c1-"$length")
    elif command -v python3 >/dev/null 2>&1; then
        key=$(python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range($length)))")
    else
        key=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w "$length" | head -n 1)
    fi
    
    echo -e "${GREEN}Generated secure key:${NC}"
    echo "$key"
    echo ""
    echo -e "${YELLOW}💡 Copy this to your SECRET_KEY environment variable${NC}"
}

# Backup environment files
backup_env() {
    cd "$PROJECT_ROOT"
    
    local backup_dir="backups/env_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    for env_file in .env .env.* vault/config.hcl; do
        if [[ -f "$env_file" && ! "$env_file" =~ \.example$ ]]; then
            cp "$env_file" "$backup_dir/"
            echo -e "${GREEN}📦 Backed up $env_file${NC}"
        fi
    done
    
    echo -e "${GREEN}✅ Backup created in $backup_dir${NC}"
}

# Setup Vault from .env
vault_setup() {
    cd "$PROJECT_ROOT"
    
    if [[ ! -f ".env" ]]; then
        echo -e "${RED}❌ No .env file found${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}🔐 Setting up Vault secrets from .env${NC}"
    
    # Check if Vault is running
    if ! curl -s -f "http://localhost:8200/v1/sys/health" >/dev/null 2>&1; then
        echo -e "${RED}❌ Vault is not running${NC}"
        echo -e "${YELLOW}Start Vault with: make docker-compose-vault${NC}"
        exit 1
    fi
    
    # Extract API keys and store in Vault
    while IFS='=' read -r key value; do
        if [[ $key =~ _API_KEY$ ]] && [[ ! $value =~ your_.*_here ]]; then
            service=$(echo "$key" | sed 's/_API_KEY$//' | tr '[:upper:]' '[:lower:]')
            echo "Storing $service API key in Vault..."
            vault kv put kv/buyer-synthetic/api-keys "${service}_api_key=$value"
        fi
    done < .env
    
    echo -e "${GREEN}✅ Vault setup completed${NC}"
}

# Compare environments
compare_env() {
    local env1="$1"
    local env2="$2"
    
    cd "$PROJECT_ROOT"
    
    local file1=".env.$env1"
    local file2=".env.$env2"
    
    if [[ ! -f "$file1" ]]; then
        echo -e "${RED}❌ File $file1 not found${NC}"
        exit 1
    fi
    
    if [[ ! -f "$file2" ]]; then
        echo -e "${RED}❌ File $file2 not found${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}🔍 Comparing $env1 vs $env2${NC}"
    echo -e "${BLUE}========================${NC}"
    
    # Show differences
    if command -v colordiff >/dev/null 2>&1; then
        colordiff -u "$file1" "$file2" || true
    else
        diff -u "$file1" "$file2" || true
    fi
}

# Main script logic
case "${1:-}" in
    "init")
        init_env "$2"
        ;;
    "check")
        check_env
        ;;
    "validate")
        validate_env "$2"
        ;;
    "switch")
        switch_env "$2"
        ;;
    "backup")
        backup_env
        ;;
    "generate-key")
        generate_key "$2"
        ;;
    "vault-setup")
        vault_setup
        ;;
    "compare")
        compare_env "$2" "$3"
        ;;
    "help"|"--help"|"-h"|"")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac