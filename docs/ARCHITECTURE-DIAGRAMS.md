# BizReg Architecture Diagrams

This file contains visual Mermaid diagrams for the BizReg system architecture, data flows, and workflows.

## 1. System Architecture Overview

```mermaid
graph TB
    User["👤 Citizen Browser<br/>(Windows, Mac, iOS, Android)"]
    
    Frontend["🎨 Next.js Frontend<br/>localhost:3000"]
    
    API["⚡ FastAPI API<br/>localhost:8000/api/v1"]
    
    DB["🗄️ PostgreSQL<br/>localhost:5432"]
    
    Cache["💾 Redis Cache<br/>localhost:6379"]
    
    Alembic["📋 Alembic<br/>Migrations"]
    
    User -->|HTTP/JSON<br/>Bearer Token| Frontend
    Frontend -->|REST API<br/>Authorization| API
    API -->|SQL<br/>Parameterized| DB
    API -->|Commands<br/>Queries| Cache
    Alembic -->|Version Control| DB
    
    style User fill:#e1f5ff
    style Frontend fill:#fff3e0
    style API fill:#f3e5f5
    style DB fill:#e8f5e9
    style Cache fill:#fce4ec
    style Alembic fill:#f1f8e9
```

## 2. Frontend Pages & Routing

```mermaid
graph TD
    App["App Router<br/>layout.tsx"]
    
    App -->|/| Landing["🏠 Landing Page<br/>page.tsx"]
    App -->|/login| Login["🔐 Login Page<br/>login/page.tsx"]
    App -->|/register| Register["📝 Register Page<br/>register/page.tsx"]
    App -->|/dashboard| Dashboard["📊 Dashboard<br/>dashboard/page.tsx<br/>(Protected)"]
    App -->|/services| Services["🛍️ Services Catalog<br/>services/page.tsx<br/>(Protected)"]
    Services -->|/business-registration| BizReg["📋 Business Registration<br/>business-registration/page.tsx<br/>(Protected)"]
    
    style Landing fill:#e3f2fd
    style Login fill:#fff3e0
    style Register fill:#fff3e0
    style Dashboard fill:#c8e6c9
    style Services fill:#c8e6c9
    style BizReg fill:#c8e6c9
```

## 3. API Route Structure

```mermaid
graph TD
    Router["API v1 Router<br/>/api/v1"]
    
    Router -->|/auth| AuthRoutes["🔐 Authentication Routes<br/>routes/auth.py"]
    Router -->|/services| ServiceRoutes["🛍️ Service Routes<br/>routes/services.py"]
    Router -->|/applications| AppRoutes["📋 Application Routes<br/>routes/applications.py"]
    Router -->|/health| HealthRoutes["❤️ Health Routes<br/>routes/health.py"]
    
    AuthRoutes -->|POST /register| Register["Register User"]
    AuthRoutes -->|POST /token| Token["OAuth2 Login"]
    AuthRoutes -->|GET /me| Me["Get Current User"]
    
    ServiceRoutes -->|GET| ListServices["List Active Services"]
    
    AppRoutes -->|POST| CreateApp["Create Application"]
    AppRoutes -->|GET /me| MyApps["List User's Applications"]
    AppRoutes -->|GET /:id| GetApp["Get Application Details"]
    
    HealthRoutes -->|GET| Health["Health Check"]
    
    style Router fill:#f3e5f5
    style AuthRoutes fill:#fce4ec
    style ServiceRoutes fill:#fce4ec
    style AppRoutes fill:#fce4ec
    style HealthRoutes fill:#fce4ec
```

## 4. Request Lifecycle: Application Submission

