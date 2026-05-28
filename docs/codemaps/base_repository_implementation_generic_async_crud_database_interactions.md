# Base Repository Implementation: Generic Async CRUD & Database Interactions

Maps the async repository pattern from database engine initialization through generic BaseRepository CRUD operations to concrete domain repositories and FastAPI integration. Key entry points: database engine setup [1b], generic CRUD methods [2b-2e], session lifecycle [4b-4e], and API usage [5a-5e].

## Trace ID: 1
**Title:** Database Engine & Session Factory Initialization

**Description:** Core database infrastructure setup - shows how SQLAlchemy async engine connects to PostgreSQL and creates session factories

**Motivation:**
EduBoost V2 uses SQLAlchemy 2.0 with async support for database operations, enabling non-blocking database queries in an async FastAPI application. The async engine uses the asyncpg driver for PostgreSQL, providing high-performance async database access. Connection pooling is configured to manage database connections efficiently, reducing connection overhead. The async session factory creates session instances with expire_on_commit=False, allowing ORM objects to remain accessible after transaction commit (important for async operations). The declarative base class provides shared metadata for all ORM models, enabling automatic table mapping and relationship management. The FastAPI dependency function get_db() provides request-scoped sessions with automatic commit/rollback, ensuring transaction boundaries are properly managed at the HTTP request level.

**Details:**
- **Execution Flow:** Application Startup → Load settings from environment → create_async_engine() creates engine → Configure async session factory → async_sessionmaker() with config → Define ORM base class → Base(DeclarativeBase) → FastAPI Request Lifecycle → Route dependency injection → get_db() async generator → Session context manager → AsyncSessionLocal() creates session → yield session to route handler → commit() on success → rollback() on exception
- **Concurrency Safety:** Engine uses connection pooling for concurrent access. Session factory creates independent sessions per request. Async operations use cooperative multitasking. No distributed locks needed as connection pool handles concurrency. Multiple concurrent requests handled independently
- **Covered Objects:** SQLAlchemy async engine, asyncpg driver, connection pool, async session factory, declarative base, FastAPI dependency injection, session lifecycle, transaction management
- **Timeouts:** Engine creation: ~100-500ms. Session factory creation: ~10-50ms. Session creation per request: ~10-50ms. Query execution: ~10-500ms depending on query. Total request overhead: ~50-1000ms
- **Migration Path:** From synchronous to asynchronous SQLAlchemy. Migration requires: 1) Install asyncpg driver, 2) Create async engine, 3) Configure async session factory, 4) Update ORM models for async, 5) Implement async dependency injection
- **Error Handling:** Connection failures logged and raised. Session creation failures logged. Transaction failures trigger rollback. All errors propagated to FastAPI exception handlers. Connection pool errors handled automatically
- **Security Considerations:** Database credentials from environment variables. Connection pool limits prevent connection exhaustion. SSL/TLS for database connections. Session isolation prevents data leaks. Transaction rollback on error prevents partial updates

**Trace text diagram:**
```
Database Infrastructure Initialization
├── Application Startup
│   ├── Load settings from environment <-- 1a
│   │   └── create_async_engine() creates engine <-- database.py:39
│   ├── Configure async session factory <-- 1b
│   │   └── async_sessionmaker() with config <-- database.py:42
│   └── Define ORM base class <-- 1c
│       └── Base(DeclarativeBase) <-- database.py:57
└── FastAPI Request Lifecycle
    ├── Route dependency injection <-- 1d
    │   └── get_db() async generator <-- database.py:61
    └── Session context manager <-- 1e
        ├── AsyncSessionLocal() creates session <-- database.py:63
        ├── yield session to route handler <-- database.py:65
        ├── commit() on success <-- database.py:66
        └── rollback() on exception <-- database.py:68
```

**Location ID: 1a**
- **Title:** Async Engine Creation
- **Description:** Creates SQLAlchemy async engine with asyncpg driver and connection pooling
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:39

**Location ID: 1b**
- **Title:** Session Factory Creation
- **Description:** Configures async session maker with expire_on_commit=False for async operations
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:41

**Location ID: 1c**
- **Title:** Declarative Base Definition
- **Description:** Shared ORM base class that all models inherit from
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:57

**Location ID: 1d**
- **Title:** FastAPI Dependency Function
- **Description:** Async generator that provides database sessions to API routes via dependency injection
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:61

**Location ID: 1e**
- **Title:** Session Context Manager
- **Description:** Creates new async session for each request with automatic cleanup
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:63

### AI Guide: Database Engine & Session Factory Initialization

**Overview:** The database infrastructure setup initializes SQLAlchemy async engine, session factory, and declarative base for async database operations. This trace shows how the database layer is configured for use with FastAPI.

**Key Components:**

1. **Async Engine Creation (1a):** Creates SQLAlchemy async engine with asyncpg driver. Configures connection pooling. Loads settings from environment.

2. **Session Factory Creation (1b):** Configures async session maker with expire_on_commit=False. Enables async operations. Binds to engine.

3. **Declarative Base Definition (1c):** Shared ORM base class for all models. Provides metadata tracking. Enables automatic table mapping.

4. **FastAPI Dependency Function (1d):** Async generator for dependency injection. Provides sessions to routes. Manages session lifecycle.

5. **Session Context Manager (1e):** Creates new async session per request. Yields session to route handler. Handles commit/rollback automatically.

**Best Practices:**
- Use asyncpg driver for PostgreSQL
- Configure connection pooling appropriately
- Set expire_on_commit=False for async
- Use dependency injection for sessions
- Handle commit/rollback automatically
- Use environment variables for credentials
- Enable SSL/TLS for production

