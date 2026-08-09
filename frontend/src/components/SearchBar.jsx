import React, { useState } from 'react';

export default function SearchBar({ onSearch }) {
  const [lastName, setLastName] = useState('');
  const [dob, setDob] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch({
      last_name: lastName,
      date_of_birth: dob,
      phone_number: phoneNumber,
    });
  };

  const handleClear = () => {
    setLastName('');
    setDob('');
    setPhoneNumber('');
    onSearch({ last_name: '', date_of_birth: '', phone_number: '' });
  };

  return (
    <form className="search-bar-form" onSubmit={handleSubmit}>
      <div className="search-grid">
        <div className="form-group">
          <label htmlFor="search-last-name">Last Name</label>
          <input
            id="search-last-name"
            type="text"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            placeholder="e.g. O'Connor"
            className="form-control"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="search-dob">Date of Birth</label>
          <input
            id="search-dob"
            type="date"
            value={dob}
            onChange={(e) => setDob(e.target.value)}
            className="form-control"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="search-phone">Phone Number</label>
          <input
            id="search-phone"
            type="text"
            value={phoneNumber}
            onChange={(e) => setPhoneNumber(e.target.value)}
            placeholder="e.g. 10-digit number"
            className="form-control"
          />
        </div>
      </div>
      
      <div className="search-buttons">
        <button type="submit" className="btn btn-search">
          Filter Patients
        </button>
        <button type="button" className="btn btn-clear" onClick={handleClear}>
          Reset
        </button>
      </div>
    </form>
  );
}
