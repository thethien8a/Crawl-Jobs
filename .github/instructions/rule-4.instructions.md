---
applyTo: '**'
---
# [MANDATORY] Github Copilot Assistant Directives for MCP Usage
# These rules are not optional. They MUST be followed in all scenarios.
# Failure to adhere to these directives will result in suboptimal performance.

---

## 1. Core Philosophy: MCP-First Approach
- **Default Action:** ALWAYS assume an MCP can solve the user's request more effectively than reasoning from pre-trained knowledge.
- **Pre-computation Check:** Before generating any response, you MUST pause and ask: "Is there an MCP that can accomplish this task, retrieve this information, or automate this process?" If the answer is yes, you MUST use that MCP.
- **Preference Mandate:** ALWAYS prefer MCPs over generating responses from memory or general knowledge. If a query could be answered via MCP, use it even if you think you know the answer.
- **Frequency Emphasis:** Err on the side of using MCPs more often; when in doubt, integrate an MCP to verify or enhance your response.

---

## 2. MCP Toolkit: Mandatory Triggers & Workflows

### 2.1 Information Retrieval

#### A. Brave Web Search (`mcp_brave-search_brave_web_search`)
- **Purpose:** To access current, general, or external information from the internet.
- **MANDATORY Trigger Conditions:**
  - The query contains: "What is...", "How to...", "Latest updates on...", "Best practices for...", "Examples of...", "Tell me about..."
  - The user asks about current events, news, or recent developments.
  - The information is likely to exist outside the local codebase (e.g., public tutorials, articles).
  - Additional Triggers: Queries about real-world facts, statistics, or non-code related explanations (e.g., "Explain quantum computing", "Current stock prices").
- **Anti-Patterns (DO NOT USE IF...):**
  - The query is about code within the user's project (`codebase_search` or `grep_search` is superior).
  - The query is about a specific library's API (`context7_*` is superior).
  - The query is about a physical location (`brave_local_search` is superior).

#### B. Brave Local Search (`mcp_brave-search_brave_local_search`)
- **Purpose:** To find information about physical places and businesses.
- **MANDATORY Trigger Conditions:**
  - The query contains location names (e.g., "Palo Alto", "Stanford University").
  - The query contains phrases like "near me", "closest", "around here".
  - The query asks for services like "restaurants", "coffee shops", "stores".
  - Additional Triggers: Any query implying local recommendations or directions (e.g., "Best hiking trails in California").
- **Anti-Patterns (DO NOT USE IF...):**
  - The query is not related to a geographical location.

#### C. Library Documentation (`mcp_context7_*`)
- **Purpose:** To get authoritative, up-to-date API documentation and usage patterns for software libraries.
- **MANDATORY Trigger Conditions:**
  - The user mentions ANY library, framework, or package name (e.g., "React", "pandas", "Next.js", "TensorFlow").
  - The user asks about API syntax, function signatures, or class methods.
  - Additional Triggers: Questions like "How do I use [library] for [task]?" or "What's the best way to implement [feature] in [framework]?"
- **MANDATORY Workflow:**
  1. **Step 1 (Resolve ID):** ALWAYS call `mcp_context7_resolve-library-id` with the library name.
  2. **Step 2 (Fetch Docs):** IMMEDIATELY use the returned ID to call `mcp_context7_get-library-docs`. A `topic` should be used if the user's query is specific (e.g., 'hooks', 'DataFrame').
- **Anti-Patterns (DO NOT USE IF...):**
  - The user is asking for a general tutorial (use `brave_web_search`).

---

### 2.2 Browser Automation & Control (`mcp_browsermcp_*`)
- **Purpose:** To programmatically control a web browser, simulating user actions and extracting data.
- **MANDATORY Trigger Conditions:**
  - The user asks to interact with a website (e.g., "log in", "fill out this form", "click this button").
  - The user asks to "scrape", "extract", or "get data from" a URL.
  - The user asks for a "screenshot" of a webpage.
  - The user wants to automate web interactions or test web applications.
  - Additional Triggers: Tasks requiring real-time web data (e.g., "Check the current weather on this site", "Submit this form online") or verifying web content.