**Common Issues:**
- Connection pool exhaustion: Increase pool size
- Session not committed: Check exception handling
- Expired objects: Ensure expire_on_commit=False
- Connection timeout: Check database connectivity
- Memory leaks: Ensure sessions are closed

## Trace ID: 2
**Title:** Generic BaseRepository CRUD Operations

**Description:** Foundation layer providing type-safe async CRUD methods for any ORM model - used by all concrete repositories

**Motivation:**
EduBoost V2 implements a generic BaseRepository class that provides standard async CRUD operations for any ORM model, reducing code duplication and ensuring consistent data access patterns. The class uses Python's Generic type system with a TypeVar bound to Base, providing type safety for all operations. The get() method performs async select queries using SQLAlchemy 2.0 syntax, returning a single instance or None. The get_or_404() method wraps get() with domain exception raising, providing 404 responses for missing entities. The create() method instantiates models from kwargs, adds to session, flushes to get ID without committing, and refreshes to load database-generated defaults. The update() method dynamically updates model attributes from kwargs, enabling partial updates. The list() method provides filtered, paginated queries with optional filter dictionaries. This generic foundation is extended by all concrete repositories, ensuring consistent patterns across the codebase.

**Details:**
- **Execution Flow:** BaseRepository[ModelT] class → async get(id, db) → select(self.model).where(...) → result.scalar_one_or_none() → async get_or_404(id, db) → await self.get(id, db) → raise NotFoundError(...) → async create(db, **kwargs) → instance = self.model(**kwargs) → db.add(instance) → await db.flush() → await db.refresh(instance) → async update(instance, db, **kwargs) → setattr(instance, field, value) → db.add(instance) → await db.flush() → Type Parameter: ModelT bound to Base → Provides type safety for all operations
- **Concurrency Safety:** Repository operations are stateless and thread-safe. Session operations are independent per request. No shared state between operations. No distributed locks needed as session handles concurrency. Multiple concurrent operations handled independently
- **Covered Objects:** BaseRepository, TypeVar ModelT, async CRUD methods, SQLAlchemy 2.0 select queries, domain exceptions, model instantiation, session operations, attribute updates
- **Timeouts:** get() operation: ~10-100ms. create() operation: ~10-100ms. update() operation: ~10-100ms. list() operation: ~10-500ms depending on filters. Total CRUD operation: ~10-500ms
- **Migration Path:** From ad-hoc queries to generic repository. Migration requires: 1) Define BaseRepository class, 2) Implement generic CRUD methods, 3) Add type parameters, 4) Migrate existing repositories, 5) Update API routes
- **Error Handling:** Query failures logged and raised. Entity not found raises NotFoundError. Validation errors raised. Session errors propagated. All errors handled by FastAPI exception handlers
- **Security Considerations:** Type safety prevents injection attacks. Parameterized queries prevent SQL injection. Domain exceptions hide implementation details. Session isolation prevents data leaks. Authorization handled at service layer

**Trace text diagram:**
```
BaseRepository Generic CRUD Layer
├── BaseRepository[ModelT] class <-- 2a
│   ├── async get(id, db) <-- base.py:23
│   │   ├── select(self.model).where(...) <-- 2b
│   │   └── result.scalar_one_or_none() <-- base.py:25
│   ├── async get_or_404(id, db) <-- base.py:27
│   │   ├── await self.get(id, db) <-- base.py:29
│   │   └── raise NotFoundError(...) <-- 2f
│   ├── async create(db, **kwargs) <-- base.py:50
│   │   ├── instance = self.model(**kwargs) <-- 2c
│   │   ├── db.add(instance) <-- base.py:52
│   │   ├── await db.flush() <-- base.py:53
│   │   └── await db.refresh(instance) <-- base.py:54
│   └── async update(instance, db, **kwargs) <-- base.py:57
│       ├── setattr(instance, field, value) <-- 2e
│       ├── db.add(instance) <-- base.py:60
│       └── await db.flush() <-- base.py:61
└── Type Parameter: ModelT bound to Base <-- base.py:15
    └── Provides type safety for all operations
```

**Location ID: 2a**
- **Title:** Generic Repository Class
- **Description:** Type-parameterized base repository providing standard async operations
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/base.py:18

**Location ID: 2b**
- **Title:** Generic Get Operation
- **Description:** Async select query using SQLAlchemy 2.0 syntax with type safety
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/base.py:24

**Location ID: 2c**
- **Title:** Model Instantiation
- **Description:** Creates new model instance from keyword arguments
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/base.py:51

**Location ID: 2d**
- **Title:** Flush Without Commit
- **Description:** Persists to database and gets ID without committing transaction
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/base.py:53

**Location ID: 2e**
- **Title:** Dynamic Attribute Update
- **Description:** Updates model attributes dynamically from kwargs dictionary
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/base.py:59

**Location ID: 2f**
- **Title:** 404 Error Handling
- **Description:** Raises domain exception when entity not found, caught by FastAPI handlers
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/base.py:29

### AI Guide: Generic BaseRepository CRUD Operations

**Overview:** The BaseRepository class provides generic async CRUD operations for any ORM model, ensuring consistent data access patterns across the codebase. This trace shows how the generic foundation is implemented.

**Key Components:**

1. **Generic Repository Class (2a):** Type-parameterized base repository with ModelT bound to Base. Provides standard async operations. Extended by concrete repositories.

2. **Generic Get Operation (2b):** Async select query using SQLAlchemy 2.0 syntax. Filters by ID. Returns single instance or None.

3. **Model Instantiation (2c):** Creates new model instance from kwargs. Uses model constructor. Validates types automatically.

