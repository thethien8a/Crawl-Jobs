# Workflow Preferences (CrawlJob)

## 🎯 **Preferred Development Patterns**

### Spider Development
- **Selector Priority**: CSS selectors > XPath (better readability)
- **Error Handling**: Always use try-catch with fallback selectors
- **Rate Limiting**: Respect robots.txt and implement delays
- **Data Validation**: Check for empty/null values before yielding items
- **Logging**: Use spider.logger.info/error for debugging

### Database Operations
- **Connection Management**: Always use context managers for DB connections
- **Transaction Safety**: Wrap operations in try-except with rollback
- **Query Optimization**: Use parameterized queries to prevent SQL injection
- **Indexing Strategy**: Index on frequently queried fields (source_site, created_at)
- **Migration Safety**: Always test migrations on development data first

### API Design
- **RESTful Standards**: Use proper HTTP methods and status codes
- **Pagination**: Implement consistent pagination across all endpoints
- **Validation**: Use Pydantic models for request/response validation
- **Documentation**: Leverage FastAPI's automatic OpenAPI documentation
- **CORS**: Configure appropriately for frontend integration

### Frontend Development
- **Responsive First**: Mobile-first design with Bootstrap breakpoints
- **Progressive Enhancement**: Core functionality works without JavaScript
- **Performance**: Minimize API calls, implement loading states
- **Accessibility**: Use semantic HTML and ARIA labels
- **Error Handling**: User-friendly error messages and fallback states

## 🔧 **Code Style Guidelines**

### Python Standards
- **PEP 8**: Follow Python style guidelines
- **Type Hints**: Use typing for function parameters and return types
- **Docstrings**: Document all functions, classes, and modules
- **Imports**: Organize imports (standard library, third-party, local)
- **Constants**: Use UPPER_CASE for constants

### Scrapy Best Practices
- **Spider Naming**: Use descriptive, lowercase names
- **Item Design**: Create comprehensive items with all possible fields
- **Pipeline Order**: Process items in logical order (validation → cleaning → storage)
- **Settings**: Use project settings instead of hardcoded values
- **Extensions**: Leverage Scrapy's built-in extensions for common tasks

### JavaScript Standards
- **ES6+**: Use modern JavaScript features
- **Async/Await**: Prefer over Promise chains for readability
- **Error Handling**: Use try-catch for API calls
- **DOM Manipulation**: Use modern APIs (querySelector, addEventListener)
- **Performance**: Debounce search inputs to reduce API calls

## 🚀 **Deployment Preferences**

### Environment Configuration
- **Environment Variables**: Use .env files for all configuration
- **Secrets Management**: Never commit credentials to version control
- **Configuration Hierarchy**: Default → Environment → Runtime overrides
- **Validation**: Validate required environment variables on startup
- **Documentation**: Document all required environment variables

### Production Considerations
- **Logging**: Structured logging with appropriate levels
- **Monitoring**: Implement health checks and metrics
- **Backup**: Regular database backups and log rotation
- **Security**: Use HTTPS, validate inputs, sanitize outputs
- **Performance**: Implement caching, connection pooling, query optimization

### Automation Strategy
- **Scheduling**: Use Windows Task Scheduler for production
- **Monitoring**: Implement comprehensive logging and alerting
- **Recovery**: Design for failure with automatic retry mechanisms
- **Scaling**: Plan for horizontal scaling and load balancing
- **Updates**: Implement rolling updates with zero downtime

## 🐛 **Debugging Preferences**

### Spider Debugging
- **Shell Testing**: Use scrapy shell for selector testing
- **Step-by-Step**: Debug with print statements and logging
- **Network Inspection**: Use browser dev tools for AJAX requests
- **Data Inspection**: Save sample responses for testing
- **Performance Analysis**: Monitor execution time and memory usage

### Database Debugging
- **Query Analysis**: Use SQL Server Profiler for slow queries
- **Connection Testing**: Verify connection strings and permissions
- **Data Validation**: Check data integrity and constraints
- **Index Analysis**: Monitor index usage and fragmentation
- **Backup Testing**: Regularly test backup and restore procedures

### API Debugging
- **Request Inspection**: Use curl and browser dev tools
- **Response Analysis**: Validate JSON structure and data types
- **Performance Testing**: Monitor response times and throughput
- **Error Analysis**: Check error codes and messages
- **Integration Testing**: Test with frontend applications

## 📊 **Testing Strategy**

### Unit Testing
- **Spider Testing**: Test individual parsing functions
- **Pipeline Testing**: Test data transformation and validation
- **Utility Testing**: Test helper functions and utilities
- **API Testing**: Test endpoint responses and error handling
- **Integration Testing**: Test end-to-end data flow

### Manual Testing
- **Spider Verification**: Check selector accuracy and data completeness
- **API Testing**: Test all endpoints with various parameters
- **UI Testing**: Test responsive design and user interactions
- **Performance Testing**: Monitor system behavior under load
- **Error Testing**: Test error scenarios and recovery mechanisms

## 🔄 **Maintenance Workflow**

### Regular Tasks
- **Log Rotation**: Archive old log files
- **Data Cleanup**: Remove duplicate or outdated records
- **Performance Monitoring**: Monitor system metrics and performance
- **Security Updates**: Update dependencies and apply security patches
- **Documentation Updates**: Keep documentation current with changes

### Issue Resolution
- **Problem Classification**: Categorize issues (bug, feature, enhancement)
- **Reproduction**: Create minimal test case to reproduce issues
- **Root Cause Analysis**: Identify underlying cause of issues
- **Solution Design**: Design appropriate fix or workaround
- **Testing**: Thoroughly test fixes before deployment

This workflow ensures consistent, maintainable, and scalable development practices for the CrawlJob system.