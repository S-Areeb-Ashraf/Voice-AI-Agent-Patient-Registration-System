import React, { useEffect, useState } from 'react';
import { callsApi } from '../api/callsApi';
import { IconChat, IconPhone, IconUser } from '../components/Icons';

export default function VoiceCallDetailPage({ callId, onBack }) {
  const [call, setCall] = useState(null);
  const [messages, setMessages] = useState(null); // null until loaded
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!callId) return;
    let active = true;
    setLoading(true);
    callsApi.getCallById(callId)
      .then((data) => { if (active) { setCall(data); setLoading(false); } })
      .catch((err) => { if (active) { setError(err.message || 'Failed to load call'); setLoading(false); } });
    // Conversation script may not exist yet (migration pending) — non-blocking.
    callsApi.getCallMessages(callId)
      .then((data) => { if (active) setMessages(Array.isArray(data) ? data : []); })
      .catch(() => { if (active) setMessages([]); });
    return () => { active = false; };
  }, [callId]);

  const formatTS = (ts) => {
    if (!ts) return '—';
    try { return new Date(ts).toLocaleString(); } catch { return ts; }
  };

  const formatPhone = (phoneStr) => {
    if (!phoneStr) return '—';
    const c = ('' + phoneStr).replace(/\D/g, '');
    const m = c.match(/^(\d{3})(\d{3})(\d{4})$/);
    return m ? `(${m[1]}) ${m[2]}-${m[3]}` : phoneStr;
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

  const hasScript = Array.isArray(messages) && messages.length > 0;

  return (
    <div className="detail-page">
      <div className="detail-breadcrumb">
        <button className="btn-back" onClick={onBack}>← Back to Calls</button>
      </div>

      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title-icon"><IconPhone size={14} /> Call Details</h3>
            <p className="card-subtitle">Details for call {call.vapi_call_id}</p>
          </div>
          {call.call_status && <span className={`status-pill ${String(call.call_status).toLowerCase().includes('end') ? 'ok' : 'neutral'}`}>{call.call_status}</span>}
        </div>
        <div className="card-body">
          <div className="info-list">
            <div className="info-item"><span className="info-label">Call ID</span><span className="info-value mono">{call.vapi_call_id}</span></div>
            <div className="info-item"><span className="info-label">Patient ID</span><span className="info-value mono">{call.patient_id || '—'}</span></div>
            <div className="info-item"><span className="info-label">Phone</span><span className="info-value mono">{formatPhone(call.caller_phone_number)}</span></div>
            <div className="info-item"><span className="info-label">Status</span><span className="info-value">{call.call_status || '—'}</span></div>
            <div className="info-item"><span className="info-label">Date</span><span className="info-value">{formatTS(call.created_at)}</span></div>
          </div>

          {call.call_summary && (
            <div className="transcript-summary" style={{ marginTop: '16px' }}>
              <div className="transcript-summary-label">AI Call Summary</div>
              <p>{call.call_summary}</p>
            </div>
          )}
        </div>
      </div>

      {/* Conversation script — one bubble per spoken turn */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title-icon"><IconChat size={14} /> Conversation Script</h3>
            <p className="card-subtitle">
              {hasScript
                ? `${messages.length} turns — AI assistant vs patient`
                : 'Stored turn-by-turn under the call transcript'}
            </p>
          </div>
        </div>
        <div className="card-body">
          {hasScript ? (
            <div className="chat-thread">
              {messages.map((m) => (
                <div key={m.id} className={`chat-row chat-${m.speaker === 'AI' ? 'ai' : m.speaker === 'Patient' ? 'patient' : 'system'}`}>
                  {m.speaker !== 'System' ? (
                    <div className="chat-avatar" aria-hidden="true">
                      {m.speaker === 'AI' ? <IconChat size={13} /> : <IconUser size={13} />}
                    </div>
                  ) : null}
                  <div className="chat-col">
                    <span className="chat-speaker">
                      {m.speaker === 'AI' ? 'AI Assistant' : m.speaker === 'Patient' ? 'Patient' : 'System'}
                    </span>
                    <div className="chat-bubble">{m.message_text}</div>
                  </div>
                </div>
              ))}
            </div>
          ) : call.transcript ? (
            <div className="transcript-dialog-body">
              {call.transcript.split('\n').filter(l => l.trim()).map((line, i) => (
                <div key={i} className="dialog-line">{line}</div>
              ))}
            </div>
          ) : (
            <div className="empty-state" style={{ padding: '32px 16px' }}>
              <div className="empty-state-icon"><IconChat size={32} /></div>
              <h4>No conversation stored yet</h4>
              <p>The per-turn script for this call will appear once the database migration has been applied and a new call completes.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