4. **Flush Without Commit (2d):** Persists to database without committing. Gets database-generated ID. Enables subsequent operations.

5. **Dynamic Attribute Update (2e):** Updates model attributes from kwargs. Enables partial updates. Uses setattr for flexibility.

6. **404 Error Handling (2f):** Raises domain exception when not found. Caught by FastAPI handlers. Returns 404 response.

**Best Practices:**
- Use generic repository for common operations
- Implement type parameters for type safety
- Use flush before commit for ID generation
- Refresh after flush for database defaults
- Use get_or_404 for required entities
- Implement custom queries in concrete repositories
- Keep generic methods simple and focused

**Common Issues:**
- Type errors: Check TypeVar binding
- Entity not found: Use get_or_404
- Missing defaults: Refresh after flush
- Partial updates: Use update method
- Query performance: Add indexes

## Trace ID: 3
**Title:** Concrete Repository Implementation Pattern

**Description:** Domain-specific repositories extending base patterns with custom queries - shows LearnerRepository and GuardianRepository examples

**Motivation:**
EduBoost V2 implements concrete repositories that extend the generic BaseRepository with domain-specific queries and business logic. The LearnerRepository provides learner-specific operations like create() with guardian association and get_by_guardian() for filtering learners by parent. The GuardianRepository extends BaseRepository[Guardian] to inherit generic CRUD operations while adding custom queries like get_by_email_hash() for authentication. This pattern allows code reuse through inheritance while enabling domain-specific customization. Concrete repositories accept AsyncSession in their constructor, enabling dependency injection from FastAPI. Domain-specific queries use SQLAlchemy 2.0 select syntax with type-safe ORM models. This separation of concerns keeps data access logic organized and testable, with generic operations in the base and domain-specific operations in concrete repositories.

**Details:**
- **Execution Flow:** Repository Pattern Architecture → Domain Repository Classes → LearnerRepository class → __init__(db: AsyncSession) → create() method → LearnerProfile(**kwargs) → self.db.add(learner) → GuardianRepository class → extends BaseRepository[Guardian] → get_by_email_hash() method → select(Guardian).where(...) → Base Infrastructure → BaseRepository[ModelT] (generic CRUD) → AsyncSession (from get_db dependency)
- **Concurrency Safety:** Repository instances are request-scoped and thread-safe. Session operations are independent per request. No shared state between instances. No distributed locks needed as session handles concurrency. Multiple concurrent requests handled independently
- **Covered Objects:** LearnerRepository, GuardianRepository, BaseRepository, AsyncSession, domain models, custom queries, dependency injection, inheritance pattern
- **Timeouts:** Repository initialization: ~1-5ms. Custom query execution: ~10-100ms. Generic CRUD operations: ~10-100ms. Total repository operation: ~10-200ms
- **Migration Path:** From ad-hoc queries to repository pattern. Migration requires: 1) Define concrete repository classes, 2) Extend BaseRepository, 3) Implement custom queries, 4) Update service layer, 5. Refactor API routes
- **Error Handling:** Query failures logged and raised. Entity not found returns None. Validation errors raised. Session errors propagated. All errors handled by FastAPI exception handlers
- **Security Considerations:** Type-safe queries prevent injection. Authorization handled at service layer. Session isolation prevents data leaks. Domain-specific queries enforce business rules. Dependency injection enables testing

**Trace text diagram:**
```
Repository Pattern Architecture
├── Domain Repository Classes
│   ├── LearnerRepository class <-- 3a
│   │   ├── __init__(db: AsyncSession) <-- repositories.py:59
│   │   └── create() method <-- repositories.py:62
│   │       ├── LearnerProfile(**kwargs) <-- 3b
│   │       └── self.db.add(learner) <-- 3c
│   └── GuardianRepository class <-- 3d
│       ├── extends BaseRepository[Guardian] <-- auth_repository.py:16
│       └── get_by_email_hash() method <-- auth_repository.py:21
│           └── select(Guardian).where(...) <-- 3e
└── Base Infrastructure
    ├── BaseRepository[ModelT] (generic CRUD) <-- base.py:18
    └── AsyncSession (from get_db dependency) <-- database.py:61
```

**Location ID: 3a**
- **Title:** Concrete Repository Class
- **Description:** Domain repository for learner persistence operations
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/repositories.py:58

**Location ID: 3b**
- **Title:** Domain Model Creation
- **Description:** Instantiates LearnerProfile ORM model with provided data
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/repositories.py:63

**Location ID: 3c**
- **Title:** Add to Session
- **Description:** Stages new entity in session for persistence
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/repositories.py:64

**Location ID: 3d**
- **Title:** Repository Extending Base
- **Description:** Guardian repository inherits generic CRUD from BaseRepository[Guardian]
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/auth_repository.py:16

**Location ID: 3e**
- **Title:** Custom Domain Query
- **Description:** Domain-specific query method for authentication by email hash
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/auth_repository.py:22

### AI Guide: Concrete Repository Implementation Pattern

**Overview:** Concrete repositories extend the generic BaseRepository with domain-specific queries and business logic. This trace shows how the repository pattern is implemented for domain-specific data access.

**Key Components:**

1. **Concrete Repository Class (3a):** Domain repository for learner operations. Accepts AsyncSession in constructor. Provides domain-specific methods.

2. **Domain Model Creation (3b):** Instantiates ORM model with provided data. Uses model constructor. Validates types automatically.

3. **Add to Session (3c):** Stages entity in session for persistence. Uses session.add(). Enables transaction management.

4. **Repository Extending Base (3d):** Guardian repository inherits generic CRUD. Extends BaseRepository[Guardian]. Adds custom queries.

