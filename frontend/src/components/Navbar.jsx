import React from 'react';
import { 
  Sparkles, 
  MessageSquare, 
  CheckCircle2, 
  BarChart3, 
  BookOpen, 
  Settings as SettingsIcon, 
  Database, 
  Cpu 
} from 'lucide-react';

export default function Navbar({ 
  activeTab, 
  setActiveTab, 
  backendOnline, 
  studentId, 
  groqModel,
  onOpenSettings 
}) {
  const tabs = [
    { id: 'chat', label: 'Chat & Learn', icon: MessageSquare },
    { id: 'quiz', label: 'Adaptive Quiz', icon: CheckCircle2 },
    { id: 'progress', label: 'My Progress', icon: BarChart3 },
    { id: 'notes', label: 'Knowledge Base', icon: BookOpen },
  ];

  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '1.25rem 0',
      marginBottom: '1.5rem',
      borderBottom: '1px solid var(--glass-border)',
      flexWrap: 'wrap',
      gap: '1rem'
    }}>
      {/* Brand Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
        <div style={{
          width: '42px',
          height: '42px',
          borderRadius: '12px',
          background: 'var(--gradient-primary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 15px rgba(99, 102, 241, 0.4)'
        }}>
          <Sparkles size={24} color="#fff" />
        </div>
        <div>
          <h1 style={{ fontSize: '1.35rem', lineHeight: '1.2' }}>Agentic AI Tutor</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.2rem' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.75rem', color: backendOnline ? 'var(--accent-emerald)' : 'var(--accent-amber)' }}>
              <span className="pulse-dot" style={{ backgroundColor: backendOnline ? 'var(--accent-emerald)' : 'var(--accent-amber)' }} />
              {backendOnline ? 'FastAPI + Postgres Active' : 'Connecting to API...'}
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>•</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.75rem', color: 'var(--accent-cyan)' }}>
              <Cpu size={12} /> {groqModel}
            </span>
          </div>
        </div>
      </div>

      {/* Navigation Pills */}
      <nav style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.4rem',
        background: 'rgba(15, 20, 34, 0.6)',
        padding: '0.35rem',
        borderRadius: 'var(--radius-full)',
        border: '1px solid var(--glass-border)'
      }}>
        {tabs.map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              className={`nav-tab-btn ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <Icon size={16} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </nav>

      {/* User / Settings Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.45rem 0.9rem',
          background: 'rgba(255, 255, 255, 0.04)',
          borderRadius: 'var(--radius-full)',
          border: '1px solid var(--glass-border)',
          fontSize: '0.85rem'
        }}>
          <Database size={14} color="var(--accent-indigo)" />
          <span style={{ color: 'var(--text-secondary)' }}>ID:</span>
          <strong style={{ color: 'var(--text-primary)' }}>{studentId}</strong>
        </div>

        <button 
          className="btn-secondary" 
          onClick={onOpenSettings}
          style={{ padding: '0.5rem 0.75rem' }}
          title="API & Model Settings"
        >
          <SettingsIcon size={18} />
        </button>
      </div>
    </header>
  );
}
