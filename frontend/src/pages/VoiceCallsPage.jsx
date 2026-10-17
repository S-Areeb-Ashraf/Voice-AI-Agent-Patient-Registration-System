import React, { useEffect, useState } from 'react';
import { callsApi } from '../api/callsApi';
import { IconPhone, IconArrow, IconEye } from '../components/Icons';

export default function VoiceCallsPage({ onViewCall }) {
  const [calls, setCalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    callsApi.getCalls()
      .then((data) => { setCalls(data || []); setLoading(false); })
      .catch((err) => { setError(err.message || 'Failed to load calls'); setLoading(false); });
  }, []);

  const formatTS = (ts) => {
    if (!ts) return '—';
    try { return new Date(ts).toLocaleString(); } catch { return ts; }
  };

  return (
    <div>
      <div className="page-header">
        <h2>Voice Calls</h2>
        <p>All recorded voice-call transcripts stored in the database</p>
      </div>

      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title-icon"><IconPhone size={14} /> Recorded Calls</h3>
            <p className="card-subtitle">Showing recent call transcripts</p>
          </div>
        </div>
        <div className="card-body-flush">
          {loading ? (
            <div className="loading-state"><div className="spinner"></div>Loading calls…</div>
          ) : error ? (
            <div className="alert alert-error">⚠ {error}</div>
          ) : calls.length === 0 ? (
            <div className="empty-state"><div className="empty-state-icon"><IconPhone size={40} /></div><h4>No calls found</h4><p>Recorded call transcripts will appear here when available.</p></div>
          ) : (
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Call ID</th>
                    <th>Patient</th>
                    <th>Phone</th>
                    <th>Status</th>
                    <th>Date</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {calls.map((c) => (
                    <tr key={c.id}>
                      <td className="mono" style={{ fontSize: '12px' }}>{c.vapi_call_id}</td>
                      <td className="mono" style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                        {c.patient_id ? `${String(c.patient_id).substring(0, 12)}…` : '—'}
                      </td>
                      <td className="mono" style={{ fontSize: '12.5px' }}>{c.caller_phone_number || '—'}</td>
                      <td>
                        <span className={`status-pill ${String(c.call_status || '').toLowerCase().includes('end') ? 'ok' : 'neutral'}`}>
                          {c.call_status || '—'}
                        </span>
                      </td>
                      <td style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>{formatTS(c.created_at)}</td>
                      <td>
                        <button className="btn btn-ghost btn-sm" onClick={() => onViewCall(c.id)}>
                          <IconEye size={13} /> View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