5. **Custom Domain Query (3e):** Domain-specific query for authentication. Uses SQLAlchemy 2.0 select syntax. Returns single instance or None.

**Best Practices:**
- Extend BaseRepository for code reuse
- Implement domain-specific queries
- Use dependency injection for sessions
- Keep repositories focused on data access
- Move business logic to service layer
- Use type-safe ORM models
- Test repositories with test sessions

**Common Issues:**
- Code duplication: Extend BaseRepository
- Business logic in repositories: Move to services
- Missing dependencies: Inject via constructor
- Query performance: Add indexes
- Type errors: Check ORM model types

## Trace ID: 4
**Title:** FastAPI Session Lifecycle & Transaction Management

**Description:** Request-scoped database session lifecycle with automatic commit/rollback - core of transaction boundary management

**Motivation:**
EduBoost V2 uses FastAPI's dependency injection system to manage database session lifecycle per HTTP request, ensuring proper transaction boundaries. The get_db() async generator creates a new async session for each request using the session factory. The session is yielded to the route handler, pausing execution during request processing. After the route handler completes, the generator resumes and commits the transaction if no exception occurred. If any exception occurs during request processing, the transaction is rolled back automatically. This pattern ensures that each HTTP request has its own isolated transaction, preventing data corruption from concurrent modifications. The finally block ensures the session is always closed, preventing connection leaks. This automatic transaction management simplifies route handler code by removing manual commit/rollback logic while ensuring data consistency.

**Details:**
- **Execution Flow:** FastAPI Request Lifecycle → Route Handler Entry → @router.post("/") endpoint → db: AsyncSession = Depends(get_db) → Dependency Injection System → get_db() async generator → Session Creation Phase → async with AsyncSessionLocal() → yield session → Request Processing Phase → [route handler executes here] → Cleanup & Transaction Phase → Success Path → await session.commit() → Exception Path → await session.rollback()
- **Concurrency Safety:** Each request gets isolated session. Transactions are independent per request. Connection pool manages concurrent access. No distributed locks needed as database handles isolation. Multiple concurrent requests handled independently
- **Covered Objects:** FastAPI dependency injection, async generator, session lifecycle, transaction management, commit/rollback, session context manager, connection pool
- **Timeouts:** Session creation: ~10-50ms. Request processing: variable. Commit: ~10-100ms. Rollback: ~10-100ms. Session cleanup: ~1-5ms. Total request overhead: ~50-500ms
- **Migration Path:** From manual session management to dependency injection. Migration requires: 1) Implement get_db() generator, 2) Add Depends(get_db) to routes, 3) Remove manual session management, 4) Test transaction boundaries, 5) Update error handling
- **Error Handling:** Session creation failures logged. Request exceptions trigger rollback. Commit failures logged. Session cleanup always executed. All errors propagated to FastAPI exception handlers
- **Security Considerations:** Session isolation prevents data leaks. Transaction rollback prevents partial updates. Connection pool limits prevent exhaustion. Session cleanup prevents leaks. Authorization handled at route level

**Trace text diagram:**
```
FastAPI Request Lifecycle
├── Route Handler Entry
│   └── @router.post("/") endpoint <-- learners.py:24
│       └── db: AsyncSession = Depends(get_db) <-- 4a
│
└── Dependency Injection System
    └── get_db() async generator <-- 4b
        ├── Session Creation Phase
        │   └── async with AsyncSessionLocal() <-- 4b
        │       └── yield session <-- 4c
        │
        ├── Request Processing Phase
        │   └── [route handler executes here]
        │
        └── Cleanup & Transaction Phase <-- database.py:64
            ├── Success Path
            │   └── await session.commit() <-- 4d
            │
            └── Exception Path <-- database.py:67
                └── await session.rollback() <-- 4e
```

**Location ID: 4a**
- **Title:** Dependency Injection
- **Description:** FastAPI injects database session into route handler
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/learners.py:27

**Location ID: 4b**
- **Title:** Session Creation
- **Description:** Opens new async session for the request
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:63

**Location ID: 4c**
- **Title:** Session Yield to Route
- **Description:** Provides session to route handler, pauses here during request processing
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:65

**Location ID: 4d**
- **Title:** Auto-Commit on Success
- **Description:** Commits transaction if route handler completes without exception
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:66

**Location ID: 4e**
- **Title:** Auto-Rollback on Error
- **Description:** Rolls back transaction if any exception occurs during request
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:68

### AI Guide: FastAPI Session Lifecycle & Transaction Management

**Overview:** FastAPI's dependency injection system manages database session lifecycle per HTTP request with automatic commit/rollback. This trace shows how transaction boundaries are managed at the HTTP request level.

**Key Components:**

1. **Dependency Injection (4a):** FastAPI injects database session into route handler. Uses Depends(get_db). Provides session to route.

2. **Session Creation (4b):** Opens new async session for request. Uses session factory. Creates isolated transaction.

3. **Session Yield to Route (4c):** Yields session to route handler. Pauses generator during processing. Resumes after handler completes.

4. **Auto-Commit on Success (4d):** Commits transaction if no exception. Persists changes to database. Closes session.

5. **Auto-Rollback on Error (4e):** Rolls back transaction on exception. Reverts changes. Re-raises exception.

**Best Practices:**
- Use dependency injection for sessions
- Let FastAPI manage commit/rollback
- Keep transactions request-scoped
- Avoid manual session management
- Test transaction boundaries
- Handle exceptions appropriately
- Ensure session cleanup

