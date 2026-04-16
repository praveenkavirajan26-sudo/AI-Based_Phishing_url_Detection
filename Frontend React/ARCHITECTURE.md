# PhishGuard AI - Frontend Architecture

## 📁 Project Structure

```
frontend-react-app/
├── src/
│   ├── config/              # Configuration files
│   │   └── api.js          # API endpoints & request helpers
│   │
│   ├── services/            # Business logic & API calls
│   │   ├── authService.js  # Authentication service
│   │   └── scanService.js  # URL scanning service
│   │
│   ├── hooks/              # Custom React hooks
│   │   ├── useAuth.js      # Authentication hook
│   │   ├── useScan.js      # URL scanning hook
│   │   └── useScanHistory.js # Scan history hook
│   │
│   ├── components/         # React components
│   │   ├── ui/            # Reusable UI components
│   │   │   └── Common.jsx # Button, Input, Card, Alert, etc.
│   │   ├── Auth.jsx       # Login/Register component
│   │   ├── Scanner.jsx    # URL scanner component
│   │   ├── Output.jsx     # Results display component
│   │   └── Dashboard.jsx  # Scan history component
│   │
│   ├── App.jsx            # Main application component
│   ├── main.jsx           # Application entry point
│   └── index.css          # Global styles
│
├── .env                   # Environment variables
├── package.json           # Dependencies
├── vite.config.js        # Vite configuration
└── tailwind.config.js    # Tailwind CSS configuration
```

## 🏗️ Architecture Principles

### 1. **Separation of Concerns**
- **Config**: API URLs and settings
- **Services**: Business logic and API communication
- **Hooks**: State management and reusable logic
- **Components**: UI and user interaction

### 2. **Service Layer Pattern**
All API calls go through service classes:
```javascript
// ❌ Don't do this in components
const res = await fetch('http://localhost:8000/login', {...});

// ✅ Do this
const data = await AuthService.login(username, password);
```

### 3. **Custom Hooks**
Encapsulate stateful logic:
```javascript
const { isAuthenticated, login, logout } = useAuth();
const { loading, scanResult, analyzeUrl } = useScan();
```

### 4. **Reusable UI Components**
Consistent design system:
```javascript
<Button variant="primary" loading={isLoading}>
  Submit
</Button>

<Input icon={User} placeholder="Username" />

<Alert type="error" message="Invalid credentials" />
```

## 🔧 Usage Examples

### Authentication Flow
```javascript
import { useAuth } from '../hooks/useAuth';

function MyComponent() {
  const { isAuthenticated, login, logout, username } = useAuth();

  const handleLogin = async () => {
    const result = await login('user', 'pass');
    if (result.success) {
      console.log('Logged in as', username);
    }
  };

  return (
    <div>
      {isAuthenticated ? (
        <button onClick={logout}>Logout</button>
      ) : (
        <button onClick={handleLogin}>Login</button>
      )}
    </div>
  );
}
```

### URL Scanning Flow
```javascript
import { useScan } from '../hooks/useScan';

function Scanner() {
  const { loading, error, scanResult, analyzeUrl } = useScan();

  const handleScan = async (url) => {
    const result = await analyzeUrl(url, token);
    if (result.success) {
      console.log('Scan complete:', result.result);
    }
  };

  return (
    <div>
      {loading && <LoadingSpinner />}
      {error && <Alert type="error" message={error} />}
      {scanResult && <Output result={scanResult} />}
    </div>
  );
}
```

## 📦 Environment Variables

Create `.env` file:
```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=PhishGuard AI
VITE_APP_VERSION=2.0.0
```

Access in code:
```javascript
const apiUrl = import.meta.env.VITE_API_URL;
```

## 🎨 UI Components

### Button
```javascript
<Button variant="primary" loading={false} disabled={false}>
  Click Me
</Button>
```
Variants: `primary`, `secondary`, `danger`, `ghost`

### Input
```javascript
<Input 
  type="text"
  icon={User}
  placeholder="Enter username"
  value={username}
  onChange={handleChange}
/>
```

### Alert
```javascript
<Alert 
  type="error" 
  message="Something went wrong"
  onClose={() => setError(null)}
/>
```
Types: `error`, `success`, `warning`, `info`

### Card
```javascript
<Card bordered={true} className="custom-class">
  {children}
</Card>
```

### Badge
```javascript
<Badge variant="success">Active</Badge>
```
Variants: `default`, `success`, `danger`, `warning`, `info`

## 🚀 Best Practices

1. **Always use services for API calls** - Don't use fetch directly in components
2. **Use custom hooks** - Encapsulate stateful logic
3. **Reuse UI components** - Maintain consistency
4. **Handle errors gracefully** - Show user-friendly messages
5. **Loading states** - Always show feedback during async operations
6. **Environment variables** - Don't hardcode URLs or secrets
7. **PropTypes/TypeScript** - Add type checking for larger projects

## 📝 Future Enhancements

- [ ] Add TypeScript for type safety
- [ ] Implement React Context/Redux for global state
- [ ] Add unit tests with Jest/React Testing Library
- [ ] Add E2E tests with Cypress
- [ ] Implement code splitting and lazy loading
- [ ] Add error boundary components
- [ ] Implement analytics tracking
- [ ] Add PWA support for offline functionality
