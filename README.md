# 🚀 Smarketer Pro: The Enterprise Agentic CRM & Growth OS

**Smarketer Pro** is an enterprise-grade, Multi-Agent AI System designed to automate the entire lifecycle of B2B lead generation, qualification, hyper-personalized outreach, and relationship management. It merges a powerful **Headless Automation Engine** with a premium **Mission Control** dashboard to provide a unified "Growth Operating System."

---

## 🌟 The Vision

In an era of generic automation, Smarketer Pro provides **Agentic Intelligence**. Instead of simple scripts, it deploys a coordinated workforce of specialized AI agents that think, research, and execute like a high-performing sales and marketing team.

---

## 🧠 The Agentic Workforce

Smarketer Pro is powered by over 30 specialized AI agents, categorized by their domain expertise:

### 🏛️ Core Leadership & Strategy

* **👨‍💼 Manager Agent**: The orchestrator. Plans complex missions, delegates tasks, and ensures alignment across the agentic workforce.
* **📋 Product Manager Agent**: Translates business ideas into technical specs and strategic outreach blueprints.
* **⚖️ Qualifier Agent**: The gatekeeper. Evaluates leads against the Ideal Customer Profile (ICP) using multi-dimensional scoring.

### 🔍 Research & Intelligence

* **🕵️ Researcher Agent**: Performs deep-web scraping and analysis of prospect websites, tech stacks, and team structures.
* **📻 Social Listener Agent**: Monitors social signals and trends to identify high-intent conversion windows.
* **🔍 SEO Expert Agent**: Audits on-page SEO and identifies keyword opportunities for B2B targets.
* **📊 Strategy Reporter**: Synthesizes massive datasets into actionable boardroom-ready reports.

### ✍️ Content & Creative Production

* **✍️ Copywriter Agent**: Crafts hyper-personalized, context-aware email sequences, LinkedIn messages, and blog posts.
* **🎨 Designer Agent**: Generates custom visual assets, social media thumbnails, and branded imagery.
* **🎥 Video Agent**: Creates personalized video scripts and coordinates AI video generation for high-touch outreach.
* **✍️ Syntax Agent**: Ensures all generated content is grammatically flawless and follows brand-specific style guides.

### ⚙️ Technical & Automation Specialists

* **🌐 WordPress Agent**: Automates site management, content publishing, and DSR (Digital Sales Room) deployment.
* **🛡️ Proxy Agent**: Manages the life cycle of thousands of proxies, ensuring high anonymity and zero blocking.
* **🤖 Account Creator Agent**: Automates the complex process of setting up and warming up outreach accounts.
* **🛠️ Artifact Designer**: Generates interactive web artifacts (React/Tailwind) for personalized prospect experiences.

---

## 🏢 Core Ecosystem Modules

The Smarketer Pro ecosystem is organized into five primary functional categories, each designed to handle a critical phase of the growth lifecycle.

### 🏠 Command Center: The Central Intelligence Hub

The Command Center is where high-level strategy meets real-time execution monitoring.

* **Dashboard**: A premium visual overview of your entire operation. It tracks "Pipeline Value," "Active Agent Missions," and system health metrics. It serves as the primary "Situation Room" for sales leaders.
* **CRM Dashboard**: A robust lead and deal management system. It features a dual-view interface (Kanban for deal flow and an Enhanced Table for bulk lead triage). It includes automated task management to ensure no prospect falls through the cracks.
* **Performance Reports**: Generates boardroom-ready PDF reports. It uses the **Strategy Reporter agent** to synthesize complex outreach data into clear ROI metrics and growth insights.
* **Manager Console**: A persistent, agent-aware terminal. It allows you to speak directly to the **Manager Agent**, issue natural language commands, and oversee the "Polymorphic" reasoning of the system.

### 📣 Outreach Engine: Multi-Channel Execution

This category handles the heavy lifting of finding and engaging prospects across the web.

* **Campaigns**: The lifecycle controller for outreach. Define hyper-personalized email sequences, set cadence rules, and use "AI Optimize" to let the **Copywriter Agent** refine your messaging in real-time.
* **Lead Discovery**: A mass-harvesting interface powered by **SearXNG**. Enter industry queries and let the **Researcher Agent** find, qualify, and enrich leads with a single click.
* **Affiliate Hub**: A dual-sided partnership portal. It acts as a **Publisher Vault** (managing your own affiliate links) and a **Partner Center** (managing affiliates who promote you), complete with an attribution ledger.
* **Digital Sales Room (DSR)**: creates personalized, AI-generated microsites for high-value prospects. It coordinates the **WordPress Agent** and **Designer Agent** to deploy branded landing pages that feel like custom-built proposals.
* **Social Pulse & Scheduler**: Plan and schedule post across LinkedIn, Twitter, and Reddit. Use the **Social Listener** to identify viral trends and engage with high-intent conversations automatically.

