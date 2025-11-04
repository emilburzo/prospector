import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, History, X } from 'lucide-react';
import { applicationsApi } from '../api/client';
import { useNotification } from '../components/NotificationProvider';

const STAGE_OPTIONS = [
  { value: 'not_started', label: 'Not Started', color: 'secondary' },
  { value: 'applied', label: 'Applied', color: 'primary' },
  { value: 'in_progress', label: 'In Progress', color: 'warning' },
  { value: 'offer', label: 'Offer', color: 'success' },
  { value: 'rejected', label: 'Rejected', color: 'danger' },
  { value: 'no_answer', label: 'No Answer', color: 'secondary' },
];

function Applications() {
  const { showToast, showConfirm } = useNotification();
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [editingApp, setEditingApp] = useState(null);
  const [history, setHistory] = useState([]);
  const [formData, setFormData] = useState({
    company_name: '',
    role_name: '',
    stage: 'not_started',
    job_ad_content: '',
    cover_letter: '',
    application_notes: '',
    notes: '',
    match_percentage: '',
  });

  useEffect(() => {
    loadApplications();
  }, []);

  const loadApplications = async () => {
    try {
      const response = await applicationsApi.getAll();
      setApplications(response.data);
    } catch (error) {
      console.error('Error loading applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = {
        ...formData,
        match_percentage: formData.match_percentage ? parseFloat(formData.match_percentage) : null,
      };

      if (editingApp) {
        await applicationsApi.update(editingApp.id, data);
      } else {
        await applicationsApi.create(data);
      }

      setShowModal(false);
      resetForm();
      loadApplications();
      showToast('Application saved successfully!', 'success');
    } catch (error) {
      console.error('Error saving application:', error);
      showToast('Error saving application. Please try again.', 'error');
    }
  };

  const handleDelete = async (id) => {
    const confirmed = await showConfirm('Are you sure you want to delete this application?');
    if (!confirmed) return;

    try {
      await applicationsApi.delete(id);
      loadApplications();
    } catch (error) {
      console.error('Error deleting application:', error);
    }
  };

  const handleEdit = (app) => {
    setEditingApp(app);
    setFormData({
      company_name: app.company_name || '',
      role_name: app.role_name || '',
      stage: app.stage || 'not_started',
      job_ad_content: app.job_ad_content || '',
      cover_letter: app.cover_letter || '',
      application_notes: app.application_notes || '',
      notes: app.notes || '',
      match_percentage: app.match_percentage || '',
    });
    setShowModal(true);
  };

  const showHistory = async (app) => {
    try {
      const response = await applicationsApi.getHistory(app.id);
      setHistory(response.data);
      setShowHistoryModal(true);
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      company_name: '',
      role_name: '',
      stage: 'not_started',
      job_ad_content: '',
      cover_letter: '',
      application_notes: '',
      notes: '',
      match_percentage: '',
    });
    setEditingApp(null);
  };

  const getStageBadgeColor = (stage) => {
    const option = STAGE_OPTIONS.find(opt => opt.value === stage);
    return `badge-${option?.color || 'secondary'}`;
  };

  if (loading) {
    return <div className="text-center py-12">Loading...</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Job Applications</h2>
        <button
          onClick={() => setShowModal(true)}
          className="btn-primary flex items-center"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Application
        </button>
      </div>

      {applications.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-dark-muted">No applications yet. Create your first one!</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {applications.map((app) => (
            <div key={app.id} className="card hover:border-accent-primary transition-colors">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold">{app.company_name}</h3>
                    <span className={`badge ${getStageBadgeColor(app.stage)}`}>
                      {STAGE_OPTIONS.find(opt => opt.value === app.stage)?.label}
                    </span>
                    {app.match_percentage && (
                      <span className="badge badge-primary">
                        {app.match_percentage}% match
                      </span>
                    )}
                  </div>
                  <p className="text-lg text-dark-muted mb-2">{app.role_name}</p>
                  {app.notes && (
                    <p className="text-sm text-dark-muted mt-2">{app.notes}</p>
                  )}
                  <p className="text-sm text-dark-muted mt-2">
                    Updated: {new Date(app.updated_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => showHistory(app)}
                    className="btn-secondary flex items-center"
                    title="View History"
                  >
                    <History className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleEdit(app)}
                    className="btn-secondary flex items-center"
                    title="Edit"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(app.id)}
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
                {editingApp ? 'Edit Application' : 'New Application'}
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
                <label className="label">Company Name</label>
                <input
                  type="text"
                  className="input"
                  value={formData.company_name}
                  onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                  required
                />
              </div>

              <div>
                <label className="label">Role Name</label>
                <input
                  type="text"
                  className="input"
                  value={formData.role_name}
                  onChange={(e) => setFormData({ ...formData, role_name: e.target.value })}
                  required
                />
              </div>

              <div>
                <label className="label">Stage</label>
                <select
                  className="select"
                  value={formData.stage}
                  onChange={(e) => setFormData({ ...formData, stage: e.target.value })}
                >
                  {STAGE_OPTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="label">Match Percentage (0-100)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  className="input"
                  value={formData.match_percentage}
                  onChange={(e) => setFormData({ ...formData, match_percentage: e.target.value })}
                />
              </div>

              <div>
                <label className="label">Job Ad Content</label>
                <textarea
                  className="textarea"
                  value={formData.job_ad_content}
                  onChange={(e) => setFormData({ ...formData, job_ad_content: e.target.value })}
                />
              </div>

              <div>
                <label className="label">Cover Letter</label>
                <textarea
                  className="textarea"
                  value={formData.cover_letter}
                  onChange={(e) => setFormData({ ...formData, cover_letter: e.target.value })}
                />
              </div>

              <div>
                <label className="label">Application Notes</label>
                <textarea
                  className="textarea"
                  value={formData.application_notes}
                  onChange={(e) => setFormData({ ...formData, application_notes: e.target.value })}
                  placeholder="Additional fields required when applying..."
                />
              </div>

              <div>
                <label className="label">Notes</label>
                <textarea
                  className="textarea"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                />
              </div>

              <div className="flex gap-3">
                <button type="submit" className="btn-primary flex-1">
                  {editingApp ? 'Update' : 'Create'}
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

      {/* History Modal */}
      {showHistoryModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-dark-card rounded-lg p-6 max-w-2xl w-full">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">Stage History</h3>
              <button
                onClick={() => setShowHistoryModal(false)}
                className="text-dark-muted hover:text-dark-text"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-3">
              {history.map((entry) => (
                <div key={entry.id} className="border-l-2 border-accent-primary pl-4 py-2">
                  <div className="flex items-center gap-2 mb-1">
                    {entry.previous_stage && (
                      <>
                        <span className={`badge ${getStageBadgeColor(entry.previous_stage)}`}>
                          {STAGE_OPTIONS.find(opt => opt.value === entry.previous_stage)?.label}
                        </span>
                        <span className="text-dark-muted">→</span>
                      </>
                    )}
                    <span className={`badge ${getStageBadgeColor(entry.new_stage)}`}>
                      {STAGE_OPTIONS.find(opt => opt.value === entry.new_stage)?.label}
                    </span>
                  </div>
                  <p className="text-sm text-dark-muted">
                    {new Date(entry.changed_at).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Applications;
