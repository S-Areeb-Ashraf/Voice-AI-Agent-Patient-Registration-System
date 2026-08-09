import React, { useState } from 'react';

export default function PatientsPage({
  patients,
  loading,
  error,
  onSearch,
  onViewPatient,
  onDeletePatient,
  selectedPatientId,
}) {
  const [lastName, setLastName] = useState('');
  const [dob, setDob] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    onSearch({ last_name: lastName, date_of_birth: dob, phone_number: phoneNumber });
  };

  const handleReset = () => {
    setLastName('');
    setDob('');
    setPhoneNumber('');
    onSearch({ last_name: '', date_of_birth: '', phone_number: '' });
  };

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

  const getSexClass = (sex) => {
    if (sex === 'Male') return 'badge-male';
    if (sex === 'Female') return 'badge-female';
    if (sex === 'Other') return 'badge-other';
    return 'badge-decline';
  };

  const getInitials = (p) =>
    `${p.first_name?.[0] || ''}${p.last_name?.[0] || ''}`.toUpperCase();

  return (
    <div className="patients-page-layout">
      {/* Filter bar */}
      <form onSubmit={handleSearch}>
        <div className="filter-bar">
          <div className="filter-bar-inner">
            <div className="filter-group">
              <label htmlFor="fl-name">Last Name</label>
              <input
                id="fl-name"
                type="text"
                className="filter-input"
                placeholder="e.g. O'Connor"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
              />
            </div>
            <div className="filter-group">
              <label htmlFor="fl-dob">Date of Birth</label>
              <input
                id="fl-dob"
                type="date"
                className="filter-input"
                value={dob}
                onChange={(e) => setDob(e.target.value)}
              />
            </div>
            <div className="filter-group">
              <label htmlFor="fl-phone">Phone Number</label>
              <input
                id="fl-phone"
                type="text"
                className="filter-input"
                placeholder="10-digit number"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
              />
            </div>
            <div className="filter-actions">
              <button type="submit" className="btn btn-primary">
                🔍 Search
              </button>
              <button type="button" className="btn btn-ghost" onClick={handleReset}>
                Reset
              </button>
            </div>
          </div>
        </div>
      </form>

      {/* Error alert */}
      {error && <div className="alert alert-error">⚠ {error}</div>}

      {/* Patients Card */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3>Patient Records</h3>
            <p className="card-subtitle">
              {loading ? 'Loading…' : `${patients.length} active patient${patients.length !== 1 ? 's' : ''} found`}
            </p>
          </div>
          {loading && <div className="topbar-loader"></div>}
        </div>
        <div className="card-body-flush">
          {loading && patients.length === 0 ? (
            <div className="loading-state">
              <div className="spinner"></div>
              Fetching patients…
            </div>
          ) : patients.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">🗂️</div>
              <h4>No patients found</h4>
              <p>No active patient records match your search. Try adjusting the filters above or check back once patients register via the Voice Agent.</p>
            </div>
          ) : (
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Patient</th>
                    <th>DOB</th>
                    <th>Sex</th>
                    <th>Phone</th>
                    <th>Language</th>
                    <th>Location</th>
                    <th>Insurance</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {patients.map((p) => {
                    const isSelected = selectedPatientId === p.patient_id;
                    return (
                      <tr
                        key={p.patient_id}
                        className={isSelected ? 'row-selected' : ''}
                        onClick={() => onViewPatient(p.patient_id)}
                      >
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <div style={{
                              width: 34, height: 34, borderRadius: '50%',
                              background: 'linear-gradient(135deg, var(--accent), #1e40af)',
                              display: 'flex', alignItems: 'center', justifyContent: 'center',
                              fontSize: 12, fontWeight: 700, color: '#fff', flexShrink: 0
                            }}>{getInitials(p)}</div>
                            <div>
                              <span className="pt-name-primary">{p.last_name}, {p.first_name}</span>
                              <span className="pt-name-id">{p.patient_id.substring(0, 14)}…</span>
                            </div>
                          </div>
                        </td>
                        <td style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>{formatDate(p.date_of_birth)}</td>
                        <td>
                          <span className={`badge ${getSexClass(p.sex)}`}>{p.sex}</span>
                        </td>
                        <td style={{ color: 'var(--text-secondary)', fontFamily: 'var(--mono)', fontSize: '13px' }}>
                          {formatPhone(p.phone_number)}
                        </td>
                        <td style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>{p.preferred_language}</td>
                        <td style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>{p.city}, {p.state} {p.zip_code}</td>
                        <td style={{ fontSize: '12.5px' }}>
                          {p.insurance_provider ? (
                            <span style={{ color: '#93c5fd' }}>{p.insurance_provider}</span>
                          ) : (
                            <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>Self-Pay</span>
                          )}
                        </td>
                        <td onClick={(e) => e.stopPropagation()}>
                          <div className="table-actions">
                            <button
                              className="btn btn-ghost btn-sm"
                              onClick={() => onViewPatient(p.patient_id)}
                            >
                              View
                            </button>
                            <button
                              className="btn btn-danger"
                              onClick={() => {
                                if (window.confirm(`Delete patient ${p.first_name} ${p.last_name}? This action is irreversible.`)) {
                                  onDeletePatient(p.patient_id);
                                }
                              }}
                            >
                              Delete
                            </button>
                          </div>
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
    </div>
  );
}
