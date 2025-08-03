# React Development Context

## Core Concepts

### Components
React applications are built using components - modular UI pieces with logic and appearance.

```jsx
// Functional component
function ContentCard({ title, content, onEdit }) {
  return (
    <div className="content-card">
      <h3>{title}</h3>
      <p>{content}</p>
      <button onClick={onEdit}>Edit</button>
    </div>
  );
}

// Component with children
function Layout({ children }) {
  return (
    <div className="layout">
      <nav>Navigation</nav>
      <main>{children}</main>
      <footer>Footer</footer>
    </div>
  );
}
```

### JSX
Syntax extension for JavaScript that allows embedding markup in code.

```jsx
function WelcomeMessage({ user, isLoggedIn }) {
  return (
    <div className="welcome">
      {isLoggedIn ? (
        <h1>Welcome back, {user.name}!</h1>
      ) : (
        <h1>Please log in</h1>
      )}
      
      {/* Conditional rendering */}
      {user.notifications.length > 0 && (
        <div className="notifications">
          You have {user.notifications.length} new notifications
        </div>
      )}
      
      {/* List rendering */}
      <ul>
        {user.recentActivities.map((activity, index) => (
          <li key={activity.id}>{activity.description}</li>
        ))}
      </ul>
    </div>
  );
}
```

## Hooks

### State Hooks

#### useState
Declares state variables you can update directly.

```jsx
import { useState } from 'react';

function ContentGenerator() {
  const [topic, setTopic] = useState('');
  const [contentType, setContentType] = useState('study-guide');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState(null);

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, contentType })
      });
      const content = await response.json();
      setGeneratedContent(content);
    } catch (error) {
      console.error('Generation failed:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div>
      <input 
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder="Enter topic"
      />
      <select 
        value={contentType}
        onChange={(e) => setContentType(e.target.value)}
      >
        <option value="study-guide">Study Guide</option>
        <option value="flashcards">Flashcards</option>
        <option value="quiz">Quiz</option>
      </select>
      <button onClick={handleGenerate} disabled={isGenerating}>
        {isGenerating ? 'Generating...' : 'Generate Content'}
      </button>
      
      {generatedContent && (
        <div className="generated-content">
          {generatedContent.content}
        </div>
      )}
    </div>
  );
}
```

#### useReducer
Declares state variables with update logic in a reducer function.

```jsx
import { useReducer } from 'react';

const initialState = {
  content: null,
  loading: false,
  error: null,
  history: []
};

function contentReducer(state, action) {
  switch (action.type) {
    case 'GENERATE_START':
      return { ...state, loading: true, error: null };
    case 'GENERATE_SUCCESS':
      return {
        ...state,
        loading: false,
        content: action.payload,
        history: [...state.history, action.payload]
      };
    case 'GENERATE_ERROR':
      return { ...state, loading: false, error: action.payload };
    case 'CLEAR_CONTENT':
      return { ...state, content: null, error: null };
    case 'CLEAR_HISTORY':
      return { ...state, history: [] };
    default:
      return state;
  }
}

function AdvancedContentGenerator() {
  const [state, dispatch] = useReducer(contentReducer, initialState);

  const generateContent = async (topic, type) => {
    dispatch({ type: 'GENERATE_START' });
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, type })
      });
      const content = await response.json();
      dispatch({ type: 'GENERATE_SUCCESS', payload: content });
    } catch (error) {
      dispatch({ type: 'GENERATE_ERROR', payload: error.message });
    }
  };

  return (
    <div>
      {state.loading && <div>Generating...</div>}
      {state.error && <div className="error">Error: {state.error}</div>}
      {state.content && <div>{state.content.content}</div>}
      
      <div className="history">
        <h3>History ({state.history.length})</h3>
        <button onClick={() => dispatch({ type: 'CLEAR_HISTORY' })}>
          Clear History
        </button>
      </div>
    </div>
  );
}
```

### Effect Hooks

#### useEffect
Connects components to external systems.