**Common Issues:**
- Transaction not committed: Check for exceptions
- Partial updates: Ensure rollback on error
- Connection leaks: Ensure session cleanup
- Concurrent modifications: Use proper isolation
- Long transactions: Keep transactions short

## Trace ID: 5
**Title:** Repository Usage in API Endpoint

**Description:** Complete flow from API route through repository to database - demonstrates learner creation with transaction management

**Motivation:**
EduBoost V2 demonstrates the complete flow from API endpoint through repository to database, showing how the repository pattern integrates with FastAPI. The POST /learners endpoint uses dependency injection to get a database session. The route handler instantiates a LearnerRepository with the injected session. The repository's create() method is called with request data, creating a LearnerProfile ORM instance and adding it to the session. The flush() operation persists the entity to the database and gets the database-generated ID without committing the transaction. The response is serialized using Pydantic's model_validate() to convert the ORM model to the response schema. After the route handler completes successfully, FastAPI's dependency system automatically commits the transaction. This pattern shows how the repository pattern provides clean separation between API logic and data access, with automatic transaction management handled by the framework.

**Details:**
- **Execution Flow:** FastAPI Learner Creation Flow → POST /learners endpoint → Dependency Injection → get_db() yields AsyncSession → Route Handler → repo = LearnerRepository(db) → await repo.create(...) → LearnerRepository.create() → learner = LearnerProfile(**kwargs) → self.db.add(learner) → await self.db.flush() → LearnerResponse.model_validate() → Return JSON response
- **Concurrency Safety:** Each request gets isolated session. Repository operations are stateless. Transaction management per request. No distributed locks needed as database handles isolation. Multiple concurrent requests handled independently
- **Covered Objects:** FastAPI endpoint, dependency injection, repository instantiation, repository create method, ORM model, session operations, response serialization
- **Timeouts:** Dependency injection: ~1-5ms. Repository instantiation: ~1-5ms. Repository create: ~10-100ms. Response serialization: ~1-5ms. Total endpoint: ~50-200ms
- **Migration Path:** From direct database access to repository pattern. Migration requires: 1) Create repository classes, 2) Update endpoints to use repositories, 3. Remove direct database access, 4) Add response serialization, 5) Test integration
- **Error Handling:** Validation errors raised before repository. Repository failures trigger rollback. Serialization errors logged. All errors handled by FastAPI exception handlers. Transaction rollback on error
- **Security Considerations:** Authorization checked before repository. Input validation before repository. Repository enforces business rules. Transaction isolation prevents data leaks. Response serialization hides internal state

**Trace text diagram:**
```
FastAPI Learner Creation Flow
└── POST /learners endpoint <-- 5a
    ├── Dependency Injection
    │   └── get_db() yields AsyncSession <-- database.py:61
    └── Route Handler
        ├── repo = LearnerRepository(db) <-- 5b
        ├── await repo.create(...) <-- 5c
        │   └── LearnerRepository.create() <-- repositories.py:62
        │       ├── learner = LearnerProfile(**kwargs) <-- repositories.py:63
        │       ├── self.db.add(learner) <-- 5d
        │       └── await self.db.flush() <-- 5e
        └── LearnerResponse.model_validate() <-- 5f
            └── Return JSON response
```

**Location ID: 5a**
- **Title:** API Endpoint Definition
- **Description:** FastAPI route for creating new learner with response model validation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/learners.py:24

**Location ID: 5b**
- **Title:** Repository Instantiation
- **Description:** Creates repository instance with injected database session
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/learners.py:30

**Location ID: 5c**
- **Title:** Async Repository Call
- **Description:** Invokes repository create method with request data
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/learners.py:31

**Location ID: 5d**
- **Title:** Entity Persistence
- **Description:** Adds learner to session within repository method
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/repositories.py:64

**Location ID: 5e**
- **Title:** Flush for ID Generation
- **Description:** Flushes to get database-generated ID before transaction commits
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/repositories.py:65

**Location ID: 5f**
- **Title:** Response Serialization
- **Description:** Validates and serializes ORM model to Pydantic response schema
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/learners.py:37

### AI Guide: Repository Usage in API Endpoint

**Overview:** The complete flow from API endpoint through repository to database demonstrates how the repository pattern integrates with FastAPI. This trace shows the learner creation flow with transaction management.

**Key Components:**

1. **API Endpoint Definition (5a):** FastAPI route for creating learner. Uses POST method. Defines response model. Requires authentication.

2. **Repository Instantiation (5b):** Creates repository instance with injected session. Passes session to constructor. Enables repository operations.

3. **Async Repository Call (5c):** Invokes repository create method. Passes request data. Returns ORM instance.

4. **Entity Persistence (5d):** Adds entity to session. Stages for persistence. Enables transaction management.

5. **Flush for ID Generation (5e):** Flushes to get database-generated ID. Persists without commit. Enables subsequent operations.

6. **Response Serialization (5f):** Validates ORM model to response schema. Converts to JSON. Returns to client.

**Best Practices:**
- Use dependency injection for sessions
- Instantiate repositories in route handlers
- Call repository methods with await
- Use flush for ID generation
- Serialize responses with Pydantic
- Let FastAPI manage transactions
- Handle errors appropriately

**Common Issues:**
- Repository not instantiated: Check constructor
- Entity not persisted: Check session operations
- ID not generated: Use flush before commit
- Serialization errors: Check response model
- Transaction not committed: Check for exceptions

## Trace ID: 6
**Title:** ORM Model to Repository Connection

**Description:** How SQLAlchemy ORM models integrate with repositories - shows model definition and query execution

