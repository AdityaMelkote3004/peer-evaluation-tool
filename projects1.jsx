import { useState, useEffect } from 'react';
import { projectsAPI } from '../api';
import { Plus, Edit, Trash2, Calendar } from 'lucide-react';

function Projects({ user }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    instructor_id: user.id,
    start_date: '',
    end_date: '',
    status: 'active'
  });

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const response = await projectsAPI.list();
      setProjects(response.data.projects || []);
    } catch (error) {
      console.error('Failed to load projects:', error);
      alert('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isEditing) {
        await projectsAPI.update(editingId, formData);
        alert('Project updated successfully!');
      } else {
        await projectsAPI.create(formData);
        alert('Project created successfully!');
      }
      setShowModal(false);
      setIsEditing(false);
      setEditingId(null);
      setFormData({
        title: '',
        description: '',
        instructor_id: user.id,
        start_date: '',
        end_date: '',
        status: 'active'
      });
      loadProjects();
    } catch (error) {
      alert(error.response?.data?.detail || `Failed to ${isEditing ? 'update' : 'create'} project`);
    }
  };

  const handleEdit = (project) => {
    setIsEditing(true);
    setEditingId(project.id);
    setFormData({
      title: project.title,
      description: project.description || '',
      instructor_id: user.id,
      start_date: project.start_date || '',
      end_date: project.end_date || '',
      status: project.status
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this project?')) return;
    
    try {
      await projectsAPI.delete(id);
      alert('Project deleted successfully!');
      loadProjects();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to delete project');
    }
  };

  if (loading) {
    return <div className="container"><div className="loading">Loading projects...</div></div>;
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: '700' }}>Projects</h1>
        {user.role === 'instructor' && (
          <button className="btn btn-primary" onClick={() => {
            setIsEditing(false);
            setEditingId(null);
            setFormData({
              title: '',
              description: '',
              instructor_id: user.id,
              start_date: '',
              end_date: '',
              status: 'active'
            });
            setShowModal(true);
          }}>
            <Plus size={16} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'middle' }} />
            Create Project
          </button>
        )}
      </div>

      {projects.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <p>No projects yet.</p>
            {user.role === 'instructor' && <p>Create your first project to get started!</p>}
          </div>
        </div>
      ) : (
        <div className="grid grid-2">
          {projects.map((project) => (
            <div key={project.id} className="card">
              <div style={{ marginBottom: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
                    {project.title}
                  </h3>
                  <span className={`badge ${
                    project.status === 'active' ? 'badge-success' : 
                    project.status === 'completed' ? 'badge-info' : 'badge-warning'
                  }`}>
                    {project.status}
                  </span>
                </div>
                <p style={{ color: '#6b7280', fontSize: '14px', marginBottom: '12px' }}>
                  {project.description}
                </p>
                <div style={{ fontSize: '13px', color: '#6b7280' }}>
                  <div style={{ marginBottom: '4px' }}>
                    <strong>Instructor:</strong> {project.instructor?.name || 'N/A'}
                  </div>
                  {project.start_date && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Calendar size={14} />
                      {project.start_date} to {project.end_date}
                    </div>
                  )}
                  <div style={{ marginTop: '4px' }}>
                    <strong>Teams:</strong> {project.teams?.length || 0}
                  </div>
                </div>
              </div>
              
              {user.role === 'instructor' && (
                <div style={{ display: 'flex', gap: '8px', paddingTop: '12px', borderTop: '1px solid #e5e7eb' }}>
                  <button className="btn btn-secondary" onClick={() => handleEdit(project)} style={{ flex: 1 }}>
                    <Edit size={14} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'middle' }} />
                    Edit
                  </button>
                  <button className="btn btn-danger" onClick={() => handleDelete(project.id)} style={{ flex: 1 }}>
                    <Trash2 size={14} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'middle' }} />
                    Delete
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Create/Edit Project Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">{isEditing ? 'Edit Project' : 'Create New Project'}</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="label">Project Title</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g., Software Engineering Mini Project"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label className="label">Description</label>
                <textarea
                  className="textarea"
                  placeholder="Describe the project objectives and requirements"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>

              <div className="grid grid-2">
                <div className="form-group">
                  <label className="label">Start Date</label>
                  <input
                    type="date"
                    className="input"
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  />
                </div>

                <div className="form-group">
                  <label className="label">End Date</label>
                  <input
                    type="date"
                    className="input"
                    value={formData.end_date}
                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="label">Status</label>
                <select
                  className="input"
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  required
                >
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                  <option value="archived">Archived</option>
                </select>
              </div>

              <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>
                  {isEditing ? 'Update Project' : 'Create Project'}
                </button>
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Projects;
