import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, BookOpen, CheckCircle, HelpCircle, ArrowRight, Loader2 } from 'lucide-react';
import { sendChatMessage } from '../services/api';

export default function ChatView({ studentId, groqApiKey, groqModel }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I am your AI Tutor. Ask me any concept from math, physics, or chemistry, or ask for practice questions!',
      practice_quiz: null,
      plan_executed: null
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [userPracticeAnswers, setUserPracticeAnswers] = useState({});
  const messagesEndRef = useRef(null);

  const quickPrompts = [
    "Explain Bayes' Theorem with an intuitive example",
    "How does Newton's 3rd law apply to rockets?",
    "Explain the Chain Rule in Calculus with a formula",
    "What is the difference between SN1 and SN2 reactions?"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (queryToSend) => {
    const text = queryToSend || inputQuery;
    if (!text.trim() || loading) return;

    const userMessage = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setInputQuery('');
    setLoading(true);

    try {
      const res = await sendChatMessage(studentId, text, groqApiKey, groqModel);
      
      const assistantMessage = {
        role: 'assistant',
        action: res.action,
        content: res.explanation || res.response || res.message || 'I have analyzed your request.',
        practice_quiz: res.practice_quiz || null,
        plan_executed: res.plan_executed || null
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: `⚠️ Error: ${err.message}. Please verify your Groq API key in Settings.`,
          isError: true
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handlePracticeChoice = (qId, optionLetter) => {
    setUserPracticeAnswers(prev => ({
      ...prev,
      [qId]: optionLetter
    }));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 160px)', gap: '1rem' }}>
      
      {/* Chat Messages Stream */}
      <div className="glass-panel" style={{
        flex: 1,
        overflowY: 'auto',
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.25rem'
      }}>
        {messages.map((msg, idx) => {
          const isUser = msg.role === 'user';
          return (
            <div
              key={idx}
              className="animate-fade-in"
              style={{
                display: 'flex',
                justifyContent: isUser ? 'flex-end' : 'flex-start',
                width: '100%'
              }}
            >
              <div style={{
                maxWidth: '82%',
                background: isUser 
                  ? 'var(--gradient-primary)' 
                  : 'rgba(255, 255, 255, 0.04)',
                border: isUser ? 'none' : '1px solid var(--glass-border)',
                borderRadius: '16px',
                borderBottomRightRadius: isUser ? '4px' : '16px',
                borderBottomLeftRadius: isUser ? '16px' : '4px',
                padding: '1.15rem 1.4rem',
                color: '#fff',
                boxShadow: isUser ? '0 4px 15px rgba(99, 102, 241, 0.25)' : 'none'
              }}>
                {/* Agent Plan Breadcrumb */}
                {!isUser && msg.plan_executed && msg.plan_executed.length > 0 && (
                  <div style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    alignItems: 'center',
                    gap: '0.4rem',
                    marginBottom: '0.85rem',
                    padding: '0.4rem 0.75rem',
                    background: 'rgba(99, 102, 241, 0.1)',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid rgba(99, 102, 241, 0.2)',
                    fontSize: '0.78rem',
                    color: 'var(--accent-cyan)'
                  }}>
                    <Sparkles size={13} />
                    <strong>Agent Workflow:</strong>
                    {msg.plan_executed.map((step, sIdx) => (
                      <span key={sIdx} style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                        {step} {sIdx < msg.plan_executed.length - 1 && <ArrowRight size={10} color="var(--text-muted)" />}
                      </span>
                    ))}
                  </div>
                )}

                {/* Main Text Content */}
                <div style={{ lineHeight: '1.65', fontSize: '0.98rem', whiteSpace: 'pre-wrap' }}>
                  {msg.content}
                </div>

                {/* Inline Practice Questions */}
                {!isUser && msg.practice_quiz && msg.practice_quiz.length > 0 && (
                  <div style={{ marginTop: '1.25rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)', paddingTop: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                      <HelpCircle size={16} color="var(--accent-amber)" />
                      <strong style={{ fontSize: '0.9rem', color: 'var(--accent-amber)' }}>
                        Quick Concept Check
                      </strong>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                      {msg.practice_quiz.map((q) => {
                        const selected = userPracticeAnswers[q.id];
                        const isAnswered = Boolean(selected);
                        const isCorrect = selected === q.correct_answer;

                        return (
                          <div 
                            key={q.id}
                            style={{
                              background: 'rgba(15, 20, 34, 0.7)',
                              border: '1px solid rgba(255, 255, 255, 0.08)',
                              borderRadius: '12px',
                              padding: '1rem'
                            }}
                          >
                            <p style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '0.6rem' }}>
                              Q{q.id}: {q.question}
                            </p>

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                              {q.options.map((opt, oIdx) => {
                                const optLetter = opt.split(')')[0].trim();
                                const isSelected = selected === optLetter;
                                let btnBg = 'rgba(255, 255, 255, 0.04)';
                                let btnBorder = 'rgba(255, 255, 255, 0.1)';

                                if (isAnswered) {
                                  if (optLetter === q.correct_answer) {
                                    btnBg = 'rgba(16, 185, 129, 0.2)';
                                    btnBorder = 'rgba(16, 185, 129, 0.5)';
                                  } else if (isSelected && !isCorrect) {
                                    btnBg = 'rgba(244, 63, 94, 0.2)';
                                    btnBorder = 'rgba(244, 63, 94, 0.5)';
                                  }
                                }

                                return (
                                  <button
                                    key={oIdx}
                                    disabled={isAnswered}
                                    onClick={() => handlePracticeChoice(q.id, optLetter)}
                                    style={{
                                      padding: '0.5rem 0.75rem',
                                      background: btnBg,
                                      border: `1px solid ${btnBorder}`,
                                      borderRadius: '8px',
                                      color: '#fff',
                                      fontSize: '0.85rem',
                                      textAlign: 'left',
                                      cursor: isAnswered ? 'default' : 'pointer',
                                      transition: 'all 0.15s ease'
                                    }}
                                  >
                                    {opt}
                                  </button>
                                );
                              })}
                            </div>

                            {/* Explanation Dropdown on Answer */}
                            {isAnswered && (
                              <div style={{
                                marginTop: '0.65rem',
                                padding: '0.6rem 0.8rem',
                                background: isCorrect ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)',
                                borderRadius: '8px',
                                fontSize: '0.82rem',
                                color: isCorrect ? '#34d399' : '#fb7185'
                              }}>
                                <strong>{isCorrect ? '✅ Correct!' : `❌ Incorrect (Correct: ${q.correct_answer})`}</strong> — {q.explanation}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {loading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', color: 'var(--text-muted)', fontSize: '0.9rem', padding: '0.5rem 1rem' }}>
            <Loader2 className="animate-spin" size={16} color="var(--accent-indigo)" />
            Thinking and querying study notes...
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggestion Chips */}
      {messages.length <= 2 && (
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {quickPrompts.map((prompt, pIdx) => (
            <button
              key={pIdx}
              onClick={() => handleSend(prompt)}
              className="btn-secondary"
              style={{ fontSize: '0.8rem', padding: '0.45rem 0.85rem', borderRadius: 'var(--radius-full)' }}
            >
              <Sparkles size={12} color="var(--accent-cyan)" /> {prompt}
            </button>
          ))}
        </div>
      )}

      {/* Input Field */}
      <form 
        onSubmit={(e) => { e.preventDefault(); handleSend(); }}
        style={{ display: 'flex', gap: '0.75rem' }}
      >
        <input
          type="text"
          className="input-field"
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          placeholder="Ask your tutor anything (e.g., 'Explain Doppler Effect with formulas')..."
          disabled={loading}
        />
        <button 
          type="submit" 
          className="btn-primary"
          disabled={loading || !inputQuery.trim()}
          style={{ minWidth: '110px' }}
        >
          {loading ? <Loader2 className="animate-spin" size={18} /> : <><Send size={16} /> Ask</>}
        </button>
      </form>

    </div>
  );
}
