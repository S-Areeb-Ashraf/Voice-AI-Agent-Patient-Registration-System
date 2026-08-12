import React, { useEffect, useState } from 'react';
import { callsApi } from '../api/callsApi';

export default function VoiceCallDetailPage({ callId, onBack }) {
  const [call, setCall] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!callId) return;
    setLoading(true);
    callsApi.getCallById(callId)
      .then((data) => { setCall(data); setLoading(false); })
      .catch((err) => { setError(err.message || 'Failed to load call'); setLoading(false); });
  }, [callId]);

  const formatTS = (ts) => {
    if (!ts) return '—';
    try { return new Date(ts).toLocaleString(); } catch { return ts; }
  };

  if (loading) return (
    <div className="detail-page">
      <button className="btn-back" onClick={onBack}>← Back to Calls</button>
      <div className="loading-state"><div className="spinner"></div>Loading call…</div>
    </div>
  );

  if (error || !call) return (
    <div className="detail-page">
      <button className="btn-back" onClick={onBack}>← Back to Calls</button>
      <div className="alert alert-error">⚠ {error || 'Call not found.'}</div>
    </div>
  );

  return (
    <div className="detail-page">
      <div className="detail-breadcrumb">
        <button className="btn-back" onClick={onBack}>← Back to Calls</button>
      </div>

      <div className="card">
        <div className="card-header">
          <div>
            <h3>Call Details</h3>
            <p className="card-subtitle">Details for call {call.vapi_call_id}</p>
          </div>
        </div>
        <div className="card-body">
          <div className="info-list">
            <div className="info-item"><span className="info-label">Call ID</span><span className="info-value mono">{call.vapi_call_id}</span></div>
            <div className="info-item"><span className="info-label">Patient ID</span><span className="info-value mono">{call.patient_id || '—'}</span></div>
            <div className="info-item"><span className="info-label">Phone</span><span className="info-value mono">{call.caller_phone_number || '—'}</span></div>
            <div className="info-item"><span className="info-label">Status</span><span className="info-value">{call.call_status || '—'}</span></div>
            <div className="info-item"><span className="info-label">Date</span><span className="info-value">{formatTS(call.created_at)}</span></div>
          </div>

          {call.call_summary && (
            <div style={{ marginTop: '16px' }}>
              <h4>Summary</h4>
              <p>{call.call_summary}</p>
            </div>
          )}

          {call.transcript && (
            <div style={{ marginTop: '16px' }}>
              <h4>Transcript</h4>
              <div className="transcript-dialog-body">
                {call.transcript.split('\n').filter(l => l.trim()).map((line, i) => (
                  <div key={i} className="dialog-line">{line}</div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
