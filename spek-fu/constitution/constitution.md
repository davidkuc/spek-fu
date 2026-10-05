# Constitution

This constitution file defines how the artificial intelligence agent must behave in this project.

## Glossary

**AI** - Artifical Intelligence. Most commonly refers to AI agents.

## Project Principles

## AI Principles

Section defining the guidelines and boundaries for artificial intelligence agents.

### **I. Language**

- Use plain, simple and common language.
- Avoid professional, specialistic, scientific or technical language and wording.
- Assume the reader does not have any technical/specialistic background and has beginner language skills.
- The project is Polish languaged-based. Write specs and communicate in Polish. Write code in English.

### **II. Depth and Volume**

- Maximum signal, minimal verbosity.
- Keep language short, simple and concise while maintaining depth and intent.
- Avoid word bloat. 
- Always aim for minimal amount of text. One sentence per point/thought if possible.
- Aim for terse, yet comprehensive output.

### **III. Ambiguity**

- Never fabricate facts, sources, links, file contents, or outcomes.
- Signal uncertainty explicitly; never present speculation as fact.
- Provide a confidence signal when it materially affects how output should be trusted.
- Request clarification from the user when ambiguous; never assume intent, requirements, or constraints.
- Mark critical missing information with `[NEEDS CLARIFICATION]` and halt work until resolved.
- The user is the final decision-maker. Any critical doubts must be escalated to the user.

### **IV. Criticism**

- Avoid default agreement; respectfully push back when logic conflicts, risks, or missing constraints are detected.
- Hold positions unless new evidence is provided; never mirror user bias uncritically.
- Always verify what the user presents.
- Never assume the user knows everything.

### **V. Source of Truth**
- Follow strictly the SSOT rule - **Single Source of Truth**.
- Do not repeat any information or data.
- Always check if such information exists elsewhere.
- Make sure the SSOT is referenced appropriately when needed.
- Rewriting the same information in different words is considered a violation of this rule.

## Software Development Principles

Section specific for technical-oriented skills.

### SD1. Simplicity (KISS)

The system MUST follow KISS.

Code MUST:
- Avoid unnecessary complexity.
- Minimize deep nesting.
- Keep methods and modules small, focused, and readable.
- Prioritize clarity over cleverness.

### SD2. DRY / Single Source of Truth

- Every piece of knowledge MUST have a single, authoritative representation.
- Logic, validation rules, and domain rules MUST NOT be duplicated across layers.
- Repetition across modules MUST be eliminated through abstraction.

### SD3. SOLID Compliance (OO Components)

All object-oriented components MUST adhere to SOLID:
- Single Responsibility Principle (SRP): a module/class MUST have one reason to change.
- Open-Closed Principle (OCP): components MUST be open for extension, closed for modification.
- Liskov Substitution Principle (LSP): derived types MUST be substitutable for base types.
- Interface Segregation Principle (ISP): interfaces MUST be client-specific and minimal.
- Dependency Inversion Principle (DIP): high-level modules MUST depend on abstractions.

### SD4. Core-Centric Architecture

- The system MUST follow a core-centric, decoupled architecture (e.g., Hexagonal, Clean, or Onion-style).
- Core business logic MUST remain isolated from infrastructure concerns.

### SD5. Dependency Direction

- Dependencies MUST point inward toward domain/core logic.
- Infrastructure (databases, APIs, frameworks, UI) MUST depend on abstractions defined by the core.
Business rules MUST NOT depend on external frameworks.

### SD6. Decoupling & Configuration Discipline

- The system MUST separate interface from implementation.
- External integrations MUST be replaceable without modifying core logic.
Environmental configuration (paths, IPs, credentials, secrets) MUST NOT be hard-coded.

### SD7. Modularity & Extensibility

- Each component MUST be modular and independently testable.
- The system MUST support extensibility without modification of stable components.
Changes in one module MUST NOT cascade across unrelated modules.

### SD8. Test-Driven Development (TDD)

- Development MUST follow Red–Green–Refactor cycles.
- Functional code MUST be written only in response to failing tests. Only the minimal code necessary to pass a test MUST be implemented. Refactoring MUST preserve behavior and improve structure.

If needed, `test-design-guide.md` for the full TDD workflow (shell → red → green → refactor) and examples on building high-value tests.

### SD9. Behavior-Driven Testing Focus (BDD)

- Tests MUST specify behavior (what), not implementation (how).
- Tests MUST use Given/When/Then structure in both naming and narrative, and MUST be readable as executable specifications.

If needed, `test-design-guide.md` for naming conventions and helper method patterns and examples on building high-value tests.

### SD10. Parameterized & Narrative Test Design

- Tests MUST be parameterized; hardcoding test values is forbidden. Test names MUST describe behavior, not specific values.
- Tests MUST read as narratives of intention-revealing helper methods — one method per Given/When/Then step.

If needed, `test-design-guide.md` for parameterization patterns and narrative design conventions and examples on building high-value tests.

### SD11. Testing Pyramid Enforcement

The project MUST follow the Testing Pyramid:
- Many fast, isolated unit tests.
- A moderate layer of integration/service tests.
- A minimal layer of end-to-end tests.

The "Ice-Cream Cone" anti-pattern MUST be avoided.

### SD12. Test Isolation & Doubles

- Core business logic MUST be testable without external integrations.
- Test doubles MUST be used for external dependencies only.
- Internal business logic MUST NOT be excessively mocked.
- Tests MUST be deterministic and fast.

### SD13. Coverage & Meaningfulness

- Test coverage SHOULD focus on critical paths and business logic.
- Coverage metrics MUST NOT be gamed to reach arbitrary 100% targets.
- Trivial code SHOULD NOT be tested purely for coverage inflation.

### SD14. Maintainability & Continuous Refactoring

- Code MUST prioritize long-term maintainability over short-term speed.
- Clear naming conventions MUST be enforced consistently.
- Related logic MUST be grouped logically and formatted clearly.
- Refactoring MUST be continuous.

### SD15. Technical Debt Management

- Technical debt MUST be actively identified and managed.
- Sub-optimal shortcuts MUST NOT be normalized.
- Code introducing structural degradation MUST be refactored.

### SD16. Complexity Control

- Cyclomatic complexity SHOULD be minimized.
- Large methods MUST be decomposed.
- Code MUST "tell its story" through composition of well-named methods.

### SD17. Boy Scout Rule

Every modification MUST leave the codebase in a better state than before.

### SD18. Testability & Local Manual Validation

- Core logic MUST run and be testable without external systems.
- Manual testability MUST be possible locally, with and without integrations.
- Concurrency logic MUST separate functional logic from synchronization concerns.

### SD19. Forbidden Practices

The following are forbidden at the constitutional level:
- Hard-coded environmental configuration.
- Business logic inside infrastructure layers.
- Deep coupling between modules.
- Excessive end-to-end test reliance.
- Mocking internal business logic.
- Testing implementation instead of behavior.
- Allowing architecture to degrade into tightly coupled "spaghetti" structure.
- Letting technical debt accumulate unmanaged.

### SD20. Quality Attributes Prioritized

The system MUST prioritize:
1. Maintainability
2. Reliability
3. Testability
4. Modularity
5. Scalability
6. Portability
7. Reusability

Architecture MUST serve as a tool to manage complexity and technical debt, not merely as documentation.

### SD21. Human-Verifiable Design

- Always design systems that are locally testable by the human
- Design systems from a user-perspective - how will the user consume the system?
- Design systems from a developers-perspective - how will the developer test the various components of the system in isolation and the whole system in end-to-end?
