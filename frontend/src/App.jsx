import React, { useState, useEffect } from 'react';
import { patientsApi } from './api/patientsApi';
import { callsApi } from './api/callsApi';
import PatientsPage from './pages/PatientsPage';
import PatientDetailPage from './pages/PatientDetailPage';
import DashboardPage from './pages/DashboardPage';
import VoiceCallsPage from './pages/VoiceCallsPage';
import VoiceCallDetailPage from './pages/VoiceCallDetailPage';

// Simple in-app router using state — no new dependencies
export default function App() {
  // ── Router state ──
  // page: 'dashboard' | 'patients' | 'patient-detail'
  const [page, setPage] = useState('dashboard');
  const [selectedCallId, setSelectedCallId] = useState(null);
  const [selectedPatientId, setSelectedPatientId] = useState(null);

  // ── Shared data state ──
  const [patients, setPatients] = useState([]);
  const [loadingPatients, setLoadingPatients] = useState(false);
  const [patientsError, setPatientsError] = useState('');
  const [totalCalls, setTotalCalls] = useState(null);

  const fetchPatients = async (filters = {}) => {
    setLoadingPatients(true);
    setPatientsError('');
    try {
      const data = await patientsApi.getPatients(filters);
      setPatients(data || []);
    } catch (err) {
      setPatientsError(err.message || 'Failed to fetch patients.');
    } finally {
      setLoadingPatients(false);
    }
  };

  useEffect(() => {
    fetchPatients();
    // fetch call count
    (async () => {
      try {
        const calls = await callsApi.getCalls();
        setTotalCalls(Array.isArray(calls) ? calls.length : 0);
      } catch (e) {
        setTotalCalls(0);
      }
    })();
  }, []);

  // ── Navigation ──
  const navigate = (target, id = null) => {
    setPage(target);
    // id may be patient id or call id based on target
    if (target === 'patient-detail' && id) setSelectedPatientId(id);
    if ((target === 'call-detail' || target === 'voicecalls') && id) setSelectedCallId(id);
    window.scrollTo(0, 0);
  };

  // ── Handlers ──
  const handleViewPatient = (id) => {
    setSelectedPatientId(id);
    setPage('patient-detail');
    window.scrollTo(0, 0);
  };

  const handleViewCall = (id) => {
    setSelectedCallId(id);
    setPage('call-detail');
    window.scrollTo(0, 0);
  };

  const handleDeletePatient = async (id) => {
    try {
      await patientsApi.deletePatient(id);
      // If we deleted the viewed patient, go back to list
      if (selectedPatientId === id) {
        setPage('patients');
        setSelectedPatientId(null);
      }
      fetchPatients();
    } catch (err) {
      alert(`Failed to delete patient: ${err.message}`);
    }
  };

  // ── Active nav helper ──
  const navActive = (target) => {
    if (target === 'patients' && page === 'patient-detail') return true;
    return page === target;
  };

  // ── Page titles ──
  const pageTitles = {
    dashboard: { title: 'Dashboard Overview', subtitle: 'Welcome back — your clinic at a glance' },
    patients: { title: 'Patient Registry', subtitle: 'Search, filter, and manage registered patients' },
    'patient-detail': { title: 'Patient Chart', subtitle: 'Complete demographic, insurance & voice call history' },
    voicecalls: { title: 'Voice Calls', subtitle: 'Browse recorded voice-call transcripts' },
    'call-detail': { title: 'Call Details', subtitle: 'Transcript and metadata for a single call' },
  };

  const { title, subtitle } = pageTitles[page] || pageTitles.dashboard;

  return (
    <div className="app-shell">
      {/* ── Sidebar ── */}
      <aside className="sidebar">
        {/* Brand */}
        <div className="sidebar-brand">
          <div className="brand-icon">⚕️</div>
          <div className="brand-text">
            <h1>Care Cloud AI</h1>
            <span>Patient Intake System</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav">
          <span className="nav-section-label">Main</span>

          <button
            className={`nav-item ${page === 'dashboard' ? 'active' : ''}`}
            onClick={() => navigate('dashboard')}
          >
            <span className="nav-icon">📊</span>
            Dashboard
          </button>

          <button
            className={`nav-item ${navActive('patients') ? 'active' : ''}`}
            onClick={() => navigate('patients')}
          >
            <span className="nav-icon">👥</span>
            Patient Registry
          </button>

          <span className="nav-section-label">System</span>

          <button className={`nav-item ${page === 'voicecalls' ? 'active' : ''}`} onClick={() => navigate('voicecalls')}>
            <span className="nav-icon">🎙️</span>
            Voice Calls
          </button>
        </nav>

        {/* Footer status */}
        <div className="sidebar-footer">
          <div className="status-indicator">
            <span className="status-dot"></span>
            <div className="status-text">
              Vapi Voice Agent
              <span>Online & Ready</span>
            </div>
          </div>
        </div>
      </aside>

      {/* ── Main Content ── */}
      <div className="main-content">
        {/* Top Bar */}
        <header className="topbar">
          <div className="topbar-left">
            <span className="topbar-title">{title}</span>
            <span className="topbar-subtitle">{subtitle}</span>
          </div>
          <div className="topbar-right">
            {loadingPatients && <div className="topbar-loader"></div>}
            <div className="topbar-badge">{new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}</div>
            <div className="topbar-badge live">● Live</div>
          </div>
        </header>

        {/* Page Renderer */}
        <main className="page-body">
          {page === 'dashboard' && (
            <DashboardPage
              patients={patients}
              totalCalls={totalCalls}
              onGoToPatients={() => navigate('patients')}
              onViewPatient={handleViewPatient}
            />
          )}

          {page === 'patients' && (
            <PatientsPage
              patients={patients}
              loading={loadingPatients}
              error={patientsError}
              onSearch={fetchPatients}
              onViewPatient={handleViewPatient}
              onDeletePatient={handleDeletePatient}
              selectedPatientId={selectedPatientId}
            />
          )}

          {page === 'patient-detail' && selectedPatientId && (
            <PatientDetailPage
              patientId={selectedPatientId}
              onBack={() => navigate('patients')}
              onDelete={handleDeletePatient}
            />
          )}

          {page === 'voicecalls' && (
            <VoiceCallsPage onViewCall={(id) => handleViewCall(id)} />
          )}

          {page === 'call-detail' && selectedCallId && (
            <VoiceCallDetailPage callId={selectedCallId} onBack={() => navigate('voicecalls')} />
          )}
        </main>
      </div>
    </div>
  );
}
