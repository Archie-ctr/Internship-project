# Minimal frontend page layout

Every page uses the root `app/layout.tsx`, which provides the same lightweight shell:

```mermaid
graph TB
    subgraph Layout["app/layout.tsx (Root Shell)"]
        Header["SiteHeader<br/>- Logo: BizReg<br/>- Navigation: Services, Sign in<br/>- Create account link"]
        Content["Page-specific Content<br/>(Route child)"]
        Footer["Footer<br/>- Copyright: BizReg learning platform<br/>- © SecureAI Labs"]
    end
    
    Header --> Content
    Content --> Footer
    
    style Layout fill:#f9f9f9,stroke:#333
    style Header fill:#e3f2fd,stroke:#1976d2
    style Content fill:#f5f5f5,stroke:#666
    style Footer fill:#e3f2fd,stroke:#1976d2
```

## Current page structure

```mermaid
graph TD
    Root["/"]
    Landing["/ (Landing)<br/>Public page<br/>Register/Login"]
    Register["/register<br/>Citizen account creation<br/>Email, Password, Name"]
    Login["/login<br/>OAuth2 password flow<br/>Sign-in form"]
    Dashboard["/dashboard (Protected)<br/>Citizen overview<br/>Application list"]
    Services["/services (Protected)<br/>Service catalogue<br/>Browse services"]
    BizForm["/services/business-registration<br/>(Protected)<br/>4-step form wizard"]
    
    Root --> Landing
    Root --> Register
    Root --> Login
    Root --> Dashboard
    Root --> Services
    Services --> BizForm
    
    style Landing fill:#fff3cd,stroke:#856404
    style Register fill:#d1ecf1,stroke:#0c5460
    style Login fill:#d1ecf1,stroke:#0c5460
    style Dashboard fill:#d4edda,stroke:#155724
    style Services fill:#d4edda,stroke:#155724
    style BizForm fill:#d4edda,stroke:#155724
    style Root fill:#f8f9fa,stroke:#495057
```

**Page Access Control**:
- 🟨 **Public**: Landing, Register, Login (no authentication required)
- 🟩 **Protected**: Dashboard, Services, Business Registration (require valid JWT token)
- 🔐 **Authorization**: `ProtectedRoute` component + FastAPI JWT dependencies enforce access
