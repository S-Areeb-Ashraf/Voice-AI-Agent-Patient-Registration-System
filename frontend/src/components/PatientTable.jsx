import React from 'react';

export default function PatientTable({ patients, onSelectPatient, onDeletePatient, selectedPatientId }) {
  
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
      // Adding UTC offsets / using date values correctly
      const parts = dateStr.split('-');
      if (parts.length === 3) {
        // Formats YYYY-MM-DD local dates nicely
        const [year, month, day] = parts;
        const dateObj = new Date(year, month - 1, day);
        return dateObj.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
      }
      return new Date(dateStr).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  if (!patients || patients.length === 0) {
    return (
      <div className="empty-state-card">
        <div className="empty-icon">📂</div>
        <h3>No Patient Records</h3>
        <p>No active patient records match your search criteria. Register a patient via the Vapi Voice Agent or use the creation options.</p>
      </div>
    );
  }

  return (
    <div className="table-wrapper">
      <table className="patient-table">
        <thead>
          <tr>
            <th>Patient Name</th>
            <th>DOB</th>
            <th>Sex</th>
            <th>Phone</th>
            <th>Language</th>
            <th>State / City</th>
            <th className="text-center">Actions</th>
          </tr>
        </thead>
        <tbody>
          {patients.map((patient) => {
            const isSelected = selectedPatientId === patient.patient_id;
            return (
              <tr 
                key={patient.patient_id} 
                onClick={() => onSelectPatient(patient.patient_id)}
                className={`patient-row-item ${isSelected ? 'row-active' : ''}`}
              >
                <td>
                  <span className="patient-name-cell">
                    {patient.last_name}, {patient.first_name}
                  </span>
                </td>
                <td>{formatDate(patient.date_of_birth)}</td>
                <td>
                  <span className={`gender-badge gender-${patient.sex.toLowerCase().replace(/\s+/g, '-')}`}>
                    {patient.sex}
                  </span>
                </td>
                <td>{formatPhone(patient.phone_number)}</td>
                <td>{patient.preferred_language}</td>
                <td>{patient.city}, {patient.state}</td>
                <td className="actions-cell-item" onClick={(e) => e.stopPropagation()}>
                  <button 
                    onClick={() => {
                      if (window.confirm(`Are you sure you want to delete patient ${patient.first_name} ${patient.last_name}?`)) {
                        onDeletePatient(patient.patient_id);
                      }
                    }} 
                    className="btn btn-delete-item"
                    aria-label={`Delete ${patient.first_name}`}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