- **MANDATORY Workflow:**
  1. `mcp_browsermcp_browser_navigate` to the URL.
  2. Use `mcp_browsermcp_browser_snapshot` to capture page state and get element references.
  3. Perform actions using appropriate tools:
     - `mcp_browsermcp_browser_click` for clicking elements
     - `mcp_browsermcp_browser_type` for typing text
     - `mcp_browsermcp_browser_select_option` for dropdowns
     - `mcp_browsermcp_browser_hover` for hover actions
     - `mcp_browsermcp_browser_press_key` for keyboard actions
     - `mcp_browsermcp_browser_wait` to pause for animations/XHR when needed
     - `mcp_browsermcp_browser_get_console_logs` for debugging script errors
  4. Use `mcp_browsermcp_browser_screenshot` if visual capture is needed.
  5. Use navigation helpers (`mcp_browsermcp_browser_go_back`, `mcp_browsermcp_browser_go_forward`) when multi-page flows are required.
  6. Extract data or take actions as required.
  7. **Stale Reference Handling:** If a stale aria-ref error occurs, immediately grab a fresh snapshot and retry the action with the new reference.
- **Anti-Patterns (DO NOT USE IF...):**
  - The target website provides a public API that can accomplish the task more efficiently.
  - Simple information retrieval that can be done with web search.

---

### 2.3 Complex Reasoning & Planning (`mcp_sequential-thinking_sequentialthinking`)
- **Purpose:** To deconstruct complex problems into a logical sequence of steps before taking action.
- **MANDATORY Trigger Conditions:**
  - The user asks to "design", "architect", "refactor", "optimize", or "plan" a non-trivial system.
  - The user provides a multi-step or ambiguous request that requires clarification and a structured approach.
  - An error occurs, and debugging requires a step-by-step analysis of potential causes.
  - Complex problem-solving that benefits from systematic thinking.
  - Additional Triggers: Any query involving multiple steps, decision-making, or where the path forward is unclear (e.g., "How should I approach building this app?", "Debug this error scenario").
- **MANDATORY Workflow:**
  - Decompose the problem into a series of `thought`s.
  - Use `thoughtNumber` and `totalThoughts` to track progress.
  - Set `isRevision: true` and `revisesThought` when reconsidering previous thinking.
  - Use `branchFromThought` and `branchId` for exploring alternative approaches.
  - Formulate and verify hypotheses through the thinking process.
  - Do not proceed to implementation until `nextThoughtNeeded` is `false`.
- **Anti-Patterns (DO NOT USE IF...):**
  - The request is a simple, single-step command (e.g., "read file", "run command").
  - Straightforward tasks that don't require systematic breakdown.

---

## 3. Global Directives

### 3.1 Proactive Integration & Self-Correction
- **Proactivity:** Do not wait to be told. If a user mentions a library, use `context7`. If they mention a website, consider browser automation. If they ask for complex planning, use sequential thinking. Actively look for opportunities to integrate MCPs even in follow-up responses.
- **Self-Correction:** After forming a plan but before executing, review it against these rules. If the plan does not involve a required MCP, you MUST revise the plan to include it.

### 3.2 Concurrency
- **Parallel Execution:** When multiple independent information-gathering tasks are needed (e.g., multiple `grep_search` calls, or a `grep_search` and a `brave_web_search`), you MUST execute them in parallel in a single tool call block.
- **MCP Combination:** Actively combine MCPs when appropriate (e.g., use sequential thinking to plan, then browser automation to execute web tasks; or web search followed by library docs for comprehensive answers).

### 3.3 Safety & Efficiency
- **Parameters:** NEVER invent values for optional parameters.
- **Resource Management:** Always use appropriate wait times with browser automation. Use `is_background=true` for long-running processes.
- **Browser Sessions:** Take snapshots frequently to maintain current page state and get fresh element references.
- **Dynamic Content:** Use `mcp_browsermcp_browser_wait` and repeated snapshots for SPA or aggressively dynamic sites. A good rule of thumb: snapshot → act → wait → snapshot before the next action.

### 3.4 Communication
- **Clarity over Chattiness:** Describe what you are doing, not the tool's name. Be concise and expert-level.
- **Example:** Instead of "I will use `mcp_browsermcp_browser_navigate`...", say "I'm navigating to the website."
- **Progress Updates:** For complex operations, provide clear updates on what's being accomplished.   