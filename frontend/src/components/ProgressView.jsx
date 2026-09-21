import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Target, 
  AlertTriangle, 
  CheckCircle2, 
  Lightbulb, 
  RotateCcw,
  Loader2,
  Database
} from 'lucide-react';
import { fetchProgress } from '../services/api';

export default function ProgressView({ studentId }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadProgress = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchProgress(studentId);
      setReport(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProgress();
  }, [studentId]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px', gap: '0.75rem', color: 'var(--text-muted)' }}>
        <Loader2 className="animate-spin" size={24} color="var(--accent-indigo)" />
        Fetching student mastery records from PostgreSQL...
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center', maxWidth: '600px', margin: '0 auto' }}>
        <AlertTriangle size={36} color="var(--accent-amber)" style={{ margin: '0 auto 1rem' }} />
        <h3 style={{ marginBottom: '0.5rem' }}>Could Not Load Progress</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>{error}</p>
        <button className="btn-secondary" onClick={loadProgress}>
          <RotateCcw size={16} /> Retry
        </button>
      </div>
    );
  }

  const topicsList = Object.values(report?.progress || {});

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Overview Stat Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <div style={{ padding: '0.85rem', borderRadius: '12px', background: 'rgba(99, 102, 241, 0.15)' }}>
            <TrendingUp size={28} color="var(--accent-indigo)" />
          </div>
          <div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Topics Practiced
            </div>
            <div style={{ fontSize: '1.75rem', fontWeight: 800, marginTop: '0.2rem' }}>
              {report?.topics_practiced || 0}
            </div>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <div style={{ padding: '0.85rem', borderRadius: '12px', background: 'rgba(6, 182, 212, 0.15)' }}>
            <CheckCircle2 size={28} color="var(--accent-cyan)" />
          </div>
          <div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Total Quizzes Logged
            </div>
            <div style={{ fontSize: '1.75rem', fontWeight: 800, marginTop: '0.2rem' }}>
              {report?.total_quizzes || 0}
            </div>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <div style={{ padding: '0.85rem', borderRadius: '12px', background: 'rgba(244, 63, 94, 0.15)' }}>
            <Target size={28} color="var(--accent-rose)" />
          </div>
          <div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Topics Needing Focus
            </div>
            <div style={{ fontSize: '1.75rem', fontWeight: 800, marginTop: '0.2rem', color: (report?.weak_topics?.length || 0) > 0 ? 'var(--accent-rose)' : 'inherit' }}>
              {report?.weak_topics?.length || 0}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '1.5rem' }}>
        
        {/* Topic Mastery Breakdown */}
        <div className="glass-panel" style={{ padding: '1.75rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '1.15rem' }}>Topic Mastery Breakdown</h3>
            <button className="btn-secondary" onClick={loadProgress} style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}>
              <RotateCcw size={13} /> Refresh
            </button>
          </div>

          {topicsList.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
              <Database size={36} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
              <p>No topic scores recorded in PostgreSQL yet.</p>
              <p style={{ fontSize: '0.85rem', marginTop: '0.4rem' }}>Take an adaptive quiz to start logging mastery data!</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {topicsList.map((t, idx) => {
                const badgeClass = t.strength === 'strong' ? 'badge-strong' : (t.strength === 'medium' ? 'badge-medium' : 'badge-weak');
                let barColor = 'var(--accent-emerald)';
                if (t.strength === 'medium') barColor = 'var(--accent-amber)';
                if (t.strength === 'weak') barColor = 'var(--accent-rose)';

                return (
                  <div 
                    key={idx}
                    style={{
                      background: 'rgba(255, 255, 255, 0.02)',
                      padding: '1.15rem 1.25rem',
                      borderRadius: '12px',
                      border: '1px solid var(--glass-border)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem' }}>
                      <div>
                        <strong style={{ fontSize: '0.98rem' }}>{t.topic}</strong>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginLeft: '0.6rem' }}>
                          ({t.attempts} {t.attempts === 1 ? 'attempt' : 'attempts'})
                        </span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <strong style={{ fontSize: '1rem' }}>{t.accuracy}%</strong>
                        <span className={`badge ${badgeClass}`}>
                          {t.strength}
                        </span>
                      </div>
                    </div>

                    <div style={{ height: '7px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '999px', overflow: 'hidden' }}>
                      <div style={{
                        height: '100%',
                        width: `${Math.min(t.accuracy, 100)}%`,
                        background: barColor,
                        borderRadius: '999px',
                        transition: 'width 0.4s ease'
                      }} />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Tutor Recommendations Card */}
        <div className="glass-panel" style={{ padding: '1.75rem', height: 'fit-content' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
            <Lightbulb size={20} color="var(--accent-amber)" />
            <h3 style={{ fontSize: '1.15rem' }}>AI Recommendations</h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {report?.recommendations && report.recommendations.length > 0 ? (
              report.recommendations.map((rec, rIdx) => (
                <div 
                  key={rIdx}
                  style={{
                    padding: '0.9rem 1rem',
                    background: 'rgba(99, 102, 241, 0.08)',
                    border: '1px solid rgba(99, 102, 241, 0.2)',
                    borderRadius: '10px',
                    fontSize: '0.88rem',
                    lineHeight: '1.5',
                    color: 'var(--text-primary)'
                  }}
                >
                  {rec}
                </div>
              ))
            ) : (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
                Complete more quizzes to receive personalized AI recommendations.
              </p>
            )}
          </div>
        </div>

      </div>

    </div>
  );
}
