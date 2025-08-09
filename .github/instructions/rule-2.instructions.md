---
applyTo: '**'
---
## 🧠 PROJECT CONTEXT MANAGEMENT RULES

### 🎯 Core Philosophy: Intelligent Project Context Capture

**MANDATORY TRIGGER CONDITIONS:**
- User enters a new project workspace.
- User says "hiểu dự án này" or "understand this project".
- First time working with a project.

**GOAL:** Create a comprehensive understanding of the project context to assist the user effectively.

---

## 🚀 PROJECT INITIALIZATION WORKFLOW

### Phase 1: Project Discovery (MANDATORY)

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

### Phase 2: Deep Context Analysis

#### Step 4: Key Files Analysis
```typescript
// Analyze critical project files by reading them
const critical_files = [
    "README.md", "CHANGELOG.md", "LICENSE",
    "requirements.txt", "package.json",
    "Dockerfile", "docker-compose.yml", ".env.example",
    "src/", "app/", "main/"
];
// Example for one file:
read_file({ filePath: "README.md", startLine: 1, endLine: 9999});
```

#### Step 5: Code Patterns Discovery
```typescript
// Find architectural patterns and conventions
grep_search({ query: "def main|if __name__|public static void main|func main", isRegexp: true });
grep_search({ query: "class.*Controller|class.*Service|class.*Repository|class.*Model", isRegexp: true });
```

#### Step 6: Database & Configuration Analysis
```typescript
// Database and configuration patterns
grep_search({ query: "database|db|sql|mongo|redis|postgres|mysql", isRegexp: true });
grep_search({ query: "config|settings|environment|env|properties", isRegexp: true });
```

### Phase 3: Documentation & Summarization

#### Step 7: Create Project Overview
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
// Read existing overview to understand current context
read_file({ filePath: ".github/PROJECT_OVERVIEW.md", startLine: 1, endLine: 9999 });
```

#### Step 2: Change Detection
```typescript
// Use git to see what has changed
get_changed_files({});

// Look for comments indicating changes
grep_search({ query: "TODO|FIXME|HACK|NOTE|CHANGED|UPDATED", isRegexp: true });
```

#### Step 3: Incremental Analysis
```typescript
// Focus on new or modified files identified in the previous step
// Read and analyze the changed files
```

#### Step 4: Update Documentation
```typescript
// Update the project overview file with new information
replace_string_in_file({
    filePath: ".github/PROJECT_OVERVIEW.md",
    oldString: "...",
    newString: "..."
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