```jsx
import { useState, useEffect } from 'react';

function ContentDashboard() {
  const [contents, setContents] = useState([]);
  const [loading, setLoading] = useState(true);

  // Effect for fetching data on mount
  useEffect(() => {
    async function fetchContents() {
      try {
        const response = await fetch('/api/contents');
        const data = await response.json();
        setContents(data);
      } catch (error) {
        console.error('Failed to fetch contents:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchContents();
  }, []); // Empty dependency array - runs once on mount

  // Effect for auto-refresh
  useEffect(() => {
    const interval = setInterval(() => {
      // Refresh data every 30 seconds
      fetchContents();
    }, 30000);

    return () => clearInterval(interval); // Cleanup
  }, []);

  // Effect for document title
  useEffect(() => {
    document.title = `Dashboard (${contents.length} items)`;
  }, [contents.length]);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Content Dashboard</h2>
      {contents.map(content => (
        <div key={content.id}>{content.title}</div>
      ))}
    </div>
  );
}
```

### Context Hooks

#### useContext
Reads and subscribes to context for sharing data across components.

```jsx
import { createContext, useContext, useState, useEffect } from 'react';

// Create contexts
const AuthContext = createContext();
const ThemeContext = createContext();

// Auth Provider
function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('auth_token');
    if (token) {
      validateToken(token).then(userData => {
        setUser(userData);
        setLoading(false);
      });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (credentials) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    });
    const data = await response.json();
    setUser(data.user);
    localStorage.setItem('auth_token', data.token);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('auth_token');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

// Theme Provider
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// Using contexts in components
function Header() {
  const { user, logout } = useContext(AuthContext);
  const { theme, toggleTheme } = useContext(ThemeContext);

  return (
    <header className={`header ${theme}`}>
      <h1>La Factoria</h1>
      <div>
        <button onClick={toggleTheme}>
          Switch to {theme === 'light' ? 'dark' : 'light'} theme
        </button>
        {user ? (
          <div>
            Welcome, {user.name}!
            <button onClick={logout}>Logout</button>
          </div>
        ) : (
          <button>Login</button>
        )}
      </div>
    </header>
  );
}
```

### Performance Hooks

#### useMemo
Caches expensive calculation results.

```jsx
import { useMemo, useState } from 'react';

function ContentAnalytics({ contents }) {
  const [filterType, setFilterType] = useState('all');

  // Expensive calculation cached with useMemo
  const analytics = useMemo(() => {
    console.log('Calculating analytics...'); // This should only run when contents change
    
    const filtered = filterType === 'all' 
      ? contents 
      : contents.filter(content => content.type === filterType);

    return {
      total: filtered.length,
      byType: filtered.reduce((acc, content) => {
        acc[content.type] = (acc[content.type] || 0) + 1;
        return acc;
      }, {}),
      avgLength: filtered.reduce((sum, content) => sum + content.content.length, 0) / filtered.length || 0,
      mostRecent: filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))[0]
    };
  }, [contents, filterType]);

  return (
    <div>
      <select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
        <option value="all">All Types</option>
        <option value="study-guide">Study Guides</option>
        <option value="flashcards">Flashcards</option>
        <option value="quiz">Quizzes</option>
      </select>

      <div className="analytics">
        <div>Total: {analytics.total}</div>
        <div>Average Length: {Math.round(analytics.avgLength)} characters</div>
        <div>
          By Type:
          {Object.entries(analytics.byType).map(([type, count]) => (
            <div key={type}>{type}: {count}</div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

#### useCallback
Caches function definitions.

```jsx
import { useCallback, useState, memo } from 'react';

// Memoized child component
const ContentItem = memo(function ContentItem({ content, onEdit, onDelete }) {
  console.log('ContentItem rendered:', content.id);
  
  return (
    <div className="content-item">
      <h3>{content.title}</h3>
      <p>{content.excerpt}</p>
      <button onClick={() => onEdit(content.id)}>Edit</button>
      <button onClick={() => onDelete(content.id)}>Delete</button>
    </div>
  );
});

function ContentList({ contents }) {
  const [editingId, setEditingId] = useState(null);

  // These callbacks are memoized to prevent unnecessary re-renders
  const handleEdit = useCallback((id) => {
    setEditingId(id);
  }, []);

  const handleDelete = useCallback(async (id) => {
    if (confirm('Are you sure you want to delete this content?')) {
      try {
        await fetch(`/api/contents/${id}`, { method: 'DELETE' });
        // Refresh contents list
      } catch (error) {
        console.error('Delete failed:', error);
      }
    }
  }, []);

  return (
    <div>
      {contents.map(content => (
        <ContentItem
          key={content.id}
          content={content}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      ))}
    </div>
  );
}
```

### Custom Hooks

```jsx
// Custom hook for API calls
function useApi(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const response = await fetch(url);
        if (!response.ok) throw new Error('API call failed');
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [url]);

  return { data, loading, error };
}

