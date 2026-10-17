import React from 'react';
import {
  IconUsers,
  IconMic,
  IconBuilding,
  IconPhone,
  IconChip,
  IconPlug,
  IconHook,
  IconArrow,
} from '../components/Icons';

export default function DashboardPage({ patients, onGoToPatients, onViewPatient, totalCalls = null }) {
  const totalPatients = patients.length;
  const recentPatients = patients.slice(0, 5);

  const formatPhone = (phoneStr) => {
    if (!phoneStr) return '—';
    const cleaned = ('' + phoneStr).replace(/\D/g, '');
    const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
    return match ? `(${match[1]}) ${match[2]}-${match[3]}` : phoneStr;
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '—';
    try {
      const [y, m, d] = dateStr.split('-');
      return new Date(y, m - 1, d).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    } catch { return dateStr; }
  };

  return (
    <div>
      <div className="page-header">
        <h2>Overview</h2>
        <p>Real-time snapshot of your clinic's patient intake activity</p>
      </div>

      {/* Stats Row */}
      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-icon-wrap blue"><IconUsers size={20} /></div>
          <div className="stat-info">
            <label>Registered Patients</label>
            <div className="stat-value">{totalPatients}</div>
            <div className="stat-sub">Active records</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrap cyan"><IconMic size={20} /></div>
          <div className="stat-info">
            <label>Voice Agent</label>
            <div className="stat-value" style={{ fontSize: '18px', marginTop: '4px', color: 'var(--success)' }}>Online</div>
            <div className="stat-sub">Vapi + Gemini LLM</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrap green"><IconBuilding size={20} /></div>
          <div className="stat-info">
            <label>Clinic Status</label>
            <div className="stat-value" style={{ fontSize: '18px', marginTop: '4px', color: 'var(--success)' }}>Receiving</div>
            <div className="stat-sub">Accepting new patients</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrap purple"><IconPhone size={20} /></div>
          <div className="stat-info">
            <label>Total Calls</label>
            <div className="stat-value">{totalCalls === null ? '—' : totalCalls}</div>
            <div className="stat-sub">Lifetime call records</div>
          </div>
        </div>
      </div>

      {/* Recent Patients Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3>Recently Registered Patients</h3>
            <p className="card-subtitle">The most recent intakes via Voice Agent or API</p>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={onGoToPatients}>
            View All <IconArrow size={14} />
          </button>
        </div>
        <div className="card-body-flush">
          {totalPatients === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">🗂️</div>
              <h4>No patients registered yet</h4>
              <p>Patients registered via the Vapi Voice Agent or the API will appear here.</p>
            </div>
          ) : (
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Patient</th>
                    <th>DOB</th>
                    <th>Phone</th>
                    <th>Location</th>
                    <th>Sex</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {recentPatients.map((p) => {
                    const sexClass = p.sex === 'Male' ? 'badge-male'
                      : p.sex === 'Female' ? 'badge-female'
                      : p.sex === 'Other' ? 'badge-other'
                      : 'badge-decline';

                    const initials = `${p.first_name?.[0] || ''}${p.last_name?.[0] || ''}`.toUpperCase();

                    return (
                      <tr key={p.patient_id} onClick={() => onViewPatient(p.patient_id)}>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <div className="table-avatar">{initials}</div>
                            <div>
                              <span className="pt-name-primary">{p.last_name}, {p.first_name}</span>
                              <span className="pt-name-id">{p.patient_id.substring(0, 12)}…</span>
                            </div>
                          </div>
                        </td>
                        <td style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>{formatDate(p.date_of_birth)}</td>
                        <td style={{ color: 'var(--text-secondary)', fontSize: '13px', fontFamily: 'var(--mono)' }}>{formatPhone(p.phone_number)}</td>
                        <td style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>{p.city}, {p.state}</td>
                        <td><span className={`badge ${sexClass}`}>{p.sex}</span></td>
                        <td>
                          <button
                            className="btn btn-ghost btn-sm"
                            onClick={(e) => { e.stopPropagation(); onViewPatient(p.patient_id); }}
                          >
                            View →
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Info cards row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px' }}>
        <div className="card">
          <div className="card-header">
            <div>
              <h3>Vapi Integration</h3>
              <p className="card-subtitle">Voice agent architecture</p>
            </div>
          </div>
          <div className="card-body">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {[
                { icon: <IconPhone size={14} />, label: 'Telephony', value: 'Vapi' },
                { icon: <IconChip size={14} />, label: 'LLM Provider', value: 'Google Gemini' },
                { icon: <IconPlug size={14} />, label: 'Tool Hook', value: 'POST /vapi-tools/handle' },
                { icon: <IconHook size={14} />, label: 'Webhook', value: 'POST /vapi-webhook/events' },
              ].map(({ icon, label, value }) => (
                <div key={label} className="inline-row">
                  <span className="inline-row-label"><span className="inline-row-icon" aria-hidden="true">{icon}</span> {label}</span>
                  <span className="inline-row-value mono">{value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <div>
              <h3>System Health</h3>
              <p className="card-subtitle">Backend & database status</p>
            </div>
          </div>
          <div className="card-body">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {[
                { label: 'FastAPI Backend', status: 'Operational', ok: true },
                { label: 'Supabase Postgres', status: 'Connected', ok: true },
                { label: 'Vapi Voice Agent', status: 'Active', ok: true },
                { label: 'Webhook Listener', status: 'Listening', ok: true },
              ].map(({ label, status, ok }) => (
                <div key={label} className="inline-row">
                  <span className="inline-row-label">{label}</span>
                  <span className={`status-pill ${ok ? 'ok' : 'down'}`}>{status}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
