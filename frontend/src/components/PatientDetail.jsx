import React, { useState, useEffect } from 'react';
import { patientsApi } from '../api/patientsApi';

export default function PatientDetail({ patient, onClose }) {
  const [transcripts, setTranscripts] = useState([]);
  const [loadingTranscripts, setLoadingTranscripts] = useState(false);
  const [errorTranscripts, setErrorTranscripts] = useState('');

  useEffect(() => {
    if (patient) {
      setLoadingTranscripts(true);
      setErrorTranscripts('');
      patientsApi.getPatientTranscripts(patient.patient_id)
        .then((data) => {
          setTranscripts(data || []);
          setLoadingTranscripts(false);
        })
        .catch((err) => {
          setErrorTranscripts(err.message || 'Failed to load call transcripts.');
          setLoadingTranscripts(false);
        });
    }
  }, [patient]);

  const formatPhone = (phoneStr) => {
    if (!phoneStr) return '';
    const cleaned = ('' + phoneStr).replace(/\D/g, '');
    const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
    if (match) {
      return `(${match[1]}) ${match[2]}-${match[3]}`;
    }
    return phoneStr;
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      const parts = dateStr.split('-');
      if (parts.length === 3) {
        const [year, month, day] = parts;
        return new Date(year, month - 1, day).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });
      }
      return new Date(dateStr).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  const formatTimestamp = (tsStr) => {
    if (!tsStr) return '';
    try {
      return new Date(tsStr).toLocaleString(undefined, {
        dateStyle: 'medium',
        timeStyle: 'short'
      });
    } catch {
      return tsStr;
    }
  };

  if (!patient) return null;

  return (
    <div className="detail-panel-backdrop" onClick={onClose}>
      <div className="detail-panel-content" onClick={(e) => e.stopPropagation()}>
        <div className="detail-panel-header">
          <div>
            <div className="patient-id-badge">ID: {patient.patient_id}</div>
            <h2>{patient.last_name}, {patient.first_name}</h2>
          </div>
          <button className="btn-close-panel" onClick={onClose} aria-label="Close details">
            &times;
          </button>
        </div>

        <div className="detail-scrollable-body">
          <div className="detail-grid-cols">
            
            {/* Demographics Card Section */}
            <div className="detail-card-col">
              <div className="detail-info-group">
                <h3>Demographics</h3>
                <div className="info-rows">
                  <div className="info-row">
                    <span className="info-label">Full Name</span>
                    <span className="info-val">{patient.first_name} {patient.last_name}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Date of Birth</span>
                    <span className="info-val">{formatDate(patient.date_of_birth)}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Sex</span>
                    <span className="info-val">{patient.sex}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Preferred Language</span>
                    <span className="info-val">{patient.preferred_language}</span>
                  </div>
                </div>
              </div>

              <div className="detail-info-group">
                <h3>Contact & Address Details</h3>
                <div className="info-rows">
                  <div className="info-row">
                    <span className="info-label">Phone</span>
                    <span className="info-val">{formatPhone(patient.phone_number)}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Email</span>
                    <span className="info-val">{patient.email || <span className="text-null">Not Provided</span>}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Address</span>
                    <span className="info-val">
                      {patient.address_line_1}
                      {patient.address_line_2 ? `, ${patient.address_line_2}` : ''}
                      <br />
                      {patient.city}, {patient.state} {patient.zip_code}
                    </span>
                  </div>
                </div>
              </div>

              <div className="detail-info-group">
                <h3>Insurance & Emergency Details</h3>
                <div className="info-rows">
                  <div className="info-row">
                    <span className="info-label">Provider</span>
                    <span className="info-val">{patient.insurance_provider || <span className="text-null">Self-Pay / None</span>}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Member ID</span>
                    <span className="info-val">{patient.insurance_member_id || <span className="text-null">N/A</span>}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Emergency Name</span>
                    <span className="info-val">{patient.emergency_contact_name || <span className="text-null">Not Provided</span>}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Emergency Phone</span>
                    <span className="info-val">{formatPhone(patient.emergency_contact_phone) || <span className="text-null">N/A</span>}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Transcripts Card Section */}
            <div className="detail-card-col scroll-y-section">
              <h3>Call Registry Logs</h3>
              {loadingTranscripts && (
                <div className="spinner-box">
                  <div className="spinner"></div>
                  <p>Loading call history...</p>
                </div>
              )}
              {errorTranscripts && <div className="error-card">{errorTranscripts}</div>}
              
              {!loadingTranscripts && transcripts.length === 0 && (
                <div className="empty-transcripts-box">
                  <div className="empty-call-icon">📞</div>
                  <p>No call registry transcripts recorded for this patient.</p>
                </div>
              )}

              {!loadingTranscripts && transcripts.length > 0 && (
                <div className="transcripts-timeline">
                  {transcripts.map((log) => (
                    <div key={log.id} className="transcript-block">
                      <div className="transcript-block-header">
                        <span className="call-id-tag">Call: {log.vapi_call_id.substring(0, 8)}...</span>
                        <span className={`status-pill pill-${(log.call_status || 'ended').toLowerCase()}`}>
                          {log.call_status}
                        </span>
                      </div>
                      
                      <div className="call-meta-date">
                        Time: {formatTimestamp(log.created_at)}
                      </div>

                      {log.call_summary && (
                        <div className="summary-field">
                          <strong>AI Executive Summary:</strong>
                          <p>{log.call_summary}</p>
                        </div>
                      )}

                      {log.transcript && (
                        <div className="transcript-field">
                          <strong>Full Call Dialog:</strong>
                          <div className="transcript-text-container">
                            {log.transcript.split('\n').map((line, idx) => (
                              <p key={idx} className="transcript-line">{line}</p>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
