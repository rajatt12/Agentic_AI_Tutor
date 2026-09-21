const API_BASE = '/api/v1';

export async function checkBackendHealth() {
  try {
    const res = await fetch('/health');
    if (!res.ok) return false;
    const data = await res.json();
    return data.status === 'healthy';
  } catch (e) {
    return false;
  }
}

export async function sendChatMessage(studentId, query, apiKey, model) {
  const payload = {
    student_id: studentId,
    query: query,
    groq_api_key: apiKey || undefined,
    groq_model: model || undefined
  };

  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to send chat message');
  }

  return await res.json();
}

export async function generateQuiz(studentId, topic, numQuestions, difficulty, apiKey, model) {
  const payload = {
    student_id: studentId,
    topic: topic,
    num_questions: numQuestions,
    difficulty: difficulty || undefined,
    groq_api_key: apiKey || undefined,
    groq_model: model || undefined
  };

  const res = await fetch(`${API_BASE}/quiz/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to generate quiz');
  }

  return await res.json();
}

export async function submitQuiz(studentId, topic, difficulty, questions) {
  const payload = {
    student_id: studentId,
    topic: topic,
    difficulty: difficulty,
    questions: questions
  };

  const res = await fetch(`${API_BASE}/quiz/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to submit quiz');
  }

  return await res.json();
}

export async function fetchProgress(studentId) {
  const res = await fetch(`${API_BASE}/progress/${studentId}`);
  if (!res.ok) {
    throw new Error('Failed to fetch progress metrics');
  }
  return await res.json();
}

export async function ingestDocument(title, content) {
  const res = await fetch(`${API_BASE}/documents/ingest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, content, source_type: 'notes' })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to index study document');
  }

  return await res.json();
}
