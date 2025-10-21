# Copilot Instructions for the Framework Project

## Project Overview
This project is a modular Python framework that uses RabbitMQ and Celery for messaging, integrates with various APIs like Discord and Mastodon, leverages AI for code generation, and includes thorough documentation.

## Context Handling
Always load the project's configuration or context file at the start of a session so you have the necessary background. This will help you understand the existing modules and the overall architecture.

## Module Creation
When creating a new module, follow the existing patterns for integrating with the message broker and ensure each module is well-documented. Modules should be easy to plug into the framework and adhere to the standard interfaces we've defined.

## AI Integration
Use the LLM to assist in generating boilerplate code, writing tests, and providing code suggestions. The AI should maintain the project's style and conventions.

## Testing with pytest
Always generate and run pytest tests for new modules to ensure we don't break the framework when making changes. Make sure each piece of functionality is covered by tests so we can maintain stability.

## Documentation and Wiki
Maintain a GitHub wiki for the project. Ensure that every new feature or module is documented thoroughly in index.md and related wiki pages. Describe the purpose of the feature, the tests involved, and provide clear usage instructions. Each session should include updating the documentation so the wiki stays current and comprehensive.

## Safety and Consistency
Ensure that the AI agent references the project context to avoid going off track. Keep instructions concise and focused, and always clarify if any ambiguity arises in the task.
