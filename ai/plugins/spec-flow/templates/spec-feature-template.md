# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`  
**Created**: [DATE]  
**Status**: Draft  
**Input**: User description: "$ARGUMENTS"

---

## Feature Overview

### Intent
<!--
WHAT THIS IS and WHY IT EXISTS — two sentences max.
What is in scope and what is out of scope.
This lets every reader immediately know what NOT to look for in this document.

Example:
  "Building a user authentication system with email and SSO support.
   Priority: core login/logout flows and RBAC. Out of scope: audit logging, 2FA, rate limiting."
-->

[Feature goal and business value — what problem it solves, priorities]

Out of scope: [what is deliberately excluded]

---

### Glossary
<!--
DEFINITIONS — capitalized, used consistently throughout the entire document.
Goal: eliminate ambiguity before anything is described.
Every term that appears multiple times and could be interpreted differently — define it here.

Example:
  **User** (Actor) - an authenticated system participant performing actions
  **Session** - a bounded context spanning login through logout
  **Permission** - a quality rating for resource access, expressed as scopes [read, write, admin]
-->

**[Term A]** ([alias if applicable]) - [definition in one sentence]

**[Term B]** - [definition in one sentence]

**[Term C]** - [definition in one sentence]

---

### Description
<!--
ONE–TWO SENTENCES describing the feature from the user's perspective.
Answers: "what does the user do and why?"
No implementation details, no systems — just the essence of the experience.

Example:
  "Users can authenticate with email/password or SSO, establishing a session that grants access to protected resources.
   The system enforces role-based authorization."
-->

