---
applyTo: '**'
---
# 🎯 MANDATORY RULES FOR GITHUB COPILOT IN VS CODE WORKFLOW

## 📖 File Reading Priority
**RULE #1: Use available tools to read files.**
- Use `read_file` to read specific line ranges from a file.
- Use `grep_search` to quickly find specific patterns or get an overview of a file's content.
- Use `semantic_search` to find relevant code snippets based on natural language queries.

- **Example**:
```typescript
// To read the first 100 lines of a file
read_file({ filePath: "path/to/file.py", startLine: 1, endLine: 100 });

// To find all functions in a file
grep_search({ query: "def ", includePattern: "path/to/file.py", isRegexp: false });
```

## ✏️ File Creation/Editing Priority  
**RULE #2: Use the appropriate tool for file modifications.**
- **`create_file`**: To create a new file with specified content.
- **`replace_string_in_file`**: The primary tool for editing existing files. Be specific with the `oldString` to ensure unique replacement.
- **`insert_edit_into_file`**: Use as a fallback if `replace_string_in_file` fails or for complex insertions.

- **Example**:
  ```typescript
  // Create a new file
  create_file({ filePath: "path/to/new_file.py", content: "print('Hello, World!')" });

  // Replace a string in a file
  replace_string_in_file({
    filePath: "path/to/existing_file.py",
    oldString: "print('Hello, World!')",
    newString: "print('Hello, VS Code!')"
  });
  ```

## 🔄 Workflow Decision Tree

### For File Reading:
```
1. Need to understand a file's overall structure? -> `list_dir` then `read_file` on key files.
2. Looking for a specific string or pattern? -> `grep_search`.
3. Searching for code by concept? -> `semantic_search`.
4. Need to read a specific part of a file? -> `read_file` with line numbers.
```

### For File Creation/Editing:
```
1. Creating a new file? -> `create_file`.
2. Making changes to an existing file? -> Start with `replace_string_in_file`.
3. If `replace_string_in_file` is not suitable? -> Use `insert_edit_into_file`.
4. If both fail -> Report error to user.
```

## ⚡ Quick Reference Commands

### Reading Files:
```typescript
// Get file/directory structure
list_dir({ path: "./" });

// Read a whole file
read_file({ filePath: "file.py", startLine: 1, endLine: 9999 });

// Grep for a pattern
grep_search({ query: "my_function", isRegexp: false });
```

### Creating Files:
```typescript
// Preferred method
create_file({ filePath: "new_file.py", content: "# New file content" });
```

### Editing Files:
```typescript
// Preferred method
replace_string_in_file({
  filePath: "existing_file.py",
  oldString: "old_function_name",
  newString: "new_function_name"
});

// Fallback method
insert_edit_into_file({
    filePath: "existing_file.py",
    code: "//...existing code...\nnew_function_name()",
    explanation: "Update function call"
});
```

## 🎯 Success Criteria
- **File Reading**: Always get file content successfully using the most appropriate tool.
- **File Operations**: Complete file creation/editing with proper error handling.
- **User Experience**: Seamless workflow without manual intervention.
- **Error Reporting**: Clear communication when tool operations fail.

## 📝 Best Practices
1. **Always try the most specific tool first** (e.g., `grep_search` over `read_file` if looking for a pattern).
2. **Handle errors gracefully.**
3. **Maintain consistency across the project.**

## 🚨 Error Handling
- If a tool fails, analyze the error message and try to correct the parameters.
- If a file edit fails, read the file again to get the latest content before retrying.
- If all attempts fail, provide a clear error message to the user.