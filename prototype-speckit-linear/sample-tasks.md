# Tasks: JWT Authentication

**Input**: Design documents from `/specs/001-jwt-auth/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure with src/, tests/ directories
- [ ] T002 [P] Initialize Node.js project with Express dependencies
- [ ] T003 [P] Configure ESLint and Prettier

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

- [ ] T004 Setup PostgreSQL database connection
- [ ] T005 [P] Create User model with email, password_hash fields
- [ ] T006 [P] Setup Express middleware structure

**Checkpoint**: Foundation ready

---

## Phase 3: User Story 1 - Login Flow (Priority: P1)

**Goal**: Users can log in and receive JWT token

**Acceptance Scenarios**:
1. **Given** valid credentials, **When** POST /auth/login, **Then** receive JWT token
2. **Given** invalid credentials, **When** POST /auth/login, **Then** receive 401 error

### Implementation for User Story 1

- [ ] T007 [US1] Create auth route at src/routes/auth.ts
- [ ] T008 [US1] Implement bcrypt password verification in src/services/auth.ts
- [ ] T009 [US1] Implement JWT token generation in src/utils/jwt.ts
- [ ] T010 [US1] Add login endpoint with validation

**Checkpoint**: User Story 1 complete

---

## Phase 4: User Story 2 - Protected Routes (Priority: P2)

**Goal**: Protected endpoints require valid JWT

**Acceptance Scenarios**:
1. **Given** valid JWT, **When** accessing protected route, **Then** request succeeds
2. **Given** expired JWT, **When** accessing protected route, **Then** receive 401

### Implementation for User Story 2

- [ ] T011 [US2] Create auth middleware in src/middleware/auth.ts
- [ ] T012 [US2] Implement JWT verification in middleware
- [ ] T013 [US2] Add protected route example at /api/profile

**Checkpoint**: User Story 2 complete