[Description of the feature from the user's perspective — what they do and why]

---

### Core Flows
<!--
MAJOR WORKFLOWS and the breakdown of the feature at concept level.
Describes the primary paths users take through the feature.
No logic here — just flow names and their general purpose.

Example:
  The feature consists of three core flows:
  - Authentication Flow — user provides credentials and receives a session token
  - Authorization Flow — system validates user permissions for each resource
  - Session Management Flow — system maintains and invalidates sessions
-->

The feature consists of [N] core flow(s):
- **[Flow A]** — [one-sentence description]
- **[Flow B]** — [one-sentence description]

---

### Components & Modules
<!--
THE HEART OF THE DOCUMENT — describes each major component separately, always following this schema:
  1. Configuration/Parameters — numbers and settings in brackets [n], tunable (e.g. via config files or environment)
  2. Behavior — logic and rules, written as declarative sentences

Each component = a separate ### section with the same subsections.
Values always in [square brackets] — signals that it is a parameter, not a constant.

When a behavior has edge cases — write them immediately after the main rule.
When a rule is complex — add an inline example.

Components to include (example list — adjust to the project):
  Authentication, Authorization, User Service, [Domain Entity], [Integration Point], Validation, Error Handling
-->

#### [Component A — e.g. Authentication Service]

##### Behavior
<!--
Component behavior and logic.
Main rule → edge case → error handling if relevant.

Example:
  - Authentication accepts email and password credentials.
  - Credentials validated against database hash. No plain-text storage.
  - On success: generate JWT token with [3600]s expiration.
  - On failure: increment failed attempt counter; lock account after [5] attempts for [15] minutes.
-->

- [Rule 1]
- [Rule 2]
- [Rule 3 — edge case: ...]

---

#### [Component B — e.g. User Service]

##### Behavior

- [Rule 1]
- [Rule 2]

---

#### [Component C — e.g. Authorization Service]

##### Behavior

- [Rule 1]
- [Rule 2 — if complex, add an example:]
  - Example: given [user role] is [admin], permission check for [resource] returns [allowed]
  - Example: given [user role] is [viewer], write operation on [resource] returns [denied]

---

#### [Component D — e.g. Validation Module]

##### Behavior
<!--
Some components have no configurable parameters — omit that subsection.
-->

- [Rule 1]
- [Rule 2]

---

#### Performance & Limits
<!--
Defines thresholds, timeouts, rate limits, and scaling parameters.
Always defines: limits, thresholds, timeout values, retry behavior.
-->

##### Configuration & Behavior

- [Component name] request timeout: [[n]] milliseconds
- [Component name] rate limit: [[n]] requests per [[unit]] per [user/IP]
- [Component name] max payload size: [[n]] bytes
- On timeout: [retry [[n]] times / return error / fallback behavior]
- On rate limit exceeded: [return 429 / queue request / reject]

---

#### Data & State Management
<!--
Defines data models, state persistence, consistency requirements.
Always include: entities, state transitions, persistence rules, constraints.
-->

##### Behavior

- [Entity] data persisted in [storage] with [consistency model]
- [State transitions]: [from state] → [to state] requires [condition]
- [Special condition — e.g. cascading deletes, soft deletes]
- [Uniqueness / constraint] — [description]

---

#### Integrations & External Dependencies
<!--
External systems, APIs, webhooks, event flows.
Structure: integration type → specific integration → behavior and error handling.

Standard types (adjust to the project):
  HTTP APIs, Event Streams, Messaging, Webhooks

Each integration described as:
  **NAME** (INT-ID)
  - endpoint/protocol: [description]
  - request/event schema: [structure]
  - retry/error handling: [behavior]
-->

The system integrates with [N] external service(s). Integration failure modes:

Integration types:
- **[Type A]** — [general description]
- **[Type B]** — [general description]
- **[Type C]** — [general description]

##### Integration List

###### [Type A]

**[NAME]** (INT-ID)
[One-sentence description]
- Endpoint: [URL/protocol]
- Retry behavior: [retry [[n]] times on failure / exponential backoff]
- Fallback: [behavior if service unavailable]

###### [Type B]

**[NAME]** (INT-ID)
[One-sentence description]
- Event type: [name]
- Delivery: [at-least-once / exactly-once / at-most-once]
- Error handling: [behavior on delivery failure]

---

### Implementation Requirements
<!--
WHAT MUST BE BUILT for the feature to work.
Split into categories: General, System States, API Endpoints, User Flows.
Tables for endpoints/UI — because they have multiple attributes.
Prose/list for everything else.

Do not describe how to build it — only what must exist and how it should behave.
-->

#### General
<!--
Cross-cutting requirements: constraints, dependencies, restrictions.

Example:
  - No authentication required for public endpoints
  - All responses use JSON format
  - Error responses use standard HTTP status codes
  - Database migrations required before deployment
-->

- [Requirement 1]
- [Requirement 2]

---

#### System States
<!--
State table: state name + description of when it is active.
Example:
  Idle, Processing, Completed, Failed
-->

| State | Description |
|-------|-------------|
| **[State A]** | [when it is active] |
| **[State B]** | [when it is active] |

---

#### API Endpoints / Interfaces
<!--
Endpoint table: method + path + description + availability/auth.
Group by entity or feature if there are many.
-->

| Method | Path | Description | Authentication |
|--------|------|-------------|----------------|
| **[GET/POST]** | [/path] | [what it does] | [required/optional/none] |
| **[GET/POST]** | [/path] | [what it does] | [required/optional/none] |
| **[GET/POST]** | [/path] | [what it does] | Always required |

---

#### User Flow / Feature Checklist
<!--
Numbered list — the shortest possible description of the flow from start to finish.
This is the "quick overview" perspective for developers and QA.
-->

1. User [action] → system state **[State A]**
2. [What the system shows/returns]
3. User [action] → system state **[State B]**, [what happens]
4. [Flow continues through feature]
5. [Feature end] → [result / message] → state **[Final State]**
6. [Optional follow-up action]

---

### User Experience
<!--
USER INTERFACE AND INTERACTION — what users see, how they interact, and how the system responds.
Describes UI states, error messaging, feedback mechanisms.
Keep it short — only what differentiates this feature from standard components.

Subsections: Form Fields, Buttons/Actions, Messages/Feedback, Error States

Example:
  ### Input Validation
  - Email field shows real-time validation feedback
  - Submit button disabled until form is valid
  - Error messages displayed inline with field focus
-->

#### Input Fields & Forms

- [Validation behavior]
- [Help text / placeholder behavior]
- [Focus and error states]

#### Buttons & Actions

- [Behavior on different states]
- [Loading indicators if applicable]
- [Disabled state conditions]

#### Messages & Feedback

- [Success message format and duration]
- [Error message format and presentation]
- [Confirmation dialogs for destructive actions if applicable]

---

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - [Brief Title] (Priority: P1)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently - e.g., "Can be fully tested by [specific action] and delivers [specific value]"]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 2 - [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 3 - [Brief Title] (Priority: P3)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- What happens when [boundary condition]?
- How does system handle [error scenario]?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST [specific capability, e.g., "allow users to create accounts"]
- **FR-002**: System MUST [specific capability, e.g., "validate email addresses"]  
- **FR-003**: Users MUST be able to [key interaction, e.g., "reset their password"]
- **FR-004**: System MUST [data requirement, e.g., "persist user preferences"]
- **FR-005**: System MUST [behavior, e.g., "log all security events"]

*Example of marking unclear requirements:*

- **FR-006**: System MUST authenticate users via [NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]
- **FR-007**: System MUST retain user data for [NEEDS CLARIFICATION: retention period not specified]

### Key Entities *(include if feature involves data)*

- **[Entity 1]**: [What it represents, key attributes without implementation]
- **[Entity 2]**: [What it represents, relationships to other entities]

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: [Measurable metric, e.g., "Users can complete account creation in under 2 minutes"]
- **SC-002**: [Measurable metric, e.g., "System handles 1000 concurrent users without degradation"]
- **SC-003**: [User satisfaction metric, e.g., "90% of users successfully complete primary task on first attempt"]
- **SC-004**: [Business metric, e.g., "Reduce support tickets related to [X] by 50%"]