```mermaid
sequenceDiagram
    participant Browser as 🌐 Browser
    participant Frontend as 📄 Next.js
    participant API as ⚡ FastAPI
    participant Schema as ✔️ Validation
    participant Service as 🔧 Business Logic
    participant DB as 🗄️ PostgreSQL
    
    Browser->>Frontend: User clicks "Submit"
    Frontend->>API: POST /api/v1/applications<br/>{business_name, type, address}<br/>Authorization: Bearer token
    
    API->>API: Extract JWT from header
    API->>DB: Verify JWT signature & expiry
    DB-->>API: ✓ Token valid
    
    API->>DB: Query User & Role by token.sub
    DB-->>API: User {id, email, role_id}
    
    API->>Schema: Validate CreateApplicationRequest
    Schema-->>API: ✓ Valid or ✗ Error (422)
    
    API->>Service: create_business_registration(user, form_data)
    
    Service->>DB: BEGIN TRANSACTION
    Service->>DB: Query Service "business-registration"
    DB-->>Service: Service object
    
    Service->>DB: Query Status "submitted"
    DB-->>Service: Status object
    
    Service->>DB: INSERT Application
    DB-->>Service: Application {id, created_at}
    
    Service->>DB: INSERT AuditLog
    DB-->>Service: AuditLog {id, created_at}
    
    Service->>DB: COMMIT TRANSACTION
    DB-->>Service: ✓ Success
    
    Service-->>API: Application object
    API-->>Frontend: HTTP 201 Created<br/>{application_id, status, form_data}
    
    Frontend->>Browser: Show success message
    Browser->>Frontend: Redirect to /dashboard
    Frontend->>API: GET /api/v1/applications/me
    API->>DB: Query User's applications
    DB-->>API: [Application list]
    API-->>Frontend: List of applications
    Frontend->>Browser: Render dashboard with new app
    
    style Browser fill:#e1f5ff
    style Frontend fill:#fff3e0
    style API fill:#f3e5f5
    style Schema fill:#fff9c4
    style Service fill:#f3e5f5
    style DB fill:#e8f5e9
```

## 5. Authentication Flow: Registration & Login

```mermaid
graph TD
    subgraph Registration["📝 Registration Flow"]
        Reg1["User enters email<br/>& password"]
        Reg2["Frontend validates<br/>locally"]
        Reg3["POST /api/v1/auth/register"]
        Reg4["Backend validates<br/>with Pydantic"]
        Reg5["Hash password<br/>with bcrypt"]
        Reg6["INSERT User"]
        Reg7["Return user_id"]
        Reg8["Redirect to login"]
        
        Reg1 --> Reg2
        Reg2 --> Reg3
        Reg3 --> Reg4
        Reg4 --> Reg5
        Reg5 --> Reg6
        Reg6 --> Reg7
        Reg7 --> Reg8
    end
    
    subgraph Login["🔐 Login Flow"]
        Login1["User enters email<br/>& password"]
        Login2["POST /api/v1/auth/token<br/>OAuth2 form"]
        Login3["Query User by email"]
        Login4["Verify bcrypt hash<br/>vs password"]
        Login5["Generate Access JWT<br/>exp: 15min"]
        Login6["Generate Refresh JWT<br/>exp: 7 days"]
        Login7["Return tokens"]
        Login8["Store in localStorage"]
        Login9["Redirect to /dashboard"]
        
        Login1 --> Login2
        Login2 --> Login3
        Login3 --> Login4
        Login4 --> Login5
        Login5 --> Login6
        Login6 --> Login7
        Login7 --> Login8
        Login8 --> Login9
    end
    
    subgraph Token["🎟️ Token Structure"]
        AccessToken["ACCESS TOKEN<br/>sub: user-uuid<br/>role: citizen<br/>type: access<br/>exp: 15min"]
        RefreshToken["REFRESH TOKEN<br/>sub: user-uuid<br/>type: refresh<br/>exp: 7 days"]
    end
    
    Login7 -.->|Contains| AccessToken
    Login7 -.->|Contains| RefreshToken
    
    style Registration fill:#e8f5e9
    style Login fill:#c8e6c9
    style Token fill:#fff9c4
```

## 6. Database Entity Relationship Diagram

