import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { Briefcase, Target, FileText } from 'lucide-react';
import Applications from './pages/Applications';
import Leads from './pages/Leads';
import Resumes from './pages/Resumes';
import { NotificationProvider } from './components/NotificationProvider';

function App() {
  return (
    <NotificationProvider>
      <Router>
      <div className="min-h-screen bg-dark-bg">
        {/* Header */}
        <header className="bg-dark-card border-b border-dark-border">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-accent-primary">Prospector</h1>
                <span className="ml-3 text-sm text-dark-muted">AI-Powered Job Tracker</span>
              </div>
            </div>
          </div>
        </header>

        {/* Navigation */}
        <nav className="bg-dark-card border-b border-dark-border">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex space-x-8">
              <NavLink
                to="/"
                className={({ isActive }) =>
                  `flex items-center px-3 py-4 text-sm font-medium border-b-2 transition-colors ${
                    isActive
                      ? 'border-accent-primary text-accent-primary'
                      : 'border-transparent text-dark-muted hover:text-dark-text hover:border-dark-border'
                  }`
                }
              >
                <Briefcase className="w-4 h-4 mr-2" />
                Applications
              </NavLink>
              <NavLink
                to="/leads"
                className={({ isActive }) =>
                  `flex items-center px-3 py-4 text-sm font-medium border-b-2 transition-colors ${
                    isActive
                      ? 'border-accent-primary text-accent-primary'
                      : 'border-transparent text-dark-muted hover:text-dark-text hover:border-dark-border'
                  }`
                }
              >
                <Target className="w-4 h-4 mr-2" />
                Job Leads
              </NavLink>
              <NavLink
                to="/resumes"
                className={({ isActive }) =>
                  `flex items-center px-3 py-4 text-sm font-medium border-b-2 transition-colors ${
                    isActive
                      ? 'border-accent-primary text-accent-primary'
                      : 'border-transparent text-dark-muted hover:text-dark-text hover:border-dark-border'
                  }`
                }
              >
                <FileText className="w-4 h-4 mr-2" />
                Resumes
              </NavLink>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Applications />} />
            <Route path="/leads" element={<Leads />} />
            <Route path="/resumes" element={<Resumes />} />
          </Routes>
        </main>
      </div>
    </Router>
    </NotificationProvider>
  );
}

export default App;
