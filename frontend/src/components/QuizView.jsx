import React, { useState } from 'react';
import { 
  CheckCircle2, 
  HelpCircle, 
  Sparkles, 
  Trophy, 
  RotateCcw, 
  ArrowRight, 
  ArrowLeft, 
  Loader2, 
  Flame, 
  Database 
} from 'lucide-react';
import confetti from 'canvas-confetti';
import { generateQuiz, submitQuiz } from '../services/api';

export default function QuizView({ studentId, groqApiKey, groqModel, onQuizCompleted }) {
  // Config state
  const [topic, setTopic] = useState('');
  const [numQuestions, setNumQuestions] = useState(3);
  const [difficulty, setDifficulty] = useState('');
  
  // Quiz taking state
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [quizData, setQuizData] = useState(null);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [submissionResult, setSubmissionResult] = useState(null);

  const handleGenerate = async (e) => {
    e?.preventDefault();
    if (!topic.trim()) return;

    setLoading(true);
    setQuizData(null);
    setSubmissionResult(null);
    setSelectedAnswers({});
    setCurrentIdx(0);

    try {
      const data = await generateQuiz(
        studentId,
        topic,
        numQuestions,
        difficulty || undefined,
        groqApiKey,
        groqModel
      );
      setQuizData(data);
    } catch (err) {
      alert(`Error generating quiz: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOption = (questionId, optionLetter) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionId]: optionLetter
    }));
  };

  const handleSubmit = async () => {
    if (!quizData) return;
    
    // Check if all answered
    const unanswered = quizData.questions.some(q => !selectedAnswers[q.id]);
    if (unanswered) {
      if (!confirm("You have unanswered questions. Are you sure you want to submit?")) {
        return;
      }
    }

    setSubmitting(true);
    try {
      const payloadQuestions = quizData.questions.map(q => ({
        id: q.id,
        question: q.question,
        options: q.options,
        user_answer: selectedAnswers[q.id] || '',
        correct_answer: q.correct_answer,
        explanation: q.explanation
      }));

      const res = await submitQuiz(
        studentId,
        quizData.topic,
        quizData.difficulty,
        payloadQuestions
      );

      setSubmissionResult(res);

      // Trigger Confetti celebration if score is high!
      if (res.accuracy >= 70) {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 }
        });
      }

      if (onQuizCompleted) {
        onQuizCompleted();
      }
    } catch (err) {
      alert(`Failed to submit quiz: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  // 1. Result Screen
  if (submissionResult) {
    const isSuccess = submissionResult.accuracy >= 70;
    return (
      <div className="animate-fade-in" style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div className="glass-panel" style={{
          textAlign: 'center',
          padding: '2.5rem',
          background: isSuccess 
            ? 'radial-gradient(circle at center, rgba(16, 185, 129, 0.15) 0%, rgba(18, 24, 38, 0.8) 70%)'
            : 'radial-gradient(circle at center, rgba(244, 63, 94, 0.12) 0%, rgba(18, 24, 38, 0.8) 70%)'
        }}>
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            background: isSuccess ? 'rgba(16, 185, 129, 0.2)' : 'rgba(244, 63, 94, 0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1.25rem'
          }}>
            <Trophy size={32} color={isSuccess ? 'var(--accent-emerald)' : 'var(--accent-rose)'} />
          </div>

          <h2 style={{ fontSize: '1.85rem', marginBottom: '0.5rem' }}>
            {isSuccess ? 'Outstanding Mastery!' : 'Keep Practicing!'}
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
            Topic: <strong>{submissionResult.topic}</strong> • Score: <strong>{submissionResult.score} / {submissionResult.total_questions}</strong> ({submissionResult.accuracy}%)
          </p>

          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.6rem',
            padding: '0.6rem 1.2rem',
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: 'var(--radius-full)',
            border: '1px solid var(--glass-border)',
            fontSize: '0.85rem',
            marginBottom: '1.5rem'
          }}>
            <Database size={14} color="var(--accent-indigo)" />
            <span>Updated Topic Mastery in PostgreSQL: <strong>{submissionResult.updated_topic_accuracy}%</strong></span>
            <span className={`badge badge-${submissionResult.updated_topic_strength}`}>
              {submissionResult.updated_topic_strength}
            </span>
          </div>

          <div>
            <button className="btn-primary" onClick={() => { setQuizData(null); setSubmissionResult(null); }}>
              <RotateCcw size={16} /> Take Another Quiz
            </button>
          </div>
        </div>

        {/* Detailed Question Review */}
        <h3 style={{ fontSize: '1.2rem' }}>Detailed Answer Review</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {submissionResult.results.map((r) => (
            <div 
              key={r.id}
              className="glass-panel"
              style={{
                padding: '1.25rem',
                borderLeft: `4px solid ${r.is_correct ? 'var(--accent-emerald)' : 'var(--accent-rose)'}`
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <strong style={{ fontSize: '0.95rem' }}>Question {r.id}: {r.question}</strong>
                <span className={`badge ${r.is_correct ? 'badge-strong' : 'badge-weak'}`}>
                  {r.is_correct ? 'Correct' : 'Incorrect'}
                </span>
              </div>

              <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginBottom: '0.6rem' }}>
                Your Answer: <strong style={{ color: r.is_correct ? '#34d399' : '#fb7185' }}>{r.user_answer || '(No answer)'}</strong>
                {!r.is_correct && <span> • Correct Answer: <strong style={{ color: '#34d399' }}>{r.correct_answer}</strong></span>}
              </div>

              <div style={{
                background: 'rgba(255, 255, 255, 0.03)',
                padding: '0.65rem 0.85rem',
                borderRadius: '8px',
                fontSize: '0.83rem',
                color: 'var(--text-primary)',
                lineHeight: '1.5'
              }}>
                <strong>Explanation:</strong> {r.explanation}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // 2. Active Quiz Taking Screen
  if (quizData && quizData.questions && quizData.questions.length > 0) {
    const currentQ = quizData.questions[currentIdx];
    const totalQ = quizData.questions.length;
    const progressPercent = ((currentIdx + 1) / totalQ) * 100;
    const currentSelected = selectedAnswers[currentQ.id];

    return (
      <div className="animate-fade-in" style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        
        {/* Progress Bar & Header */}
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <div>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Quiz on:</span>{' '}
              <strong>{quizData.topic}</strong>{' '}
              <span className="badge badge-medium" style={{ marginLeft: '0.5rem' }}>
                {quizData.difficulty}
              </span>
            </div>
            <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-cyan)' }}>
              Question {currentIdx + 1} of {totalQ}
            </div>
          </div>

          <div style={{ height: '6px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '999px', overflow: 'hidden' }}>
            <div style={{
              height: '100%',
              width: `${progressPercent}%`,
              background: 'var(--gradient-primary)',
              transition: 'width 0.3s ease'
            }} />
          </div>
        </div>

        {/* Question Card */}
        <div className="glass-panel" style={{ padding: '2rem' }}>
          <h3 style={{ fontSize: '1.15rem', lineHeight: '1.5', marginBottom: '1.5rem' }}>
            {currentQ.question}
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '2rem' }}>
            {currentQ.options.map((opt, oIdx) => {
              const optLetter = opt.split(')')[0].trim();
              const isSelected = currentSelected === optLetter;

              return (
                <div
                  key={oIdx}
                  onClick={() => handleSelectOption(currentQ.id, optLetter)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem',
                    padding: '1rem 1.25rem',
                    background: isSelected ? 'rgba(99, 102, 241, 0.15)' : 'rgba(255, 255, 255, 0.03)',
                    border: `1px solid ${isSelected ? 'var(--accent-indigo)' : 'var(--glass-border)'}`,
                    borderRadius: '12px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    boxShadow: isSelected ? '0 0 15px rgba(99, 102, 241, 0.2)' : 'none'
                  }}
                >
                  <div style={{
                    width: '24px',
                    height: '24px',
                    borderRadius: '50%',
                    border: `2px solid ${isSelected ? 'var(--accent-indigo)' : 'var(--text-muted)'}`,
                    background: isSelected ? 'var(--accent-indigo)' : 'transparent',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    color: '#fff'
                  }}>
                    {isSelected ? '✓' : optLetter}
                  </div>
                  <span style={{ fontSize: '0.95rem', color: isSelected ? '#fff' : 'var(--text-primary)' }}>
                    {opt}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Stepper Navigation */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <button
              className="btn-secondary"
              disabled={currentIdx === 0}
              onClick={() => setCurrentIdx(prev => prev - 1)}
            >
              <ArrowLeft size={16} /> Previous
            </button>

            {currentIdx < totalQ - 1 ? (
              <button
                className="btn-primary"
                onClick={() => setCurrentIdx(prev => prev + 1)}
              >
                Next Question <ArrowRight size={16} />
              </button>
            ) : (
              <button
                className="btn-primary"
                onClick={handleSubmit}
                disabled={submitting}
                style={{ background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)' }}
              >
                {submitting ? <Loader2 className="animate-spin" size={16} /> : <><CheckCircle2 size={16} /> Submit Quiz</>}
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // 3. Quiz Setup Screen
  return (
    <div className="animate-fade-in" style={{ maxWidth: '680px', margin: '0 auto' }}>
      <div className="glass-panel" style={{ padding: '2.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
          <div style={{ padding: '0.5rem', borderRadius: '10px', background: 'rgba(99, 102, 241, 0.15)' }}>
            <Sparkles size={22} color="var(--accent-indigo)" />
          </div>
          <h2 style={{ fontSize: '1.4rem' }}>Adaptive Quiz Generator</h2>
        </div>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', fontSize: '0.92rem' }}>
          Quizzes automatically scale in difficulty based on your historical mastery stored in PostgreSQL.
        </p>

        <form onSubmit={handleGenerate} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.88rem', fontWeight: 600, marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>
              Subject or Concept Topic
            </label>
            <input
              type="text"
              className="input-field"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. Probability, Newton's Laws of Motion, Thermodynamics"
              required
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.88rem', fontWeight: 600, marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>
                Number of Questions
              </label>
              <select
                className="input-field"
                value={numQuestions}
                onChange={(e) => setNumQuestions(Number(e.target.value))}
              >
                <option value={3}>3 Questions (Quick Check)</option>
                <option value={5}>5 Questions (Standard)</option>
                <option value={10}>10 Questions (Full Assessment)</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.88rem', fontWeight: 600, marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>
                Difficulty Level
              </label>
              <select
                className="input-field"
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
              >
                <option value="">⚡ Auto-Adaptive (PostgreSQL Driven)</option>
                <option value="easy">Easy (Fundamentals)</option>
                <option value="medium">Medium (Standard Applications)</option>
                <option value="hard">Hard (Competitive Exam Level)</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !topic.trim()}
            style={{ marginTop: '1rem', padding: '0.9rem' }}
          >
            {loading ? <Loader2 className="animate-spin" size={18} /> : <><Flame size={18} /> Generate Adaptive Quiz</>}
          </button>
        </form>
      </div>
    </div>
  );
}
