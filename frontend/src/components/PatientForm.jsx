import React, { useState, useEffect } from 'react';
import { patientsApi } from '../api/patientsApi';

function normalizeInitial(initial) {
  if (!initial) return null;
  const map = {
    first_name: initial.first_name ?? '',
    last_name: initial.last_name ?? '',
    // Ensure date in YYYY-MM-DD for <input type=date>
    date_of_birth: initial.date_of_birth ? (initial.date_of_birth.split && typeof initial.date_of_birth === 'string' ? initial.date_of_birth.split('T')[0] : String(initial.date_of_birth)) : '',
    sex: initial.sex ?? 'Male',
    phone_number: initial.phone_number ?? '',
    email: initial.email ?? '',
    address_line_1: initial.address_line_1 ?? '',
    address_line_2: initial.address_line_2 ?? '',
    city: initial.city ?? '',
    state: initial.state ?? '',
    zip_code: initial.zip_code ?? '',
    insurance_provider: initial.insurance_provider ?? '',
    insurance_member_id: initial.insurance_member_id ?? '',
    preferred_language: initial.preferred_language ?? 'English',
    emergency_contact_name: initial.emergency_contact_name ?? '',
    emergency_contact_phone: initial.emergency_contact_phone ?? ''
  };
  return map;
}

export default function PatientForm({ initial = null, onClose, onSaved }) {
  const empty = {
    first_name: '', last_name: '', date_of_birth: '', sex: 'Male', phone_number: '', email: '',
    address_line_1: '', address_line_2: '', city: '', state: '', zip_code: '',
    insurance_provider: '', insurance_member_id: '', preferred_language: 'English',
    emergency_contact_name: '', emergency_contact_phone: ''
  };

  const [form, setForm] = useState(empty);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!initial) {
      setForm(empty);
      return;
    }
    const mapped = normalizeInitial(initial);
    if (mapped) setForm((prev) => ({ ...prev, ...mapped }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initial]);

  const onChange = (k) => (e) => setForm((prev) => ({ ...prev, [k]: e.target.value ?? '' }));

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true); setError('');
    try {
      if (initial && initial.patient_id) {
        await patientsApi.updatePatient(initial.patient_id, form);
      } else {
        await patientsApi.createPatient(form);
      }
      onSaved && onSaved();
      onClose && onClose();
    } catch (err) {
      setError(err.message || 'Failed to save patient');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal">
      <form className="modal-card" onSubmit={submit} style={{ maxWidth: 900 }}>
        <div className="modal-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0 }}>{initial ? 'Edit Patient' : 'Create Patient'}</h3>
          <button type="button" className="btn btn-ghost" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {error && <div className="alert alert-error">{error}</div>}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            <div>
              <label>First Name</label>
              <input className="filter-input" value={form.first_name} onChange={onChange('first_name')} required />
            </div>
            <div>
              <label>Last Name</label>
              <input className="filter-input" value={form.last_name} onChange={onChange('last_name')} required />
            </div>

            <div>
              <label>Date of Birth</label>
              <input className="filter-input" type="date" value={form.date_of_birth} onChange={onChange('date_of_birth')} required />
            </div>
            <div>
              <label>Sex</label>
              <select className="filter-input" value={form.sex} onChange={onChange('sex')}>
                <option>Male</option>
                <option>Female</option>
                <option>Other</option>
              </select>
            </div>

            <div>
              <label>Phone</label>
              <input className="filter-input" value={form.phone_number} onChange={onChange('phone_number')} required />
            </div>
            <div>
              <label>Email</label>
              <input className="filter-input" value={form.email} onChange={onChange('email')} />
            </div>

            <div>
              <label>Address Line 1</label>
              <input className="filter-input" value={form.address_line_1} onChange={onChange('address_line_1')} required />
            </div>
            <div>
              <label>Address Line 2</label>
              <input className="filter-input" value={form.address_line_2} onChange={onChange('address_line_2')} />
            </div>

            <div>
              <label>City</label>
              <input className="filter-input" value={form.city} onChange={onChange('city')} required />
            </div>
            <div>
              <label>State</label>
              <input className="filter-input" value={form.state} onChange={onChange('state')} required />
            </div>

            <div>
              <label>ZIP</label>
              <input className="filter-input" value={form.zip_code} onChange={onChange('zip_code')} required />
            </div>
            <div>
              <label>Preferred Language</label>
              <input className="filter-input" value={form.preferred_language} onChange={onChange('preferred_language')} />
            </div>

            <div>
              <label>Insurance Provider</label>
              <input className="filter-input" value={form.insurance_provider} onChange={onChange('insurance_provider')} />
            </div>
            <div>
              <label>Insurance Member ID</label>
              <input className="filter-input" value={form.insurance_member_id} onChange={onChange('insurance_member_id')} />
            </div>

            <div>
              <label>Emergency Contact Name</label>
              <input className="filter-input" value={form.emergency_contact_name} onChange={onChange('emergency_contact_name')} />
            </div>
            <div>
              <label>Emergency Contact Phone</label>
              <input className="filter-input" value={form.emergency_contact_phone} onChange={onChange('emergency_contact_phone')} />
            </div>
          </div>
        </div>
        <div className="modal-footer" style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
          <button type="button" className="btn btn-ghost" onClick={onClose}>Cancel</button>
          <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Saving…' : 'Save'}</button>
        </div>
      </form>
    </div>
  );
}