### ✨ Creative Studio: High-Impact Asset Production

The Creative Studio centralizes the production of all visual and technical marketing assets.

* **Designer**: An AI-native design workspace. It leverages the **Graphics Designer agent** to create social thumbnails, blog headers, and personalized outreach images based on prospect research.
* **Video Studio**: Orchestrates the generation of personalized video outreach. It scripts content and coordinates with external video AI providers to create "Human-in-the-Loop" video messages.
* **WordPress Manager**: A centralized fleet management tool. Monitor the health, security, and content status of all your outreach-related WordPress sites from a single dashboard.

### 🛠️ Strategic Tools: The Laboratory

Advanced tools for power users to tune the engine and manage infrastructure.

* **Agent Lab**: A dedicated "Prompt Engineering" sandbox. Test individual agents (Researcher, Qualifier, etc.) with custom inputs to refine their "Digital Personas" and output quality.
* **Automation Hub**: The home of "Autonomous Missions." Launch long-running agent loops that operate 24/7, processing workflows without manual intervention.
* **Product Lab**: Uses the **Product Manager Agent** to turn vague "ideas" into full technical specs, competitor audits, and marketing strategies.
* **Proxy Lab**: A ScrapeBox-style management suite. It monitors the **Smart Proxy Harvester**, manages IP rotation, and performs L3 anonymity checks to ensure zero-blocking.
* **Account Creator**: An automated registration suite for spinning up and "warming up" new outreach accounts across various platforms.

### ⚙️ Admin: System Configuration

* **Settings**: Securely manage global API keys for LLMs (OpenAI, Gemini, Groq), search providers, and SMTP routing. It features a "Smart Router" configuration to optimize model costs vs. intelligence.

---

## 🛠️ Technical Architecture

### 🚀 Automation Engine (`src/engine/`)

The heart of the system is a modular, node-based engine that interprets JSON-based workflows. It supports:

* **Parallel Execution**: Handle multiple agent tasks concurrently.
* **Failover Logic**: Automatically retry or switch models if an agent fails.
* **State Persistence**: Full mission history stored in SQLite for audit and recovery.

### 🔍 SearXNG Search Core

Smarketer Pro utilizes a self-hosted **SearXNG** instance to aggregate results from Google, Bing, DuckDuckGo, Reddit, and 70+ other engines without being blocked or tracked.

### 🛡️ Smart Proxy Harvester

A built-in management layer that:

* **Scrapes & Validates**: Continuously pulls fresh proxies from public and private sources.
* **L3 Anonymity Checking**: Verifies proxies for "Elite" status before use.
* **Dynamic Rotation**: Rotates IPs for every search query and scraping task.

### 🧠 LLM Smart Router

Optimized for cost and intelligence, the router pattern:

* **Benchmarks Models**: Measures latency and accuracy across Gemini, Groq, and OpenAI.
* **Dynamic Assignment**: Uses "smart" models (GPT-4/Gemini Pro) for reasoning and "fast" models (Llama 3/Flash) for bulk processing.

---

## 🚀 Getting Started

### 1. Prerequisites

* **Python 3.10+** (Recommended: 3.11)

* **Docker Desktop** (Required for SearXNG)
* **Git**

### 2. Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/your-org/smarketer-pro.git
    cd smarketer-pro
    ```

2. **Setup Virtual Environment**

    ```bash
    python -m venv .venv
    .venv\Scripts\activate  # Windows
    source .venv/bin/activate  # Mac/Linux
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Launch Dependencies (SearXNG)**

    ```bash
    cd searxng
    docker-compose up -d
    cd ..
    ```

### 3. Initial Run

Launch the Mission Control dashboard:

```bash
streamlit run src/app.py
```

---

## 🛡️ Security & Ethics

Smarketer Pro is designed for **ethical outreach**.

* **Rate Limiting**: Built-in adherence to platform-specific limits.
* **Data Privacy**: All lead data is stored locally in your SQLite instance.
* **Transparency**: Every agent action is logged and auditable in the Mission Control.

---

## 🗺️ Roadmap

* [ ] **Interactive Artifacts**: Real-time generation of React-based sales calculators and tools.

* [ ] **Multi-Workspace Sync**: Synchronize leads across multiple client accounts.
* [ ] **Voice Intelligence**: Direct integration with ElevenLabs for AI-driven phone follow-ups.

---

*Built for the Autonomous Future.*
