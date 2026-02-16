#!/bin/bash
# Setup script for Ignite AI Agent System with Claude Code

echo "🚀 Setting up Ignite AI Agent System..."

# Create directory structure
mkdir -p ~/backbase-ignite/agents
mkdir -p ~/backbase-ignite/templates
mkdir -p ~/backbase-ignite/engagements

# Copy agent files
cp agent-1-strategy.md ~/backbase-ignite/agents/
cp agent-2-member.md ~/backbase-ignite/agents/
cp agent-3-employee.md ~/backbase-ignite/agents/
cp agent-4-architecture.md ~/backbase-ignite/agents/
cp agent-5-usecase.md ~/backbase-ignite/agents/
cp agent-6-presentation.md ~/backbase-ignite/agents/
cp agent-7-roi.md ~/backbase-ignite/knowledge/  # Knowledge reference, not active agent

# Copy master CLAUDE.md
cp CLAUDE.md ~/backbase-ignite/

# Copy templates
cp ENGAGEMENT_CONTEXT_TEMPLATE.md ~/backbase-ignite/templates/

# Copy documentation
cp CONSULTANT_GUIDE.md ~/backbase-ignite/
cp QUICK_REFERENCE.md ~/backbase-ignite/
cp CONVERSATION_STARTERS.md ~/backbase-ignite/

echo "✅ Setup complete!"
echo ""
echo "Directory structure created at ~/backbase-ignite/"
echo ""
echo "To start a new engagement:"
echo "  1. mkdir ~/backbase-ignite/engagements/[CLIENT]"
echo "  2. mkdir ~/backbase-ignite/engagements/[CLIENT]/inputs"
echo "  3. mkdir ~/backbase-ignite/engagements/[CLIENT]/outputs"
echo "  4. cp ~/backbase-ignite/templates/ENGAGEMENT_CONTEXT_TEMPLATE.md ~/backbase-ignite/engagements/[CLIENT]/ENGAGEMENT_CONTEXT.md"
echo "  5. cd ~/backbase-ignite && claude"
echo ""
echo "Then ask Claude Code to generate deliverables!"
