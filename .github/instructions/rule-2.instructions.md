---
applyTo: '**'
---
## 🧠 PROJECT CONTEXT MANAGEMENT RULES (with Serena MCP)

### 🎯 Core Philosophy: Intelligent Project Context Capture

**MANDATORY TRIGGER CONDITIONS:**
- User enters a new project workspace.
- User says "hiểu dự án này" or "understand this project".
- First time working with a project.

**GOAL:** Create a comprehensive understanding of the project context to assist the user effectively.

---

## 🚀 PROJECT INITIALIZATION WORKFLOW (Serena MCP)

### Phase 0: Pre-check (MANDATORY)
```typescript
// First, check if the project has already been onboarded by Serena
mcp_serena_check_onboarding_performed({});
// If this returns true, you can assume context exists and move to the update workflow or ask the user for the next task.
// If it returns false or fails, proceed with the initialization workflow.
```

### Phase 1: Project Discovery (If not initialized)

#### Step 1: Structure Discovery
```typescript
// Get comprehensive project overview using Serena
mcp_serena_list_dir({ relative_path: ".", recursive: true });
```

#### Step 2: Technology Stack Identification
```typescript
// Find and read the requirements file
mcp_serena_read_file({ relative_path: "requirements.txt" });
// For deeper analysis in Python projects
mcp_pylance_mcp_s_pylanceImports({ workspaceRoot: "." });
```

#### Step 3: Architecture Analysis
```typescript
// Get a high-level overview of all code symbols
mcp_serena_get_symbols_overview({ relative_path: "." });

// Find main entry points
mcp_serena_find_symbol({ name_path: "main", include_kinds: [12] }); // 12 = Function

// Find major code structures (e.g., all classes)
mcp_serena_find_symbol({ include_kinds: [5] }); // 5 = Class
```

### Phase 2: Deep Context Analysis

#### Step 4: Key Files Analysis
```typescript
// Analyze critical project files by reading them
mcp_serena_read_file({ relative_path: "README.md" });
mcp_serena_read_file({ relative_path: "CrawlJob/settings.py" }); // Example for this project
```

#### Step 5: Code Patterns Discovery
```typescript
// Find architectural patterns like Pipelines or specific Spider classes
mcp_serena_find_symbol({ name_path: "Pipeline", substring_matching: true, include_kinds: [5] });
mcp_serena_find_symbol({ name_path: "Spider", substring_matching: true, include_kinds: [5] });
```

#### Step 6: Database & Configuration Analysis
```typescript
// Use pattern search to find all database-related code
mcp_serena_search_for_pattern({ substring_pattern: "database|sql|pymssql", relative_path: "." });

// Find all configuration settings
mcp_serena_search_for_pattern({ substring_pattern: "settings", relative_path: "." });
```

### Phase 3: Documentation & Summarization

#### Step 7: Create Project Overview in Serena's Memory
```typescript
// After analysis, create a summary file for future reference in Serena's memory
mcp_serena_write_memory({
    memory_name: "project-overview.md",
    content: "# Project Overview\n\n## Technology Stack\n- Python, Scrapy, pymssql\n\n## Architecture\n- Scrapy-based (Spiders, Items, Pipelines)\n- Data stored in SQL Server."
});
```

---

## ⚠️ FALLBACK WORKFLOW (If Serena MCP is unavailable)

*If Serena MCP tools are not responding or available, revert to the standard VS Code tool workflow.*

### Phase 1: Project Discovery (VS Code Tools)

#### Step 1: Structure Discovery
```typescript
// Get comprehensive project overview
list_dir({ path: ".", recursive: true });
```

#### Step 2: Technology Stack Identification
```typescript
// Identify key technologies and frameworks by looking for manifest files
grep_search({ query: "requirements\\.txt|package\\.json|pom\\.xml|build\\.gradle|Cargo\\.toml|go\\.mod", isRegexp: true });
// Look for containerization and environment files
grep_search({ query: "Dockerfile|docker-compose|\\.env", isRegexp: true });
```

