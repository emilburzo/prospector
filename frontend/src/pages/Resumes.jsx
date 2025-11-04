import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, CheckCircle, X } from 'lucide-react';
import { resumesApi } from '../api/client';

function Resumes() {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingResume, setEditingResume] = useState(null);
  const [formData, setFormData] = useState({
    content: '',
    file_name: '',
  });

  useEffect(() => {
    loadResumes();
  }, []);

  const loadResumes = async () => {
    try {
      const response = await resumesApi.getAll();
      setResumes(response.data);
    } catch (error) {
      console.error('Error loading resumes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingResume) {
        await resumesApi.update(editingResume.id, formData);
      } else {
        await resumesApi.create(formData);
      }

      setShowModal(false);
      resetForm();
      loadResumes();
    } catch (error) {
      console.error('Error saving resume:', error);
      alert('Error saving resume. Please try again.');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this resume?')) return;

    try {
      await resumesApi.delete(id);
      loadResumes();
    } catch (error) {
      console.error('Error deleting resume:', error);
    }
  };

  const handleEdit = (resume) => {
    setEditingResume(resume);
    setFormData({
      content: resume.content || '',
      file_name: resume.file_name || '',
    });
    setShowModal(true);
  };

  const handleSetActive = async (id) => {
    try {
      await resumesApi.update(id, { is_active: true });
      loadResumes();
    } catch (error) {
      console.error('Error setting active resume:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      content: '',
      file_name: '',
    });
    setEditingResume(null);
  };

  if (loading) {
    return <div className="text-center py-12">Loading...</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Resumes</h2>
        <button
          onClick={() => setShowModal(true)}
          className="btn-primary flex items-center"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Resume
        </button>
      </div>

      <div className="card bg-accent-primary/10 border-accent-primary mb-6">
        <p className="text-sm text-dark-text">
          The active resume is used for AI analysis when evaluating job leads. Only one resume can be active at a time.
        </p>
      </div>

      {resumes.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-dark-muted">No resumes yet. Create your first one!</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {resumes.map((resume) => (
            <div key={resume.id} className="card hover:border-accent-primary transition-colors">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold">
                      {resume.file_name || `Resume ${resume.id}`}
                    </h3>
                    {resume.is_active && (
                      <span className="badge badge-success flex items-center">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Active
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-dark-muted mb-2">
                    {resume.content.substring(0, 200)}...
                  </p>
                  <p className="text-sm text-dark-muted">
                    Created: {new Date(resume.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex flex-col gap-2">
                  {!resume.is_active && (
                    <button
                      onClick={() => handleSetActive(resume.id)}
                      className="btn-success flex items-center"
                      title="Set as Active"
                    >
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Set Active
                    </button>
                  )}
                  <button
                    onClick={() => handleEdit(resume)}
                    className="btn-secondary flex items-center"
                    title="Edit"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(resume.id)}
                    className="btn-danger flex items-center"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-dark-card rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">
                {editingResume ? 'Edit Resume' : 'New Resume'}
              </h3>
              <button
                onClick={() => { setShowModal(false); resetForm(); }}
                className="text-dark-muted hover:text-dark-text"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="label">File Name (optional)</label>
                <input
                  type="text"
                  className="input"
                  value={formData.file_name}
                  onChange={(e) => setFormData({ ...formData, file_name: e.target.value })}
                  placeholder="My Resume - Software Engineer"
                />
              </div>

              <div>
                <label className="label">Resume Content</label>
                <textarea
                  className="textarea min-h-[400px]"
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  placeholder="Paste your resume text here..."
                  required
                />
                <p className="text-xs text-dark-muted mt-2">
                  Paste the plain text version of your resume. This will be used by AI to analyze job matches.
                </p>
              </div>

              <div className="flex gap-3">
                <button type="submit" className="btn-primary flex-1">
                  {editingResume ? 'Update' : 'Create'}
                </button>
                <button
                  type="button"
                  onClick={() => { setShowModal(false); resetForm(); }}
                  className="btn-secondary"
                >
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

export default Resumes;
