import { useState, useEffect } from 'react';
import { formsAPI, projectsAPI } from '../api';
import { Plus, Edit, Trash2, FileText, List } from 'lucide-react';

function Forms({ user }) {
  const [forms, setForms] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    project_id: '',
    title: '',
    description: '',
    max_score: 100,
    criteria: [{ name: '', description: '', max_points: 10, order_index: 0 }]
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [formsRes, projectsRes] = await Promise.all([
        formsAPI.list(),
        projectsAPI.list()
      ]);
      
      setForms(formsRes.data.forms || []);
      setProjects(projectsRes.data.projects || []);
      console.log('Loaded forms:', formsRes.data.forms);
    } catch (error) {
      console.error('Failed to load data:', error);
      alert('Failed to load forms');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate criteria points sum
    const totalPoints = formData.criteria.reduce((sum, c) => sum + parseInt(c.max_points || 0), 0);
    if (totalPoints !== parseInt(formData.max_score)) {
      alert(`Criteria points (${totalPoints}) must sum to max score (${formData.max_score})`);
      return;
    }

    try {
      const submitData = {
        ...formData,
        project_id: parseInt(formData.project_id),
        max_score: parseInt(formData.max_score),
        criteria: formData.criteria.map((c, idx) => ({
          text: c.name,
          description: c.description,
          max_points: parseInt(c.max_points),
          order_index: idx
        }))
      };

      if (isEditing) {
        await formsAPI.update(editingId, {
          title: formData.title,
          description: formData.description,
          max_score: parseInt(formData.max_score)
        });
        alert('Form updated successfully!');
      } else {
        await formsAPI.create(submitData);
        alert('Form created successfully!');
      }
      
      setShowModal(false);
      resetForm();
      loadData();
    } catch (error) {
      alert(error.response?.data?.detail || `Failed to ${isEditing ? 'update' : 'create'} form`);
    }
  };

  const resetForm = () => {
    setIsEditing(false);
    setEditingId(null);
    setFormData({
      project_id: '',
      title: '',
      description: '',
      max_score: 100,
      criteria: [{ name: '', description: '', max_points: 10, order_index: 0 }]
    });
  };

  const handleEdit = (form) => {
    setIsEditing(true);
    setEditingId(form.id);
    setFormData({
      project_id: form.project_id || '',
      title: form.title,
      description: form.description || '',
      max_score: form.max_score,
      criteria: form.criteria.map(c => ({
        name: c.text || c.name,
        description: c.description || '',
        max_points: c.max_points,
        order_index: c.order_index
      }))
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this form?')) return;
    
    try {
      await formsAPI.delete(id);
      alert('Form deleted successfully!');
      loadData();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to delete form');
    }
  };

  const addCriterion = () => {
    setFormData({
      ...formData,
      criteria: [
        ...formData.criteria,
        { name: '', description: '', max_points: 10, order_index: formData.criteria.length }
      ]
    });
  };

  const removeCriterion = (index) => {
    if (formData.criteria.length <= 1) {
      alert('Form must have at least one criterion');
      return;
    }
    setFormData({
      ...formData,
      criteria: formData.criteria.filter((_, idx) => idx !== index)
    });
  };

  const updateCriterion = (index, field, value) => {
    const newCriteria = [...formData.criteria];
    newCriteria[index][field] = value;
    setFormData({ ...formData, criteria: newCriteria });
  };

  if (loading) {
    return <div className="container"><div className="loading">Loading forms...</div></div>;
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: '700' }}>Evaluation Forms</h1>
        {user.role === 'instructor' && (
          <button className="btn btn-primary" onClick={() => {
            resetForm();
            setShowModal(true);
          }}>
            <Plus size={16} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'middle' }} />
            Create Form
          </button>
        )}
      </div>

      {forms.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <p>No evaluation forms yet.</p>
            {user.role === 'instructor' && <p>Create your first evaluation form to get started!</p>}
          </div>
        </div>
      ) : (
        <div className="grid grid-2">
          {forms.map((form) => (
            <div key={form.id} className="card">
              <div style={{ marginBottom: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'start', gap: '12px', marginBottom: '12px' }}>
                  <div style={{ 
                    width: '40px', 
                    height: '40px', 
                    borderRadius: '8px', 
                    background: '#dbeafe', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    flexShrink: 0
                  }}>
                    <FileText size={20} color="#3b82f6" />
                  </div>
                  <div style={{ flex: 1 }}>
                    <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '4px' }}>
                      {form.title}
                    </h3>
                    <p style={{ fontSize: '13px', color: '#6b7280' }}>
                      {form.project?.title || 'No project'}
                    </p>
                  </div>
                </div>
                
                <p style={{ color: '#6b7280', fontSize: '14px', marginBottom: '12px' }}>
                  {form.description || 'No description'}
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                  <div style={{ padding: '8px', background: '#f3f4f6', borderRadius: '6px' }}>
                    <div style={{ fontSize: '11px', color: '#6b7280', marginBottom: '2px' }}>Max Score</div>
                    <div style={{ fontSize: '16px', fontWeight: '600', color: '#4f46e5' }}>
                      {form.max_score}
                    </div>
                  </div>
                  <div style={{ padding: '8px', background: '#f3f4f6', borderRadius: '6px' }}>
                    <div style={{ fontSize: '11px', color: '#6b7280', marginBottom: '2px' }}>Criteria</div>
                    <div style={{ fontSize: '16px', fontWeight: '600', color: '#10b981' }}>
                      {form.criteria_count || form.criteria?.length || 0}
                    </div>
                  </div>
                </div>

                {form.criteria && form.criteria.length > 0 && (
                  <div style={{ marginBottom: '12px' }}>
                    <div style={{ fontSize: '13px', fontWeight: '500', color: '#6b7280', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <List size={14} />
                      Criteria:
                    </div>
                    <div style={{ fontSize: '12px' }}>
                      {form.criteria.slice(0, 3).map((criterion, idx) => (
                        <div key={idx} style={{ padding: '4px 0', color: '#374151', display: 'flex', justifyContent: 'space-between' }}>
                          <span>• {criterion.text || criterion.name}</span>
                          <span style={{ fontWeight: '600', color: '#6b7280' }}>({criterion.max_points} pts)</span>
                        </div>
                      ))}
                      {form.criteria.length > 3 && (
                        <div style={{ padding: '4px 0', color: '#9ca3af', fontStyle: 'italic' }}>
                          + {form.criteria.length - 3} more...
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
              
              {user.role === 'instructor' && (
                <div style={{ display: 'flex', gap: '8px', paddingTop: '12px', borderTop: '1px solid #e5e7eb' }}>
                  <button className="btn btn-secondary" onClick={() => handleEdit(form)} style={{ flex: 1 }}>
                    <Edit size={14} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'middle' }} />
                    Edit
                  </button>
                  <button className="btn btn-danger" onClick={() => handleDelete(form.id)} style={{ flex: 1 }}>
                    <Trash2 size={14} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'middle' }} />
                    Delete
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Create/Edit Form Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '700px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div className="modal-header">
              <h2 className="modal-title">{isEditing ? 'Edit Evaluation Form' : 'Create New Evaluation Form'}</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="label">Form Title</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g., Peer Evaluation Form - Sprint 1"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label className="label">Project</label>
                <select
                  className="input"
                  value={formData.project_id}
                  onChange={(e) => setFormData({ ...formData, project_id: e.target.value })}
                  required
                  disabled={isEditing}
                >
                  <option value="">Select a project</option>
                  {projects.map((project) => (
                    <option key={project.id} value={project.id}>
                      {project.title}
                    </option>
                  ))}
                </select>
                {isEditing && (
                  <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                    Project cannot be changed when editing
                  </p>
                )}
              </div>

              <div className="form-group">
                <label className="label">Description (Optional)</label>
                <textarea
                  className="textarea"
                  placeholder="Describe the purpose of this evaluation form..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows="3"
                />
              </div>

              <div className="form-group">
                <label className="label">Maximum Score</label>
                <input
                  type="number"
                  className="input"
                  placeholder="100"
                  value={formData.max_score}
                  onChange={(e) => setFormData({ ...formData, max_score: e.target.value })}
                  min="1"
                  required
                />
                <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                  Total of all criteria max points must equal this value
                </p>
              </div>

              <div className="form-group">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <label className="label" style={{ margin: 0 }}>Evaluation Criteria</label>
                  <button type="button" className="btn btn-secondary" onClick={addCriterion} style={{ padding: '4px 12px', fontSize: '13px' }}>
                    <Plus size={14} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'middle' }} />
                    Add Criterion
                  </button>
                </div>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {formData.criteria.map((criterion, index) => (
                    <div key={index} style={{ border: '1px solid #e5e7eb', borderRadius: '8px', padding: '12px', background: '#f9fafb' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <span style={{ fontSize: '13px', fontWeight: '600', color: '#6b7280' }}>
                          Criterion {index + 1}
                        </span>
                        {formData.criteria.length > 1 && (
                          <button
                            type="button"
                            onClick={() => removeCriterion(index)}
                            style={{ 
                              background: 'none', 
                              border: 'none', 
                              color: '#ef4444', 
                              cursor: 'pointer',
                              fontSize: '12px',
                              padding: '4px 8px'
                            }}
                          >
                            Remove
                          </button>
                        )}
                      </div>
                      
                      <input
                        type="text"
                        className="input"
                        placeholder="Criterion name (e.g., Communication Skills)"
                        value={criterion.name}
                        onChange={(e) => updateCriterion(index, 'name', e.target.value)}
                        required
                        style={{ marginBottom: '8px' }}
                      />
                      
                      <textarea
                        className="textarea"
                        placeholder="Description (optional)"
                        value={criterion.description}
                        onChange={(e) => updateCriterion(index, 'description', e.target.value)}
                        rows="2"
                        style={{ marginBottom: '8px' }}
                      />
                      
                      <input
                        type="number"
                        className="input"
                        placeholder="Max points"
                        value={criterion.max_points}
                        onChange={(e) => updateCriterion(index, 'max_points', e.target.value)}
                        min="1"
                        required
                      />
                    </div>
                  ))}
                </div>
                
                <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '8px' }}>
                  Current total: {formData.criteria.reduce((sum, c) => sum + parseInt(c.max_points || 0), 0)} / {formData.max_score} points
                </p>
              </div>

              <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>
                  {isEditing ? 'Update Form' : 'Create Form'}
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

export default Forms;
