#!/bin/bash
# dev-setup.sh - Set up local development environment for testing skills and agents
#
# This script creates symlinks from your local bigquery-etl-skills repo to ~/.claude,
# allowing you to test changes to skills and agents before committing.
#
# Usage:
#   ./scripts/dev-setup.sh          # Set up symlinks
#   ./scripts/dev-setup.sh --clean  # Remove symlinks

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
CLAUDE_DIR="$HOME/.claude"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

clean() {
    info "Cleaning up development symlinks..."

    # Remove skills symlinks
    if [ -L "$CLAUDE_DIR/skills/bigquery-etl-skills" ]; then
        rm "$CLAUDE_DIR/skills/bigquery-etl-skills"
        info "Removed skills symlink"
    fi

    # Remove agents symlinks
    for agent in "$REPO_ROOT/agents"/*.md; do
        if [ -f "$agent" ]; then
            agent_name=$(basename "$agent")
            if [ -L "$CLAUDE_DIR/agents/$agent_name" ]; then
                rm "$CLAUDE_DIR/agents/$agent_name"
                info "Removed agent symlink: $agent_name"
            fi
        fi
    done

    info "Cleanup complete"
}

setup() {
    info "Setting up local development environment..."
    info "Repo root: $REPO_ROOT"

    # Create ~/.claude directories if they don't exist
    mkdir -p "$CLAUDE_DIR/skills"
    mkdir -p "$CLAUDE_DIR/agents"

    # Symlink skills directory
    # The plugin format expects skills to be in a named subdirectory
    if [ -L "$CLAUDE_DIR/skills/bigquery-etl-skills" ]; then
        warn "Skills symlink already exists, removing..."
        rm "$CLAUDE_DIR/skills/bigquery-etl-skills"
    elif [ -d "$CLAUDE_DIR/skills/bigquery-etl-skills" ]; then
        error "A directory exists at $CLAUDE_DIR/skills/bigquery-etl-skills"
        error "Please remove it manually or run with --clean first"
        exit 1
    fi

    ln -s "$REPO_ROOT/skills" "$CLAUDE_DIR/skills/bigquery-etl-skills"
    info "Created skills symlink: ~/.claude/skills/bigquery-etl-skills -> $REPO_ROOT/skills"

    # Symlink each agent file individually
    for agent in "$REPO_ROOT/agents"/*.md; do
        if [ -f "$agent" ]; then
            agent_name=$(basename "$agent")
            target="$CLAUDE_DIR/agents/$agent_name"

            if [ -L "$target" ]; then
                rm "$target"
            elif [ -f "$target" ]; then
                warn "Agent file exists (not a symlink): $target - skipping"
                continue
            fi

            ln -s "$agent" "$target"
            info "Created agent symlink: ~/.claude/agents/$agent_name"
        fi
    done

    echo ""
    info "Setup complete!"
    echo ""
    echo "To test your changes:"
    echo "  1. Start a new Claude Code session: claude"
    echo "  2. Your local skills and agents are now active"
    echo "  3. Changes to files in this repo are reflected immediately"
    echo ""
    echo "To clean up when done:"
    echo "  ./scripts/dev-setup.sh --clean"
}

# Main
case "${1:-}" in
    --clean|-c)
        clean
        ;;
    --help|-h)
        echo "Usage: $0 [--clean|--help]"
        echo ""
        echo "Set up local development environment for testing skills and agents."
        echo ""
        echo "Options:"
        echo "  --clean, -c    Remove development symlinks"
        echo "  --help, -h     Show this help message"
        echo ""
        echo "Without arguments, creates symlinks for local testing."
        ;;
    "")
        setup
        ;;
    *)
        error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