```mermaid
erDiagram
    ROLE ||--o{ USER : has
    USER ||--o{ APPLICATION : submits
    USER ||--o{ AUDITLOG : performs
    SERVICE ||--o{ APPLICATION : for
    APPLICATIONSTATUS ||--o{ APPLICATION : has
    APPLICATION ||--o{ DOCUMENT : contains
    APPLICATION ||--o{ PAYMENT : requires
    APPLICATION ||--o{ WORKFLOWTASK : assigned_to
    APPLICATION ||--o{ AUDITLOG : tracked_by
    USER ||--o{ NOTIFICATION : receives
    USER ||--o{ WORKFLOWTASK : assigned_to_officer
    
    ROLE {
        uuid id PK
        string name "citizen, officer, admin"
        timestamp created_at
        timestamp updated_at
    }
    
    USER {
        uuid id PK
        string email UK "unique"
        string password_hash
        string first_name
        string last_name
        string phone
        boolean is_active
        uuid role_id FK
        timestamp created_at
        timestamp updated_at
    }
    
    SERVICE {
        uuid id PK
        string code UK "business-registration"
        string name
        string description
        string category
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    
    APPLICATIONSTATUS {
        uuid id PK
        string code "submitted, under_review, etc"
        string name
        string description
        timestamp created_at
        timestamp updated_at
    }
    
    APPLICATION {
        uuid id PK
        uuid user_id FK
        uuid service_id FK
        uuid status_id FK
        json form_data
        string reference_number
        timestamp created_at
        timestamp updated_at
    }
    
    DOCUMENT {
        uuid id PK
        uuid application_id FK
        string file_name
        string file_path
        string mime_type
        int size_bytes
        boolean is_verified
        string virus_scan_status
        uuid uploaded_by FK
        timestamp created_at
        timestamp updated_at
    }
    
    PAYMENT {
        uuid id PK
        uuid application_id FK
        decimal amount
        string currency
        string status
        string payment_method
        string transaction_id
        timestamp payment_date
        timestamp created_at
        timestamp updated_at
    }
    
    WORKFLOWTASK {
        uuid id PK
        uuid application_id FK
        uuid assigned_to FK
        string task_type
        string status
        string priority
        timestamp due_date
        timestamp created_at
        timestamp updated_at
    }
    
    AUDITLOG {
        uuid id PK
        uuid application_id FK
        uuid actor_id FK
        string action
        string old_state
        string new_state
        json metadata
        timestamp created_at
    }
    
    NOTIFICATION {
        uuid id PK
        uuid user_id FK
        string type "email, sms"
        string subject
        string body
        string status "pending, sent, failed"
        timestamp sent_at
        timestamp created_at
        timestamp updated_at
    }
```

## 7. Application State Machine

```mermaid
stateDiagram-v2
    [*] --> submitted: User submits form
    
    submitted --> under_review: Officer receives application
    
    under_review --> payment_pending: Verification passed
    under_review --> rejected: Issues found
    
    payment_pending --> paid: Payment received
    payment_pending --> rejected: Payment timeout
    
    paid --> officer_review: Admin reviews
    
    officer_review --> approved: Passes final review
    officer_review --> rejected: Fails review
    
    approved --> completed: Certificate issued
    
    rejected --> [*]: Application terminated
    completed --> [*]: Application completed
    
    note right of submitted
        Citizen submits application
        Audit: application_created
    end note
    
    note right of under_review
        Officer reviews documents
        and form data
    end note
    
    note right of payment_pending
        If registration fee applies
        Citizen makes payment
    end note
    
    note right of officer_review
        Final authorization
        by senior officer
    end note
    
    note right of approved
        System generates
        registration certificate
    end note
    
    note right of completed
        Certificate delivered
        Business officially registered
    end note
```

## 8. API Dependency Injection Chain

```mermaid
graph TD
    Route["Route Handler<br/>create_application()"]
    
    Route -->|Depends| JWT["get_current_user()"]
    Route -->|Depends| RBAC["require_role('citizen')"]
    Route -->|Depends| Session["get_db()"]
    
    JWT -->|Extracts| Token["Authorization header"]
    JWT -->|Verifies| Sig["JWT signature"]
    JWT -->|Checks| Exp["Token expiry"]
    JWT -->|Queries| User["PostgreSQL User"]
    JWT -->|Returns| CurrentUser["Current User Object"]
    
    RBAC -->|Checks| Role["User.role == 'citizen'"]
    RBAC -->|Blocks if| Fail["Role mismatch → 403 Forbidden"]
    Role -->|Passes| Allow["✓ Allowed to proceed"]
    
    Session -->|Gets| Pool["Connection pool"]
    Pool -->|Returns| SQLSession["SQLAlchemy Session"]
    
    CurrentUser & Allow & SQLSession -->|All dependencies resolved| Route
    Route -->|Passes to| Handler["Handler function body"]
    
    style Route fill:#f3e5f5
    style JWT fill:#c8e6c9
    style RBAC fill:#fce4ec
    style Session fill:#fff9c4
    style CurrentUser fill:#c8e6c9
    style Allow fill:#c8e6c9
    style SQLSession fill:#c8e6c9
```

