# 🚀 Smarketer Pro: CRM & Growth OS

**Smarketer Pro** (formerly B2B Outreach Tool) is an enterprise-grade, Multi-Agent AI System designed to automate the entire lifecycle of lead generation, qualification, outreach, and relationship management. It combines a powerful "Headless" automation engine with a premium "Mission Control" dashboard.

---

## ✨ Key Features

### 🧠 The Agentic Workforce

This system is not just a script; it is a coordinated team of specialized AI agents:

* **👨‍💼 Manager Agent**: The strategist. Plans campaigns, delegates tasks to other agents, and oversees mission execution.
* **🕵️ Researcher Agent**: The scout. Performs deep-dive analysis on prospect websites, extracting pain points, tech stacks, and team information.
* **⚖️ Qualifier Agent**: The gatekeeper. Strictly evaluates leads against your Ideal Customer Profile (ICP) to ensure quality over quantity.
* **✍️ Copywriter Agent**: The creative. Crafts hyper-personalized emails, LinkedIn messages, and articles based on research data and proven frameworks.
* **🎨 Designer Agent**: The artist. Generates custom visual assets (thumbnails, social images) to accompany outreach.
* **🛡️ Reviewer Agent**: The QA. Double-checks content quality and brand alignment before anything goes out.

### 🏢 Integrated CRM & Pipeline

* **Kanban Pipeline**: Drag-and-drop deal management (Discovery -> Closed Won).
* **Task Management**: Automated and manual task tracking for sales follow-ups.
* **DSR Manager**: Digital Sales Room creation for personalized client proposals.

### 🔍 Advanced Discovery Engine

* **Multi-Engine Search**: Aggregates results from Google, Bing, DuckDuckGo, and more via a self-hosted **SearXNG** instance.
* **Smart Proxy Harvester**: Built-in proxy management that scrapes, validates, and rotates thousands of proxies to ensure high anonymity and zero blocking.
* **Lead Enrichment**: Automatically finds emails, phone numbers, and social profiles.

### ⚙️ Automation Hub

* **Autonomous Missions**: Launch long-running campaigns where agents work in the background 24/7.
* **Workflow Engine**: Define complex, multi-step logic using JSON-based workflows (e.g., "Find Leads -> Qualify -> Enrich -> Email").
* **Agency Orchestrator**: Manage multiple client workspaces and campaigns from a single view.

---

## 🛠️ Architecture

The system is built on a modular "neuronal" architecture:

| Component | Description |
| :--- | :--- |
| **`src/app.py`** | The main **Streamlit** application entry point. Renders the UI and manages session state. |
| **`src/workflow.py`** | The CLI "Headless" runner for high-speed, background execution. |
| **`src/agents/`** | Contains the brain logic for each individual agent class. |
| **`src/engine/`** | The core **Automation Engine** that interprets JSON workflows and executes nodes. |
| **`searxng/`** | Docker configuration for the private search engine instance. |
| **`config.yaml`** | Central nervous system configuration (API keys, models, thresholds). |

---

## 🚀 Getting Started

### 1. Prerequisites

* **Python 3.10+**
* **Docker Desktop** (Required for SearXNG search engine)
* **API Keys**: You will need at least one LLM provider (Gemini, Groq, OpenAI, or OpenRouter).

### 2. Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/your-repo/b2b-outreach-tool.git
    cd b2b-outreach-tool
    ```

2. **Create Virtual Environment**

    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Start Search Engine (SearXNG)**
    This is *critical* for the Researcher Agent to function.

    ```bash
    cd searxng
    docker-compose up -d
    cd ..
    ```

### 3. Configuration

1. **Environment Variables**: Create a `.env` file in the root directory.

    ```env
    # LLM Providers (Add what you have)
    GEMINI_API_KEY=your_key_here
    GROQ_API_KEY=your_key_here
    OPENAI_API_KEY=your_key_here
    
    # Email (For outreach)
    SMTP_USER=your_email@gmail.com
    SMTP_PASS=your_app_password
    ```

2. **System Config (`config.yaml`)**:
    The generic settings are in `config.yaml`. usage:
    * **`llm.router`**: Configure which models handle which tasks (Cheap models for bulk work, smart models for reasoning).
    * **`search.profiles`**: Define search types (e.g., `tech` searches Github/StackOverflow, `social` searches LinkedIn/Twitter).
    * **`proxies`**: Enable/disable the internal proxy harvester.

---

## 🖥️ Usage Guide

### Option A: The Mission Control (Web UI)

Recommended for most users.

```bash
streamlit run src/app.py
```

* **Dashboard**: High-level metrics and quick actions.
* **Campaigns**: Create and manage outreach campaigns. Use the "AI Optimize" button to let agents rewrite your copy.
* **Lead Discovery**: The manual search interface. Enter a query (e.g., "SaaS Startups in Austin") and watch agents hunt.
* **Automation Hub**: The "Set and Forget" mode. Load a strategy and let the Manager Agent take over.
* **Proxy Lab**: Manage your IP rotation and scrape fresh proxies.

### Option B: The Headless Runner (CLI)

Best for cron jobs or high-volume background processing.

```bash
python src/workflow.py "your search query" --niche "your target industry"
```

*Example:*

```bash
python src/workflow.py "Plumbers in Chicago" --niche "Home Services" --profile "local_business"
```

---

## 🧩 Advanced Configuration

### LLM Smart Router

The system uses a "Router" pattern to save costs. It defaults to faster/cheaper models (like **Groq Llama 3**) for simple tasks and switches to high-intelligence models (like **Gemini 1.5 Pro** or **GPT-4**) for complex reasoning.

To tweak this, edit `config.yaml` under `llm.router.candidates`. The system will automatically benchmark available models on startup.

### Customizing Workflows

Workflows are defined in `src/workflows/*.json`. You can create your own "SOPs" (Standard Operating Procedures) by chaining nodes together.

**Example Task Workflow:**

```json
{
  "name": "Quick Audit",
  "nodes": [
    {"id": "1", "type": "agent.researcher", "action": "audit_site"},
    {"id": "2", "type": "agent.copywriter", "action": "write_report"}
  ]
}
```

---

## 🛡️ Troubleshooting

* **Search failing?** Check if Docker is running (`docker ps`). SearXNG must be active on port 8081.
* **Agents "hallucinating"?** Switch to a more capable model in `config.yaml` (e.g., set `llm.provider: openai`).
* **Proxy errors?** Go to the **Proxy Lab** in the UI and click "Trigger Mass Harvest" to refresh your IP pool.

---

*Built for the Autonomous Future.*