**Motivation:**
EduBoost V2 uses SQLAlchemy 2.0 ORM models that integrate with repositories through the declarative base class. ORM models are defined in the domain layer with typed column mappings using Mapped[] annotations, providing type safety and IDE support. Models inherit from the shared DeclarativeBase, enabling automatic table mapping and relationship management. The repository layer constructs select queries using the ORM model class, executing them via the AsyncSession. Queries use SQLAlchemy 2.0 select syntax with type-safe filtering. Results are extracted using scalar_one_or_none() for single instances or scalars() for multiple instances. The asyncpg driver executes the actual SQL against PostgreSQL, returning ORM instances that are automatically mapped from database rows. This integration provides a clean separation between domain models (ORM) and data access (repositories) while maintaining type safety and eliminating raw SQL.

**Details:**
- **Execution Flow:** ORM Model → Repository Query Flow → Domain Model Layer (app/models) → LearnerProfile class definition → id: Mapped[str] column → Inherits from Base → Base(DeclarativeBase) → Repository Layer (app/repositories) → LearnerRepository.get_by_id() → Constructs select(LearnerProfile) → await db.execute(query) → result.scalar_one_or_none() → Uses AsyncSession from get_db() → Database Engine (app/core/database) → AsyncSession executes via asyncpg → Returns ORM instance or None
- **Concurrency Safety:** ORM models are stateless and thread-safe. Query execution is independent per request. Session operations are isolated. No distributed locks needed as database handles isolation. Multiple concurrent queries handled independently
- **Covered Objects:** ORM models, declarative base, typed column mappings, repository queries, SQLAlchemy 2.0 select, AsyncSession, asyncpg driver, result extraction
- **Timeouts:** Model definition: compile-time. Query construction: ~1-5ms. Query execution: ~10-500ms. Result extraction: ~1-5ms. Total query: ~10-500ms
- **Migration Path:** From raw SQL to ORM models. Migration requires: 1) Define ORM models, 2) Create declarative base, 3) Update repositories to use ORM, 4) Remove raw SQL, 5) Test query execution
- **Error Handling:** Model definition errors at compile-time. Query execution failures logged. Result extraction failures logged. All errors propagated to FastAPI exception handlers
- **Security Considerations:** Type-safe queries prevent injection. ORM models hide database schema. Session isolation prevents data leaks. Typed mappings ensure data integrity. Authorization handled at service layer

**Trace text diagram:**
```
ORM Model → Repository Query Flow
├── Domain Model Layer (app/models)
│   ├── LearnerProfile class definition <-- 6a
│   │   └── id: Mapped[str] column <-- 6b
│   └── Inherits from Base
│       └── Base(DeclarativeBase) <-- 6c
│
├── Repository Layer (app/repositories)
│   ├── LearnerRepository.get_by_id() <-- repositories.py:68
│   │   ├── Constructs select(LearnerProfile) <-- repositories.py:69
│   │   ├── await db.execute(query) <-- 6d
│   │   └── result.scalar_one_or_none() <-- 6e
│   │
│   └── Uses AsyncSession from get_db() <-- database.py:61
│
└── Database Engine (app/core/database)
    └── AsyncSession executes via asyncpg <-- database.py:39
        └── Returns ORM instance or None
```

**Location ID: 6a**
- **Title:** ORM Model Definition
- **Description:** Domain model extending declarative Base with table mapping
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:142

**Location ID: 6b**
- **Title:** Typed Column Mapping
- **Description:** SQLAlchemy 2.0 typed mappings with Mapped[] annotations
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:145

**Location ID: 6c**
- **Title:** Shared Declarative Base
- **Description:** All ORM models inherit from this base for metadata tracking
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:57

**Location ID: 6d**
- **Title:** Query Execution
- **Description:** Executes async select query against ORM model
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/repositories.py:69

**Location ID: 6e**
- **Title:** Result Extraction
- **Description:** Extracts single ORM instance or None from query result
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/repositories.py:72

### AI Guide: ORM Model to Repository Connection

**Overview:** SQLAlchemy ORM models integrate with repositories through the declarative base class. This trace shows how ORM models are defined and used in repository queries.

**Key Components:**

1. **ORM Model Definition (6a):** Domain model extending declarative Base. Defines table mapping. Inherits metadata tracking.

2. **Typed Column Mapping (6b):** SQLAlchemy 2.0 typed mappings. Uses Mapped[] annotations. Provides type safety.

3. **Shared Declarative Base (6c):** All models inherit from this base. Provides metadata tracking. Enables automatic table mapping.

4. **Query Execution (6d):** Executes async select query. Uses ORM model class. Returns result object.

5. **Result Extraction (6e):** Extracts single instance or None. Uses scalar_one_or_none(). Returns ORM instance.

**Best Practices:**
- Use typed column mappings
- Inherit from declarative base
- Define relationships explicitly
- Use SQLAlchemy 2.0 select syntax
- Extract results appropriately
- Keep models in domain layer
- Use type-safe queries

**Common Issues:**
- Type errors: Check Mapped[] annotations
- Mapping errors: Check table name
- Query errors: Check select syntax
- Result errors: Check extraction method
- Relationship errors: Check foreign keys

## Trace ID: 7
**Title:** Advanced Repository Pattern - ItemBankRepository

**Description:** Complex repository with subqueries, exposure tracking, and atomic operations - demonstrates advanced SQLAlchemy patterns

**Motivation:**
EduBoost V2 implements advanced repository patterns in ItemBankRepository to handle complex data access requirements. The repository uses subqueries to filter items a learner has already seen, preventing item reuse in diagnostic assessments. Exposure tracking records each item served to a learner, enabling adaptive testing algorithms. Atomic counter increments using UPDATE statements ensure thread-safe exposure count tracking without race conditions. The upsert pattern checks for existing items before deciding between insert and update operations, handling data idempotently. These advanced patterns demonstrate SQLAlchemy's capabilities for complex queries, atomic operations, and conditional logic at the database level. The repository shows how to balance performance (subqueries, atomic updates) with correctness (exposure tracking, upsert logic) in a real-world application.