## 9. API Response Error Flow

```mermaid
graph TD
    Request["POST /api/v1/applications"]
    
    Request --> Check1{"JWT<br/>Valid?"}
    Check1 -->|No| Err401["HTTP 401<br/>Unauthorized<br/>Invalid/Expired token"]
    
    Check1 -->|Yes| Check2{"User<br/>Enabled?"}
    Check2 -->|No| Err401B["HTTP 401<br/>Unauthorized<br/>User disabled"]
    
    Check2 -->|Yes| Check3{"Role =<br/>citizen?"}
    Check3 -->|No| Err403["HTTP 403<br/>Forbidden<br/>Insufficient permissions"]
    
    Check3 -->|Yes| Check4{"Valid<br/>JSON?"}
    Check4 -->|No| Err400["HTTP 400<br/>Bad Request<br/>Malformed JSON"]
    
    Check4 -->|Yes| Check5{"Pydantic<br/>Validation<br/>Pass?"}
    Check5 -->|No| Err422["HTTP 422<br/>Unprocessable Entity<br/>Invalid fields"]
    
    Check5 -->|Yes| Check6{"Service<br/>Exists?"}
    Check6 -->|No| Err404["HTTP 404<br/>Not Found<br/>Service not found"]
    
    Check6 -->|Yes| Success["HTTP 201<br/>Created<br/>{application}"]
    
    style Request fill:#f3e5f5
    style Err401 fill:#ffcdd2
    style Err401B fill:#ffcdd2
    style Err403 fill:#ffcdd2
    style Err400 fill:#ffcdd2
    style Err422 fill:#ffcdd2
    style Err404 fill:#ffcdd2
    style Success fill:#c8e6c9
```

## 10. Frontend Authentication State Flow

```mermaid
graph TD
    Landing["🏠 Landing<br/>(Public)"]
    
    Landing -->|Not logged in| Guest["Guest State<br/>localStorage.token = null"]
    Landing -->|Logged in| Auth["Authenticated<br/>localStorage.token = JWT"]
    
    Guest -->|Click Register| RegPage["Register Page<br/>/register"]
    Guest -->|Click Login| LoginPage["Login Page<br/>/login"]
    
    RegPage -->|Submit form| RegAPI["POST /auth/register"]
    RegAPI -->|Success| RegSuccess["HTTP 201<br/>Account created<br/>Redirect to login"]
    RegAPI -->|Error| RegError["Validation error<br/>Show message"]
    RegError -->|Retry| RegPage
    
    LoginPage -->|Submit form| LoginAPI["POST /auth/token"]
    LoginAPI -->|Success| StoreTok["Store access_token<br/>& refresh_token<br/>localStorage"]
    StoreTok --> Dashboard["Redirect to<br/>/dashboard"]
    LoginAPI -->|Error| LoginError["Invalid credentials<br/>Show message"]
    LoginError -->|Retry| LoginPage
    
    Auth -->|Fetch user data| GetMe["GET /auth/me<br/>Authorization: Bearer"]
    GetMe -->|Success| Ready["✓ User ready"]
    GetMe -->|Fail 401| Clear["Clear tokens<br/>Redirect login"]
    
    Ready -->|Access /dashboard| Protected["Protected route<br/>ProtectedRoute wrapper"]
    Protected -->|Has token?| TokenCheck{"localStorage<br/>.token<br/>?"}
    TokenCheck -->|Yes| ShowDash["Show dashboard<br/>Fetch applications"]
    TokenCheck -->|No| RedirLogin["Redirect to login"]
    
    Protected -->|Click Logout| Logout["Clear localStorage<br/>Clear auth state"]
    Logout --> Guest
    
    style Landing fill:#e1f5ff
    style Guest fill:#ffebee
    style Auth fill:#e8f5e9
    style RegPage fill:#fff3e0
    style LoginPage fill:#fff3e0
    style Dashboard fill:#c8e6c9
    style Protected fill:#c8e6c9
```

## 11. Deployment Architecture (Future - Phase 11)