#### Step 3: Architecture Analysis
```typescript
// Understand project structure and patterns
// Find main entry points
grep_search({ query: "main|app|index|startup", isRegexp: true });
// Find major code structures
grep_search({ query: "class|interface|struct", isRegexp: true });
// Find how modules are connected
grep_search({ query: "import|from|require|using", isRegexp: true });
```

### Phase 2: Deep Context Analysis (VS Code Tools)

#### Step 4: Key Files Analysis
```typescript
// Analyze critical project files by reading them
read_file({ filePath: "README.md", startLine: 1, endLine: 9999});
read_file({ filePath: "requirements.txt", startLine: 1, endLine: 9999});
```

### Phase 3: Documentation & Summarization (VS Code Tools)

#### Step 5: Create Project Overview
```typescript
// After analysis, create a summary file for future reference
create_file({
    filePath: ".github/PROJECT_OVERVIEW.md",
    content: "# Project Overview\n\n## Technology Stack\n- ...\n\n## Architecture\n- ..."
});
```

---

## 🔄 PROJECT CONTEXT UPDATE WORKFLOW

### Trigger: "cập nhật context dự án"

#### Step 1: Current State Assessment
```typescript
// Read existing overview from Serena's memory
mcp_serena_read_memory({ memory_file_name: "project-overview.md" });
```

#### Step 2: Change Detection
```typescript
// Use git to see what has changed
get_changed_files({});

// Look for comments indicating changes
mcp_serena_search_for_pattern({ substring_pattern: "TODO|FIXME|HACK", relative_path: "." });
```

#### Step 3: Incremental Analysis
```typescript
// Focus on new or modified files identified in the previous step
// Read and analyze the changed files using mcp_serena_read_file or mcp_serena_get_symbols_overview
```

#### Step 4: Update Documentation
```typescript
// Update the project overview in Serena's memory
mcp_serena_write_memory({
    memory_name: "project-overview.md",
    content: "..." // New, updated content
});
```

---

## 📋 DOCUMENTATION TEMPLATES & STRUCTURE

### Project Overview Template
```markdown
# Project: [Project Name]

## 🎯 Project Purpose
- **Primary Goal**: [Main objective]
- **Key Features**: [Core functionality]

## 🏗️ Architecture Overview
- **Technology Stack**: [Languages, frameworks, databases]
- **Architecture Pattern**: [MVC, Microservices, etc.]
- **Deployment**: [How it's deployed]

## 📁 Project Structure
- **Root Directories**: [Key folders and their purposes]
- **Entry Points**: [Main files that start the application]
- **Configuration**: [Where settings are stored]

## 🔧 Development Setup
- **Dependencies**: [How to install requirements]
- **Build Process**: [How to build/run the project]
```

---

## 🎯 INTELLIGENT CONTEXT UPDATE RULES

### Rule #1: Context-Aware Updates
```
WHEN UPDATING DOCUMENTATION:
✅ Focus on structural changes (new files, deleted files, moved components)
✅ Identify new patterns or conventions
✅ Update technology stack if new dependencies added
✅ Track architectural evolution

❌ DON'T UPDATE FOR:
- Minor code changes without architectural impact
- Temporary files or build artifacts
```

### Rule #2: Change Detection Strategy
```
DETECT CHANGES BY:
- Using `get_changed_files()`
- Looking for new file patterns with `list_dir`
- Identifying new dependencies in manifest files
- Analyzing updated configuration files
```

### Rule #3: Validation
```
BEFORE WRITING DOCUMENTATION:
✅ Verify information is accurate and current
✅ Ensure consistency
✅ Validate that file paths and references are correct
```

---

## 🚀 IMPLEMENTATION COMMANDS

### For New Project:
```typescript
// User says: "hiểu dự án này" or enters new project
// Follow Phase 1-3 workflow above
```

### For Context Update:
```typescript
// User says: "cập nhật context dự án"
// Follow Project Context Update Workflow above
```

### For Quick Context Check:
```typescript
// User asks about project understanding
read_file({ filePath: ".github/PROJECT_OVERVIEW.md", startLine: 1, endLine: 9999 });
// Provide summary based on the file
```

---