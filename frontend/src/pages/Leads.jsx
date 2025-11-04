import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Sparkles, ArrowRight, X, SortDesc } from 'lucide-react';
import { leadsApi, resumesApi } from '../api/client';

function Leads() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingLead, setEditingLead] = useState(null);
  const [sortByMatch, setSortByMatch] = useState(false);
  const [analyzing, setAnalyzing] = useState(null);
  const [promoting, setPromoting] = useState(null);
  const [activeResume, setActiveResume] = useState(null);
  const [formData, setFormData] = useState({
    company_name: '',
    role_name: '',
    job_ad_content: '',
    job_url: '',
  });

  useEffect(() => {
    loadLeads();
    loadActiveResume();
  }, [sortByMatch]);

  const loadLeads = async () => {
    try {
      const response = await leadsApi.getAll({ sort_by_match: sortByMatch });
      setLeads(response.data);
    } catch (error) {
      console.error('Error loading leads:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadActiveResume = async () => {
    try {
      const response = await resumesApi.getActive();
      setActiveResume(response.data);
    } catch (error) {
      console.error('No active resume found');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingLead) {
        await leadsApi.update(editingLead.id, formData);
      } else {
        await leadsApi.create(formData);
      }

      setShowModal(false);
      resetForm();
      loadLeads();
    } catch (error) {
      console.error('Error saving lead:', error);
      alert('Error saving lead. Please try again.');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this lead?')) return;

    try {
      await leadsApi.delete(id);
      loadLeads();
    } catch (error) {
      console.error('Error deleting lead:', error);
    }
  };

  const handleEdit = (lead) => {
    setEditingLead(lead);
    setFormData({
      company_name: lead.company_name || '',
      role_name: lead.role_name || '',
      job_ad_content: lead.job_ad_content || '',
      job_url: lead.job_url || '',
    });
    setShowModal(true);
  };

  const handleAnalyze = async (leadId) => {
    if (!activeResume) {
      alert('Please create and activate a resume first!');
      return;
    }

    setAnalyzing(leadId);
    try {
      await leadsApi.analyze(leadId);
      loadLeads();
    } catch (error) {
      console.error('Error analyzing lead:', error);
      alert('Error analyzing lead. Please check your OpenRouter API configuration.');
    } finally {
      setAnalyzing(null);
    }
  };

  const handlePromote = async (leadId) => {
    if (!confirm('Promote this lead to a job application?')) return;

    setPromoting(leadId);
    try {
      await leadsApi.promote(leadId);
      loadLeads();
      alert('Lead successfully promoted to application!');
    } catch (error) {
      console.error('Error promoting lead:', error);
      alert('Error promoting lead. Please try again.');
    } finally {
      setPromoting(null);
    }
  };

  const resetForm = () => {
    setFormData({
      company_name: '',
      role_name: '',
      job_ad_content: '',
      job_url: '',
    });
    setEditingLead(null);
  };

  if (loading) {
    return <div className="text-center py-12">Loading...</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Job Leads</h2>
        <div className="flex gap-3">
          <button
            onClick={() => setSortByMatch(!sortByMatch)}
            className={`btn-secondary flex items-center ${sortByMatch ? 'bg-accent-primary text-white' : ''}`}
          >
            <SortDesc className="w-4 h-4 mr-2" />
            {sortByMatch ? 'Sorted by Match' : 'Sort by Match'}
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="btn-primary flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Lead
          </button>
        </div>
      </div>

      {!activeResume && (
        <div className="card bg-accent-warning/10 border-accent-warning mb-4">
          <p className="text-accent-warning">
            No active resume found. Please create and activate a resume in the Resumes tab to use AI analysis.
          </p>
        </div>
      )}

      {leads.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-dark-muted">No job leads yet. Add your first one!</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {leads.map((lead) => (
            <div key={lead.id} className="card hover:border-accent-primary transition-colors">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold">{lead.company_name}</h3>
                    {lead.match_percentage !== null && (
                      <span className="badge badge-primary">
                        {lead.match_percentage}% match
                      </span>
                    )}
                    {lead.is_promoted && (
                      <span className="badge badge-success">Promoted</span>
                    )}
                  </div>
                  <p className="text-lg text-dark-muted mb-2">{lead.role_name}</p>
                  {lead.job_url && (
                    <a
                      href={lead.job_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-accent-primary hover:underline mb-2 block"
                    >
                      View Job Posting
                    </a>
                  )}
                  {lead.match_reasoning && (
                    <div className="mt-3 p-3 bg-dark-bg rounded">
                      <p className="text-sm text-dark-muted">{lead.match_reasoning}</p>
                    </div>
                  )}
                  <p className="text-sm text-dark-muted mt-2">
                    Added: {new Date(lead.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex flex-col gap-2">
                  {!lead.is_promoted && (
                    <>
                      <button
                        onClick={() => handleAnalyze(lead.id)}
                        disabled={analyzing === lead.id || !activeResume}
                        className="btn-primary flex items-center"
                        title="Analyze with AI"
                      >
                        <Sparkles className="w-4 h-4 mr-2" />
                        {analyzing === lead.id ? 'Analyzing...' : 'Analyze'}
                      </button>
                      <button
                        onClick={() => handlePromote(lead.id)}
                        disabled={promoting === lead.id}
                        className="btn-success flex items-center"
                        title="Promote to Application"
                      >
                        <ArrowRight className="w-4 h-4 mr-2" />
                        {promoting === lead.id ? 'Promoting...' : 'Promote'}
                      </button>
                    </>
                  )}
                  <button
                    onClick={() => handleEdit(lead)}
                    className="btn-secondary flex items-center"
                    title="Edit"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(lead.id)}
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
                {editingLead ? 'Edit Lead' : 'New Lead'}
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
                <label className="label">Job URL (optional)</label>
                <input
                  type="url"
                  className="input"
                  value={formData.job_url}
                  onChange={(e) => setFormData({ ...formData, job_url: e.target.value })}
                  placeholder="https://..."
                />
              </div>

              <div>
                <label className="label">Job Ad Content</label>
                <textarea
                  className="textarea min-h-[200px]"
                  value={formData.job_ad_content}
                  onChange={(e) => setFormData({ ...formData, job_ad_content: e.target.value })}
                  placeholder="Paste the full job posting here..."
                  required
                />
              </div>

              <div className="flex gap-3">
                <button type="submit" className="btn-primary flex-1">
                  {editingLead ? 'Update' : 'Create'}
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

export default Leads;
