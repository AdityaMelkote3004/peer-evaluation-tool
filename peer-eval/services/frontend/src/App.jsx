import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
import Teams from './pages/Teams';
import Forms from './pages/Forms';
import Evaluations from './pages/Evaluations';
import Reports from './pages/Reports';
import Header from './components/Header';

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('token');
  };

  return (
    <Router>
      {user && <Header user={user} onLogout={handleLogout} />}
      <Routes>
        <Route 
          path="/login" 
          element={user ? <Navigate to="/dashboard" /> : <Login onLogin={handleLogin} />} 
        />
        <Route 
          path="/register" 
          element={user ? <Navigate to="/dashboard" /> : <Register />} 
        />
        <Route 
          path="/dashboard" 
          element={user ? <Dashboard user={user} /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/projects" 
          element={user ? <Projects user={user} /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/teams" 
          element={user ? <Teams user={user} /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/forms" 
          element={user ? <Forms user={user} /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/evaluations" 
          element={user ? <Evaluations user={user} /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/reports" 
          element={user ? <Reports user={user} /> : <Navigate to="/login" />} 
        />
        <Route path="/" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
      </Routes>
    </Router>
  );
}

export default App;
