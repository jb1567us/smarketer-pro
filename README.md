# 🚀 B2B Outreach Tool

An industry-agnostic, multi-agent AI system for high-volume, quality-driven lead generation and personalized outreach.

## ✨ Key Features

- **🧠 Multi-Agent Orchestration**: A specialized workforce of AI agents:
  - **Manager**: Plans campaigns and delegates tasks.
  - **Researcher**: Deep-dives into prospect websites to find pain points.
  - **Qualifier**: Gates leads against your Ideal Customer Profile (ICP).
  - **Copywriter**: Crafts hyper-personalized, relevant outreach copy.
  - **Designer**: Generates custom visual assets for campaigns.
- **💎 Premium Web Interface**: A sleek Streamlit dashboard featuring:
  - Interactive **Campaign Manager** with a guided stepper workflow.
  - Real-time **Lead Discovery** with visual status indicators.
  - Automated **Niche Analysis** and ICP definition tools.
- **🛡️ Quality Gate (ICP Verification)**: AI-driven filtering ensures you only outreach to high-relevance leads, saving resources and protecting your domain reputation.
- **🔌 Smart LLM Router**: Seamless integration with Groq, OpenAI, Gemini, Cohere, and OpenRouter with automatic provider verification and failover.
- **🔍 Advanced Search Engine**: Integrated SearXNG backend for privacy-focused, multi-engine results with intelligent domain blocklists.

## 🛠️ Getting Started

### 1. Prerequisites

- Python 3.10+
- Docker (for SearXNG)

### 2. Installation

```powershell
pip install -r requirements.txt
```

### 3. Setup SearXNG

```powershell
cd searxng
docker-compose up -d
cd ..
```

### 4. Configuration

Create a `.env` file or set environment variables:

- `GROQ_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, etc.
- `SMTP_USER`, `SMTP_PASS` (for email outreach)
- `DATABASE_URL` (optional, defaults to `leads.db`)

## 🚀 Usage

### Web Application (Recommended)

Launch the premium dashboard to manage campaigns visually:

```powershell
streamlit run src/app.py
```

### Command Line

Run the workflow directly for high-speed lead discovery:

```powershell
python src/workflow.py "your search query" --niche "target industry"
```

*Example:* `python src/workflow.py "AI startups Austin" --niche "SaaS companies"`

## 📂 Project Structure

- `src/agents/`: Specialized AI agent definitions.
- `src/llm/`: Smart router and provider abstractions.
- `src/ui/`: Streamlit dashboard components and styles.
- `src/workflow.py`: Core orchestration logic for lead processing.
- `config.yaml`: Central configuration for search engines, blocklists, and ICP defaults.

---
*Built with ❤️ for advanced agentic outreach.*
*Built with ❤️ for advanced agentic outreach.*
