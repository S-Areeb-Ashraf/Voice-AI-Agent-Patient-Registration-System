import React, { useState, useEffect } from 'react';
import { patientsApi } from '../api/patientsApi';
import PatientForm from '../components/PatientForm';

export default function PatientDetailPage({ patientId, onBack, onDelete }) {
  const [patient, setPatient] = useState(null);
  const [transcripts, setTranscripts] = useState([]);
  const [loadingPatient, setLoadingPatient] = useState(true);
  const [loadingTranscripts, setLoadingTranscripts] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [showEdit, setShowEdit] = useState(false);

  // Load patient data
  useEffect(() => {
    if (!patientId) return;
    setLoadingPatient(true);
    setError('');
    patientsApi.getPatientById(patientId)
      .then((data) => {
        setPatient(data);
        setLoadingPatient(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load patient.');
        setLoadingPatient(false);
      });
  }, [patientId]);

  // Load transcripts
  useEffect(() => {
    if (!patientId) return;
    setLoadingTranscripts(true);
    patientsApi.getPatientTranscripts(patientId)
      .then((data) => {
        setTranscripts(data || []);
        setLoadingTranscripts(false);
      })
      .catch(() => {
        setLoadingTranscripts(false);
      });
  }, [patientId]);

  // ── Formatters ──
  const formatPhone = (phoneStr) => {
    if (!phoneStr) return '—';
    const c = ('' + phoneStr).replace(/\D/g, '');
    const m = c.match(/^(\d{3})(\d{3})(\d{4})$/);
    return m ? `(${m[1]}) ${m[2]}-${m[3]}` : phoneStr;
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '—';
    try {
      const [y, mo, d] = dateStr.split('-');
      return new Date(y, mo - 1, d).toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' });
    } catch { return dateStr; }
  };

  const formatTS = (tsStr) => {
    if (!tsStr) return '—';
    try {
      return new Date(tsStr).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
    } catch { return tsStr; }
  };

  // ── Loading state ──
  if (loadingPatient) {
    return (
      <div className="detail-page">
        <button className="btn-back" onClick={onBack}>← Back to Patients</button>
        <div className="loading-state" style={{ padding: '80px' }}>
          <div className="spinner"></div>
          Loading patient chart…
        </div>
      </div>
    );
  }

  if (error || !patient) {
    return (
      <div className="detail-page">
        <button className="btn-back" onClick={onBack}>← Back to Patients</button>
        <div className="alert alert-error" style={{ marginTop: '16px' }}>
          ⚠ {error || 'Patient not found.'}
        </div>
      </div>
    );
  }

  const initials = `${patient.first_name?.[0] || ''}${patient.last_name?.[0] || ''}`.toUpperCase();
  const sexClass = patient.sex === 'Male' ? 'badge-male'
    : patient.sex === 'Female' ? 'badge-female'
    : patient.sex === 'Other' ? 'badge-other' : 'badge-decline';

  const getStatusClass = (status) => {
    if (!status) return 'status-default';
    const s = status.toLowerCase();
    if (s.includes('end') || s.includes('complet')) return 'status-ended';
    if (s.includes('active') || s.includes('progress')) return 'status-active';
    return 'status-default';
  };

  return (
    <div className="detail-page">
      {/* Breadcrumb */}
      <div className="detail-breadcrumb">
        <button className="btn-back" onClick={onBack}>← Back to Registry</button>
      </div>

      {/* Hero Header */}
      <div className="patient-hero">
        <div className="patient-hero-left">
          <div className="patient-avatar">{initials}</div>
          <div className="patient-hero-info">
            <h2>{patient.first_name} {patient.last_name}</h2>
            <div className="patient-meta-row">
              <div className="meta-chip">
                <span className="chip-icon">🎂</span>
                {formatDate(patient.date_of_birth)}
              </div>
              <div className="meta-chip">
                <span className={`badge ${sexClass}`}>{patient.sex}</span>
              </div>
              <div className="meta-chip">
                <span className="chip-icon">📞</span>
                {formatPhone(patient.phone_number)}
              </div>
              <div className="meta-chip">
                <span className="chip-icon">🌐</span>
                {patient.preferred_language}
              </div>
              {patient.email && (
                <div className="meta-chip">
                  <span className="chip-icon">✉️</span>
                  {patient.email}
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="patient-hero-right">
          <button className="btn btn-ghost" onClick={() => setShowEdit(true)}>✎ Edit</button>
          <button
            className="btn btn-danger"
            onClick={() => {
              if (window.confirm(`Permanently soft-delete patient ${patient.first_name} ${patient.last_name}?`)) {
                onDelete(patient.patient_id);
                onBack();
              }
            }}
          >
            🗑 Delete Record
          </button>
        </div>
      </div>

      {showEdit && (
        <div>
          <PatientForm initial={patient} onClose={() => setShowEdit(false)} onSaved={() => { setShowEdit(false); patientsApi.getPatientById(patientId).then(d => setPatient(d)); }} />
        </div>
      )}

      {/* Tabs */}
      <div className="card" style={{ overflow: 'visible' }}>
        <div className="tabs-bar">
          <button
            className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            📋 Patient Info
          </button>
          <button
            className={`tab-btn ${activeTab === 'transcripts' ? 'active' : ''}`}
            onClick={() => setActiveTab('transcripts')}
          >
            📞 Call Logs {transcripts.length > 0 && `(${transcripts.length})`}
          </button>
        </div>

        {/* OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <div className="tab-panel">
            <div className="detail-grid">
              {/* Demographics */}
              <div className="card" style={{ background: 'var(--navy-700)' }}>
                <div className="card-header">
                  <h3>👤 Demographics</h3>
                </div>
                <div className="card-body">
                  <div className="info-list">
                    <div className="info-item">
                      <span className="info-label">Full Name</span>
                      <span className="info-value">{patient.first_name} {patient.last_name}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Date of Birth</span>
                      <span className="info-value">{formatDate(patient.date_of_birth)}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Sex</span>
                      <span className="info-value">
                        <span className={`badge ${sexClass}`}>{patient.sex}</span>
                      </span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Preferred Language</span>
                      <span className="info-value">{patient.preferred_language}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Patient ID</span>
                      <span className="info-value mono" style={{ fontSize: '11px' }}>{patient.patient_id}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Registered</span>
                      <span className="info-value" style={{ fontSize: '12.5px' }}>{formatTS(patient.created_at)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Contact */}
              <div className="card" style={{ background: 'var(--navy-700)' }}>
                <div className="card-header">
                  <h3>📬 Contact & Address</h3>
                </div>
                <div className="card-body">
                  <div className="info-list">
                    <div className="info-item">
                      <span className="info-label">Phone</span>
                      <span className="info-value mono">{formatPhone(patient.phone_number)}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Email</span>
                      <span className={`info-value ${!patient.email ? 'dim' : ''}`}>
                        {patient.email || 'Not provided'}
                      </span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Address Line 1</span>
                      <span className="info-value">{patient.address_line_1}</span>
                    </div>
                    {patient.address_line_2 && (
                      <div className="info-item">
                        <span className="info-label">Address Line 2</span>
                        <span className="info-value">{patient.address_line_2}</span>
                      </div>
                    )}
                    <div className="info-item">
                      <span className="info-label">City</span>
                      <span className="info-value">{patient.city}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">State</span>
                      <span className="info-value">{patient.state}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">ZIP Code</span>
                      <span className="info-value mono">{patient.zip_code}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Insurance */}
              <div className="card" style={{ background: 'var(--navy-700)' }}>
                <div className="card-header">
                  <h3>🏥 Insurance</h3>
                </div>
                <div className="card-body">
                  <div className="info-list">
                    <div className="info-item">
                      <span className="info-label">Provider</span>
                      <span className={`info-value ${!patient.insurance_provider ? 'dim' : ''}`}>
                        {patient.insurance_provider || 'Self-Pay / None'}
                      </span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Member ID</span>
                      <span className={`info-value ${!patient.insurance_member_id ? 'dim' : 'mono'}`}>
                        {patient.insurance_member_id || 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Emergency Contact */}
              <div className="card" style={{ background: 'var(--navy-700)' }}>
                <div className="card-header">
                  <h3>🆘 Emergency Contact</h3>
                </div>
                <div className="card-body">
                  <div className="info-list">
                    <div className="info-item">
                      <span className="info-label">Name</span>
                      <span className={`info-value ${!patient.emergency_contact_name ? 'dim' : ''}`}>
                        {patient.emergency_contact_name || 'Not provided'}
                      </span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Phone</span>
                      <span className={`info-value ${!patient.emergency_contact_phone ? 'dim' : 'mono'}`}>
                        {formatPhone(patient.emergency_contact_phone) || 'Not provided'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TRANSCRIPTS TAB */}
        {activeTab === 'transcripts' && (
          <div className="tab-panel">
            {loadingTranscripts ? (
              <div className="loading-state">
                <div className="spinner"></div>
                Loading call logs…
              </div>
            ) : transcripts.length === 0 ? (
              <div className="no-transcripts">
                <div className="no-transcripts-icon">📞</div>
                <h4>No call logs yet</h4>
                <p>Call transcripts will appear here once this patient has interacted with the Vapi Voice Agent.</p>
              </div>
            ) : (
              <div className="transcript-list">
                {transcripts.map((log) => (
                  <div key={log.id} className="transcript-card">
                    {/* Transcript header */}
                    <div className="transcript-card-header">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span className="transcript-call-id">
                          {log.vapi_call_id.length > 16 ? `${log.vapi_call_id.substring(0, 16)}…` : log.vapi_call_id}
                        </span>
                        <span className={`transcript-status ${getStatusClass(log.call_status)}`}>
                          {log.call_status || 'ended'}
                        </span>
                      </div>
                      <span className="transcript-time">{formatTS(log.created_at)}</span>
                    </div>

                    {/* Body */}
                    <div className="transcript-card-body">
                      {/* Caller phone */}
                      {log.caller_phone_number && (
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                          📞 Caller: <span style={{ fontFamily: 'var(--mono)', color: 'var(--text-secondary)' }}>
                            {formatPhone(log.caller_phone_number)}
                          </span>
                        </div>
                      )}

                      {/* Summary */}
                      {log.call_summary && (
                        <div className="transcript-summary">
                          <div className="transcript-summary-label">AI Call Summary</div>
                          <p>{log.call_summary}</p>
                        </div>
                      )}

                      {/* Full transcript */}
                      {log.transcript && (
                        <div>
                          <div className="transcript-dialog-label">Full Call Transcript</div>
                          <div className="transcript-dialog-body">
                            {log.transcript.split('\n').filter(l => l.trim()).map((line, i) => (
                              <div key={i} className="dialog-line">{line}</div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* No content */}
                      {!log.call_summary && !log.transcript && (
                        <div style={{ fontSize: '13px', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                          No transcript or summary available for this call.
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