// Custom hook for content generation
function useContentGeneration() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [history, setHistory] = useState([]);

  const generateContent = useCallback(async (topic, type) => {
    setIsGenerating(true);
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, type })
      });
      const content = await response.json();
      
      setHistory(prev => [...prev, { ...content, timestamp: Date.now() }]);
      return content;
    } catch (error) {
      throw error;
    } finally {
      setIsGenerating(false);
    }
  }, []);

  const clearHistory = useCallback(() => {
    setHistory([]);
  }, []);

  return {
    generateContent,
    isGenerating,
    history,
    clearHistory
  };
}

// Using custom hooks
function ContentGeneratorPage() {
  const { generateContent, isGenerating, history } = useContentGeneration();
  const { data: templates } = useApi('/api/templates');
  
  const [topic, setTopic] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await generateContent(topic, selectedTemplate);
      setTopic(''); // Clear form
    } catch (error) {
      alert('Generation failed: ' + error.message);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter topic"
          required
        />
        <select
          value={selectedTemplate}
          onChange={(e) => setSelectedTemplate(e.target.value)}
          required
        >
          <option value="">Select template</option>
          {templates?.map(template => (
            <option key={template.id} value={template.id}>
              {template.name}
            </option>
          ))}
        </select>
        <button type="submit" disabled={isGenerating}>
          {isGenerating ? 'Generating...' : 'Generate'}
        </button>
      </form>

      <div className="history">
        <h3>Generated Content ({history.length})</h3>
        {history.map((item, index) => (
          <div key={index} className="history-item">
            <h4>{item.title}</h4>
            <p>{item.excerpt}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Error Boundaries

```jsx
import { Component } from 'react';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error reporting service
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong.</h2>
          <details>
            {this.state.error && this.state.error.toString()}
          </details>
          <button onClick={() => this.setState({ hasError: false, error: null })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Usage
function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <ThemeProvider>
          <Router>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/generate" element={<ContentGeneratorPage />} />
            </Routes>
          </Router>
        </ThemeProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}
```

## Performance Best Practices

### Code Splitting
```jsx
import { lazy, Suspense } from 'react';

// Lazy load components
const ContentGenerator = lazy(() => import('./ContentGenerator'));
const Dashboard = lazy(() => import('./Dashboard'));
const Settings = lazy(() => import('./Settings'));

function App() {
  return (
    <Router>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          <Route path="/generate" element={<ContentGenerator />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Suspense>
    </Router>
  );
}
```

### Virtual Scrolling for Large Lists
```jsx
import { FixedSizeList as List } from 'react-window';

function VirtualizedContentList({ contents }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      <ContentItem content={contents[index]} />
    </div>
  );

  return (
    <List
      height={600}
      itemCount={contents.length}
      itemSize={120}
    >
      {Row}
    </List>
  );
}
```

## Testing Patterns

```jsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import ContentGenerator from './ContentGenerator';

// Mock API calls
vi.mock('../api', () => ({
  generateContent: vi.fn()
}));

describe('ContentGenerator', () => {
  it('generates content when form is submitted', async () => {
    const mockGenerate = vi.fn().mockResolvedValue({
      title: 'Test Content',
      content: 'Generated content here'
    });
    
    require('../api').generateContent = mockGenerate;

    render(<ContentGenerator />);

    fireEvent.change(screen.getByPlaceholderText('Enter topic'), {
      target: { value: 'React Hooks' }
    });

    fireEvent.click(screen.getByText('Generate'));

    await waitFor(() => {
      expect(screen.getByText('Test Content')).toBeInTheDocument();
    });

    expect(mockGenerate).toHaveBeenCalledWith('React Hooks', expect.any(String));
  });
});
```

## Sources
16. React.dev Learn Documentation - Quick Start
17. React.dev Reference Documentation - Core API
18. React.dev Hooks Reference - useState, useEffect, useContext
19. React Performance Optimization Patterns
20. React Testing Library Best Practices