```mermaid
graph TB
    Client["👥 Users<br/>Internet"]
    
    subgraph Cloud["☁️ Cloud Provider (AWS/GCP/Azure)"]
        LB["🔄 Load Balancer<br/>HTTPS"]
        
        subgraph Frontend["Frontend Tier"]
            FE1["Next.js Container 1"]
            FE2["Next.js Container 2"]
            FE3["Next.js Container N"]
        end
        
        subgraph Backend["Backend Tier"]
            API1["FastAPI Container 1"]
            API2["FastAPI Container 2"]
            API3["FastAPI Container N"]
        end
        
        subgraph Database["Data Tier"]
            PrimaryDB["PostgreSQL<br/>Primary"]
            StandbyDB["PostgreSQL<br/>Standby"]
            Redis["Redis<br/>Cluster"]
        end
        
        subgraph Storage["Storage"]
            ObjectStore["S3/Cloud Storage<br/>Documents"]
            Backup["Daily Backup<br/>Snapshots"]
        end
    end
    
    Client -->|HTTPS| LB
    LB --> Frontend
    LB --> Backend
    Frontend --> Backend
    Backend --> PrimaryDB
    Backend --> Redis
    Backend --> ObjectStore
    PrimaryDB -.->|Replication| StandbyDB
    PrimaryDB -.->|Snapshot| Backup
    
    style Client fill:#e1f5ff
    style Cloud fill:#f5f5f5
    style Frontend fill:#fff3e0
    style Backend fill:#f3e5f5
    style Database fill:#e8f5e9
    style Storage fill:#fce4ec
```

## 12. Security Layers

```mermaid
graph TD
    User["👤 User"]
    
    Layer1["🌐 HTTPS/TLS<br/>(Production)"]
    Layer2["🔐 CORS<br/>Allowed origins only"]
    Layer3["📝 Input Validation<br/>Pydantic schemas"]
    Layer4["🛡️ SQL Injection<br/>Parameterized queries"]
    Layer5["🔑 JWT Verification<br/>Signature & expiry"]
    Layer6["🚪 RBAC<br/>Role-based access"]
    Layer7["🔒 Bcrypt<br/>Password hashing"]
    Layer8["📋 Audit Logging<br/>All actions tracked"]
    
    User --> Layer1
    Layer1 --> Layer2
    Layer2 --> Layer3
    Layer3 --> Layer4
    Layer4 --> Layer5
    Layer5 --> Layer6
    Layer6 --> Layer7
    Layer7 --> Layer8
    Layer8 -->|Secure data| Database["🗄️ PostgreSQL"]
    
    style User fill:#e1f5ff
    style Layer1 fill:#fff3e0
    style Layer2 fill:#fff3e0
    style Layer3 fill:#fff9c4
    style Layer4 fill:#fff9c4
    style Layer5 fill:#fce4ec
    style Layer6 fill:#fce4ec
    style Layer7 fill:#c8e6c9
    style Layer8 fill:#c8e6c9
    style Database fill:#e8f5e9
```

---

## How to Use These Diagrams

1. **System Architecture (Diagram 1)**: Use for high-level overview with stakeholders
2. **Frontend Routing (Diagram 2)**: Reference for understanding page flow
3. **API Routes (Diagram 3)**: Share with API consumers
4. **Request Lifecycle (Diagram 4)**: Deep-dive for developers understanding the flow
5. **Authentication (Diagram 5)**: Reference for security reviews
6. **Database Schema (Diagram 6)**: Use for database design discussions
7. **State Machine (Diagram 7)**: Reference for workflow discussions
8. **Dependency Injection (Diagram 8)**: Reference for backend developers
9. **Error Handling (Diagram 9)**: API error code reference
10. **Frontend Auth State (Diagram 10)**: Reference for frontend developers
11. **Deployment (Diagram 11)**: Use for Phase 11 planning
12. **Security Layers (Diagram 12)**: Reference for security reviews and compliance

## Editing the Diagrams

To update any diagram:
1. Copy the Mermaid code from above
2. Edit the code as needed
3. Preview in [mermaid.live](https://mermaid.live/)
4. Update this file with corrected code

All Mermaid diagrams are rendered automatically in GitHub Markdown and most markdown viewers.
