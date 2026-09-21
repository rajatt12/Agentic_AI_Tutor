import React, { useState } from 'react';
import { BookOpen, UploadCloud, CheckCircle2, Sparkles, Loader2, FileText } from 'lucide-react';
import { ingestDocument } from '../services/api';

export default function StudyMaterialView() {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [resultMsg, setResultMsg] = useState(null);

  const sampleTemplates = [
    {
      title: "Physics: Projectile Motion & Kinematics",
      content: "A projectile launched at angle θ with initial velocity u has horizontal component u_x = u*cos(θ) and vertical component u_y = u*sin(θ).\n\nThe time of flight is T = (2*u*sin(θ))/g.\n\nThe maximum height reached is H = (u^2 * sin^2(θ))/(2*g).\n\nThe horizontal range is R = (u^2 * sin(2*θ))/g. Maximum range is achieved when launch angle θ = 45 degrees."
    },
    {
      title: "Mathematics: Probability & Bayes Theorem",
      content: "Bayes' Theorem describes the probability of an event based on prior knowledge of conditions that might be related to the event.\n\nFormula:\nP(A|B) = [P(B|A) * P(A)] / P(B)\n\nWhere:\n- P(A|B) is the posterior probability of A given B.\n- P(B|A) is the likelihood of B given A.\n- P(A) is the prior probability of A.\n- P(B) is the marginal probability of B."
    }
  ];

  const handleIngest = async (e) => {
    e?.preventDefault();
    if (!title.trim() || !content.trim()) return;

    setLoading(true);
    setResultMsg(null);

    try {
      const res = await ingestDocument(title, content);
      setResultMsg(res.message || 'Indexed successfully!');
      setTitle('');
      setContent('');
    } catch (err) {
      alert(`Ingestion error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const loadSample = (sample) => {
    setTitle(sample.title);
    setContent(sample.content);
  };

  return (
    <div className="animate-fade-in" style={{ maxWidth: '840px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      <div className="glass-panel" style={{ padding: '2.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
          <div style={{ padding: '0.5rem', borderRadius: '10px', background: 'rgba(6, 182, 212, 0.15)' }}>
            <UploadCloud size={22} color="var(--accent-cyan)" />
          </div>
          <h2 style={{ fontSize: '1.4rem' }}>Knowledge Base Ingestion (Hybrid RAG)</h2>
        </div>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '1.75rem', fontSize: '0.92rem', lineHeight: '1.5' }}>
          Add textbook excerpts, lecture notes, or formula cheat sheets. They will be automatically vectorized and indexed into <strong>ChromaDB (HNSW Dense)</strong> and <strong>BM25 (Sparse)</strong> for instant AI grounded retrieval.
        </p>

        {/* Quick Sample Presets */}
        <div style={{ marginBottom: '1.5rem' }}>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
            Try a Quick Preset:
          </span>
          <div style={{ display: 'flex', gap: '0.6rem', flexWrap: 'wrap' }}>
            {sampleTemplates.map((s, idx) => (
              <button
                key={idx}
                type="button"
                className="btn-secondary"
                onClick={() => loadSample(s)}
                style={{ fontSize: '0.82rem', padding: '0.4rem 0.8rem' }}
              >
                <FileText size={13} color="var(--accent-cyan)" /> {s.title.split(':')[0]}
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleIngest} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.88rem', fontWeight: 600, marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>
              Document / Concept Title
            </label>
            <input
              type="text"
              className="input-field"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Kinematics Formulas & Newton's Laws"
              required
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.88rem', fontWeight: 600, marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>
              Study Content / Notes / Formulas
            </label>
            <textarea
              className="input-field"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Paste notes, definitions, theorems, or textbook chapters here..."
              rows={8}
              style={{ resize: 'vertical', lineHeight: '1.5' }}
              required
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !title.trim() || !content.trim()}
            style={{ padding: '0.9rem' }}
          >
            {loading ? <Loader2 className="animate-spin" size={18} /> : <><Sparkles size={18} /> Index into ChromaDB & BM25</>}
          </button>
        </form>

        {resultMsg && (
          <div style={{
            marginTop: '1.5rem',
            padding: '1rem 1.25rem',
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            borderRadius: '12px',
            color: '#34d399',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            fontSize: '0.92rem'
          }}>
            <CheckCircle2 size={20} />
            {resultMsg}
          </div>
        )}
      </div>

    </div>
  );
}
