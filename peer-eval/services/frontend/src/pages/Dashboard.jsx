import { useState, useEffect } from 'react';
import { projectsAPI, teamsAPI, evaluationsAPI } from '../api';
import { FolderKanban, Users, ClipboardCheck, TrendingUp, ArrowRight, Calendar } from 'lucide-react';

function Dashboard({ user }) {
  const [stats, setStats] = useState({
    projects: 0,
    teams: 0,
    evaluations: 0,
    pending: 0
  });
  const [recentProjects, setRecentProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [projectsRes, teamsRes, evalsRes] = await Promise.all([
        projectsAPI.list(),
        teamsAPI.list(),
        evaluationsAPI.list()
      ]);

      setStats({
        projects: projectsRes.data.count || 0,
        teams: teamsRes.data.count || 0,
        evaluations: evalsRes.data.count || 0,
        pending: 0 // Calculate based on your logic
      });

      setRecentProjects((projectsRes.data.projects || []).slice(0, 5));
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">
          <div className="animate-pulse">Loading dashboard...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div style={{ marginBottom: '36px' }}>
        <h1 style={{ 
          fontSize: '36px', 
          fontWeight: '800', 
          marginBottom: '8px',
          background: 'linear-gradient(135deg, #e4e4e7 0%, #a1a1aa 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          letterSpacing: '-0.02em'
        }}>
          Welcome back, {user.name}! 👋
        </h1>
        <p style={{ fontSize: '16px', color: '#a1a1aa', fontWeight: '500' }}>
          Here's what's happening with your projects today.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-3" style={{ marginBottom: '40px' }}>
        <div className="card" style={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
          color: 'white',
          border: 'none',
          position: 'relative',
          overflow: 'hidden'
        }}>
          <div style={{ position: 'absolute', top: '-20px', right: '-20px', opacity: 0.2 }}>
            <FolderKanban size={120} />
          </div>
          <div style={{ position: 'relative', zIndex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <div style={{ 
                width: '48px', 
                height: '48px', 
                background: 'rgba(255, 255, 255, 0.2)',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backdropFilter: 'blur(10px)'
              }}>
                <FolderKanban size={24} />
              </div>
              <div>
                <p style={{ fontSize: '14px', opacity: 0.9, fontWeight: '600' }}>Total Projects</p>
                <p style={{ fontSize: '36px', fontWeight: '800', lineHeight: '1' }}>{stats.projects}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card" style={{ 
          background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', 
          color: 'white',
          border: 'none',
          position: 'relative',
          overflow: 'hidden'
        }}>
          <div style={{ position: 'absolute', top: '-20px', right: '-20px', opacity: 0.2 }}>
            <Users size={120} />
          </div>
          <div style={{ position: 'relative', zIndex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <div style={{ 
                width: '48px', 
                height: '48px', 
                background: 'rgba(255, 255, 255, 0.2)',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backdropFilter: 'blur(10px)'
              }}>
                <Users size={24} />
              </div>
              <div>
                <p style={{ fontSize: '14px', opacity: 0.9, fontWeight: '600' }}>Active Teams</p>
                <p style={{ fontSize: '36px', fontWeight: '800', lineHeight: '1' }}>{stats.teams}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card" style={{ 
          background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', 
          color: 'white',
          border: 'none',
          position: 'relative',
          overflow: 'hidden'
        }}>
          <div style={{ position: 'absolute', top: '-20px', right: '-20px', opacity: 0.2 }}>
            <ClipboardCheck size={120} />
          </div>
          <div style={{ position: 'relative', zIndex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <div style={{ 
                width: '48px', 
                height: '48px', 
                background: 'rgba(255, 255, 255, 0.2)',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backdropFilter: 'blur(10px)'
              }}>
                <ClipboardCheck size={24} />
              </div>
              <div>
                <p style={{ fontSize: '14px', opacity: 0.9, fontWeight: '600' }}>Evaluations</p>
                <p style={{ fontSize: '36px', fontWeight: '800', lineHeight: '1' }}>{stats.evaluations}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Projects */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <h2 style={{ fontSize: '22px', fontWeight: '700', color: '#e4e4e7' }}>
            Recent Projects
          </h2>
          <a href="/projects" style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '6px', 
            color: '#a78bfa', 
            fontWeight: '600', 
            fontSize: '14px',
            textDecoration: 'none',
            transition: 'gap 0.2s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.gap = '10px'}
          onMouseLeave={(e) => e.currentTarget.style.gap = '6px'}>
            View all <ArrowRight size={16} />
          </a>
        </div>
        {recentProjects.length === 0 ? (
          <div className="empty-state">
            <p style={{ fontSize: '16px', marginBottom: '8px' }}>No projects yet.</p>
            <p style={{ fontSize: '14px' }}>Create your first project to get started!</p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Project</th>
                  <th>Instructor</th>
                  <th>Status</th>
                  <th>Teams</th>
                </tr>
              </thead>
              <tbody>
                {recentProjects.map((project) => (
                  <tr key={project.id}>
                    <td>
                      <div>
                        <div style={{ fontWeight: '600', color: '#e4e4e7', marginBottom: '4px' }}>
                          {project.title}
                        </div>
                        <div style={{ fontSize: '13px', color: '#a1a1aa' }}>
                          {project.description}
                        </div>
                      </div>
                    </td>
                    <td style={{ fontWeight: '500', color: '#d4d4d8' }}>
                      {project.instructor?.name || 'N/A'}
                    </td>
                    <td>
                      <span className={`badge ${
                        project.status === 'active' ? 'badge-success' : 
                        project.status === 'completed' ? 'badge-info' : 'badge-warning'
                      }`}>
                        {project.status}
                      </span>
                    </td>
                    <td style={{ fontWeight: '600', color: '#a78bfa' }}>
                      {project.teams?.length || 0}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 style={{ fontSize: '22px', fontWeight: '700', marginBottom: '20px', color: '#e4e4e7' }}>
          Quick Actions
        </h2>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          {user.role === 'instructor' && (
            <>
              <a href="/projects" className="btn btn-primary">
                <FolderKanban size={16} />
                Create Project
              </a>
              <a href="/teams" className="btn btn-secondary">
                <Users size={16} />
                Manage Teams
              </a>
            </>
          )}
          <a href="/evaluations" className="btn btn-primary">
            <ClipboardCheck size={16} />
            Submit Evaluation
          </a>
          <a href="/reports" className="btn btn-secondary">
            <TrendingUp size={16} />
            View Reports
          </a>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