**Details:**
- **Execution Flow:** ItemBankRepository Advanced Operations → Repository initialization → Query unexposed items flow → Build exposure subquery → SELECT item_id WHERE learner_id → Main query construction → Filter by caps_ref & status → Apply NOT IN subquery → Filter by difficulty bounds → Execute & return items → Record exposure & increment counter → Create ItemExposure record → Atomic UPDATE statement → SET exposure_count = count + 1 → Flush to database → Upsert pattern → Check existing item → If exists: update attributes → If new: create & add to session
- **Concurrency Safety:** Subqueries are deterministic per request. Atomic updates use database locks. Upsert logic checks existence first. No distributed locks needed as database handles isolation. Multiple concurrent operations handled by database
- **Covered Objects:** ItemBankRepository, subqueries, exposure tracking, atomic updates, upsert pattern, ItemExposure model, DiagnosticItem model, complex filters
- **Timeouts:** Subquery construction: ~1-5ms. Main query execution: ~10-200ms. Exposure record creation: ~10-50ms. Atomic update: ~10-50ms. Upsert operation: ~10-100ms. Total operation: ~50-400ms
- **Migration Path:** From simple queries to advanced patterns. Migration requires: 1) Implement subqueries, 2) Add exposure tracking, 3) Implement atomic updates, 4) Add upsert logic, 5) Test concurrency
- **Error Handling:** Query failures logged. Subquery failures logged. Atomic update failures logged. Upsert failures logged. All errors propagated to FastAPI exception handlers
- **Security Considerations:** Subqueries prevent data leaks. Exposure tracking ensures fairness. Atomic updates prevent race conditions. Upsert logic ensures idempotency. Authorization handled at service layer

**Trace text diagram:**
```
ItemBankRepository Advanced Operations
├── Repository initialization <-- 7a
├── Query unexposed items flow <-- item_bank_repository.py:64
│   ├── Build exposure subquery <-- 7b
│   │   └── SELECT item_id WHERE learner_id <-- item_bank_repository.py:79
│   ├── Main query construction <-- item_bank_repository.py:87
│   │   ├── Filter by caps_ref & status <-- item_bank_repository.py:90
│   │   ├── Apply NOT IN subquery <-- 7c
│   │   └── Filter by difficulty bounds <-- item_bank_repository.py:100
│   └── Execute & return items <-- item_bank_repository.py:105
├── Record exposure & increment counter <-- item_bank_repository.py:206
│   ├── Create ItemExposure record <-- 7d
│   ├── Atomic UPDATE statement <-- 7e
│   │   └── SET exposure_count = count + 1 <-- item_bank_repository.py:225
│   └── Flush to database <-- item_bank_repository.py:228
└── Upsert pattern <-- item_bank_repository.py:360
    ├── Check existing item <-- 7f
    ├── If exists: update attributes <-- item_bank_repository.py:367
    └── If new: create & add to session <-- item_bank_repository.py:381
```

**Location ID: 7a**
- **Title:** Repository Initialization
- **Description:** Stores async session for all repository operations
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/item_bank_repository.py:28

**Location ID: 7b**
- **Title:** Subquery Construction
- **Description:** Builds subquery to filter items learner has already seen
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/item_bank_repository.py:78

**Location ID: 7c**
- **Title:** Subquery Filter Application
- **Description:** Uses subquery in WHERE clause to exclude exposed items
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/item_bank_repository.py:94

**Location ID: 7d**
- **Title:** Exposure Record Creation
- **Description:** Adds exposure tracking record to session
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/item_bank_repository.py:220

**Location ID: 7e**
- **Title:** Atomic Counter Increment
- **Description:** Atomically increments exposure count using UPDATE statement
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/item_bank_repository.py:222

**Location ID: 7f**
- **Title:** Upsert Logic
- **Description:** Checks for existing item before deciding insert vs update
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/item_bank_repository.py:366

### AI Guide: Advanced Repository Pattern - ItemBankRepository

**Overview:** ItemBankRepository demonstrates advanced SQLAlchemy patterns including subqueries, exposure tracking, atomic operations, and upsert logic. This trace shows how to handle complex data access requirements.

**Key Components:**

1. **Repository Initialization (7a):** Stores async session for operations. Accepts session in constructor. Enables all repository methods.

2. **Subquery Construction (7b):** Builds subquery to filter seen items. Uses select() with where clause. Returns item_id list.

3. **Subquery Filter Application (7c):** Uses subquery in WHERE clause. Exposes NOT IN operator. Filters main query.

4. **Exposure Record Creation (7d):** Adds exposure tracking record. Creates ItemExposure instance. Stages in session.

5. **Atomic Counter Increment (7e):** Atomically increments exposure count. Uses UPDATE statement. Prevents race conditions.

6. **Upsert Logic (7f):** Checks for existing item. Updates if exists. Creates if new. Ensures idempotency.

**Best Practices:**
- Use subqueries for complex filters
- Track exposure for adaptive testing
- Use atomic updates for counters
- Implement upsert for idempotency
- Test concurrency scenarios
- Use database-level operations
- Keep logic in repository layer

**Common Issues:**
- Subquery performance: Add indexes
- Race conditions: Use atomic updates
- Duplicate inserts: Use upsert logic
- Exposure tracking: Check learner_id
- Query complexity: Simplify when possible

