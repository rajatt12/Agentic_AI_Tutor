import React, { useState } from 'react';
import { X, Key, Cpu, User, Check } from 'lucide-react';

export default function SettingsModal({
  isOpen,
  onClose,
  groqApiKey,
  setGroqApiKey,
  groqModel,
  setGroqModel,
  studentId,
  setStudentId
}) {
  const [localKey, setLocalKey] = useState(groqApiKey);
  const [localModel, setLocalModel] = useState(groqModel);
  const [localStudentId, setLocalStudentId] = useState(studentId);
  const [saved, setSaved] = useState(false);

  if (!isOpen) return null;

  const models = [
    { id: 'llama-3.3-70b-versatile', label: 'Llama 3.3 70B (Recommended — High Quality & Fast)' },
    { id: 'llama-3.1-8b-instant', label: 'Llama 3.1 8B (Instant Latency)' },
    { id: 'mixtral-8x7b-32768', label: 'Mixtral 8x7B (Large Context)' },
    { id: 'gemma2-9b-it', label: 'Gemma 2 9B (Google Open Weights)' }
  ];

  const handleSave = () => {
    setGroqApiKey(localKey);
    setGroqModel(localModel);
    setStudentId(localStudentId);
    setSaved(true);
    setTimeout(() => {
      setSaved(false);
      onClose();
    }, 600);
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '1rem'
    }}>
      <div className="glass-panel animate-fade-in" style={{
        width: '100%',
        maxWidth: '520px',
        padding: '2rem',
        background: 'var(--bg-secondary)',
        border: '1px solid rgba(255, 255, 255, 0.12)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.25rem' }}>Settings & Credentials</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Groq API Key */}
          <div>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>
              <Key size={14} /> Groq API Key
            </label>
            <input
              type="password"
              className="input-field"
              value={localKey}
              onChange={(e) => setLocalKey(e.target.value)}
              placeholder="gsk_..."
            />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem', display: 'block' }}>
              Leave blank to use the default key configured in the backend <code style={{ color: 'var(--accent-cyan)' }}>.env</code>.
            </span>
          </div>

          {/* Model Selector */}
          <div>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>
              <Cpu size={14} /> Active Groq Model
            </label>
            <select
              className="input-field"
              value={localModel}
              onChange={(e) => setLocalModel(e.target.value)}
              style={{ cursor: 'pointer' }}
            >
              {models.map(m => (
                <option key={m.id} value={m.id} style={{ background: '#0f1422' }}>
                  {m.label}
                </option>
              ))}
            </select>
          </div>

          {/* Student Profile ID */}
          <div>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>
              <User size={14} /> Student ID (PostgreSQL Profile)
            </label>
            <input
              type="text"
              className="input-field"
              value={localStudentId}
              onChange={(e) => setLocalStudentId(e.target.value)}
              placeholder="e.g. student_001"
            />
          </div>
        </div>

        <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
          <button className="btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn-primary" onClick={handleSave}>
            {saved ? <><Check size={16} /> Saved!</> : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
}