## Trace ID: 8
**Title:** Exception Handling & Error Responses

**Description:** How repository errors propagate to FastAPI exception handlers - shows 404 handling and integrity error management

**Motivation:**
EduBoost V2 implements a comprehensive exception handling system that converts repository errors into appropriate HTTP responses. The BaseRepository.get_or_404() method raises a domain NotFoundError when an entity is not found, providing clear error semantics. Domain exceptions inherit from a base EduBoostError class, enabling centralized exception handling. FastAPI exception handlers catch domain exceptions and convert them to JSON responses with appropriate status codes. The NotFoundError handler returns 404 Not Found with error details. SQLAlchemy IntegrityError is caught separately and converted to 409 Conflict for constraint violations. This separation of concerns keeps repository logic focused on data access while exception handlers handle HTTP response formatting. The system provides clear error messages to clients while hiding implementation details, improving security and user experience.

**Details:**
- **Execution Flow:** Exception Handling Flow → BaseRepository.get_or_404() → await self.get(id, db) → if instance is None → raise NotFoundError(...) → Domain Exception Hierarchy → EduBoostError (base) → NotFoundError (404) → SQLAlchemy IntegrityError → FastAPI Exception Handlers → @app.exception_handler(EduBoostError) → handle_eduboost_error() → return JSONResponse(404, {...}) → @app.exception_handler(IntegrityError) → handle_integrity_error() → return JSONResponse(409, {...})
- **Concurrency Safety:** Exception handling is stateless. Domain exceptions are immutable. Handler registration is thread-safe. No distributed locks needed. Multiple concurrent errors handled independently
- **Covered Objects:** BaseRepository, domain exceptions, NotFoundError, EduBoostError, IntegrityError, FastAPI exception handlers, JSON responses, error codes
- **Timeouts:** Exception raising: ~1-5ms. Exception handler execution: ~1-10ms. Response serialization: ~1-5ms. Total error handling: ~5-20ms
- **Migration Path:** From ad-hoc error handling to domain exceptions. Migration requires: 1) Define domain exception hierarchy, 2) Update repositories to raise domain exceptions, 3) Register FastAPI handlers, 4) Update error responses, 5) Test error scenarios
- **Error Handling:** Entity not found raises NotFoundError. Constraint violations raise IntegrityError. Handlers convert to HTTP responses. All errors logged appropriately. Error messages are user-friendly
- **Security Considerations:** Domain exceptions hide implementation details. Error messages don't expose sensitive data. Status codes follow HTTP semantics. Error codes enable client handling. Authorization checked before repository

**Trace text diagram:**
```
Exception Handling Flow
├── BaseRepository.get_or_404() <-- base.py:27
│   ├── await self.get(id, db) <-- 8a
│   └── if instance is None <-- base.py:30
│       └── raise NotFoundError(...) <-- 8b
│
├── Domain Exception Hierarchy
│   ├── EduBoostError (base) <-- exceptions.py:23
│   │   └── NotFoundError (404) <-- 8c
│   └── SQLAlchemy IntegrityError <-- exceptions.py:15
│
└── FastAPI Exception Handlers <-- exceptions.py:150
    ├── @app.exception_handler(EduBoostError) <-- exceptions.py:153
    │   └── handle_eduboost_error() <-- 8d
    │       └── return JSONResponse(404, {...}) <-- exceptions.py:155
    │
    └── @app.exception_handler(IntegrityError) <-- exceptions.py:195
        └── handle_integrity_error() <-- 8e
            └── return JSONResponse(409, {...}) <-- exceptions.py:198
```

**Location ID: 8a**
- **Title:** Entity Lookup
- **Description:** Attempts to fetch entity by ID in get_or_404 method
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/base.py:29

**Location ID: 8b**
- **Title:** Domain Exception Raised
- **Description:** Raises typed domain exception when entity not found
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/base.py:31

**Location ID: 8c**
- **Title:** Exception Class Definition
- **Description:** Domain exception with 404 status code and error code
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/exceptions.py:35

**Location ID: 8d**
- **Title:** Exception Handler Registration
- **Description:** FastAPI handler converts domain exceptions to JSON responses
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/exceptions.py:154

**Location ID: 8e**
- **Title:** Database Constraint Handler
- **Description:** Catches SQLAlchemy integrity errors and returns 409 Conflict
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/exceptions.py:196

### AI Guide: Exception Handling & Error Responses

**Overview:** Repository errors propagate to FastAPI exception handlers which convert them to appropriate HTTP responses. This trace shows how the exception handling system works.

**Key Components:**

1. **Entity Lookup (8a):** Attempts to fetch entity by ID. Calls get() method. Returns instance or None.

2. **Domain Exception Raised (8b):** Raises typed domain exception when not found. Uses NotFoundError class. Includes error message.

3. **Exception Class Definition (8c):** Domain exception with status code. Inherits from EduBoostError. Defines error code.

4. **Exception Handler Registration (8d):** FastAPI handler for domain exceptions. Catches EduBoostError. Converts to JSON response.

5. **Database Constraint Handler (8e):** Catches SQLAlchemy integrity errors. Returns 409 Conflict. Handles constraint violations.

**Best Practices:**
- Use domain exceptions for business errors
- Define exception hierarchy
- Register FastAPI handlers
- Return appropriate status codes
- Provide clear error messages
- Hide implementation details
- Log errors appropriately

**Common Issues:**
- Exceptions not caught: Check handler registration
- Wrong status code: Check exception definition
- Missing error details: Check response serialization
- Integrity errors not handled: Add IntegrityError handler
- Generic exceptions: Use specific exception types
