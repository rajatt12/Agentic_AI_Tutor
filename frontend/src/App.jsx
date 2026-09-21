import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ChatView from './components/ChatView';
import QuizView from './components/QuizView';
import ProgressView from './components/ProgressView';
import StudyMaterialView from './components/StudyMaterialView';
import SettingsModal from './components/SettingsModal';
import { checkBackendHealth } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [backendOnline, setBackendOnline] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // App Configuration
  const [studentId, setStudentId] = useState('student_001');
  const [groqApiKey, setGroqApiKey] = useState('');
  const [groqModel, setGroqModel] = useState('llama-3.3-70b-versatile');

  const verifyBackend = async () => {
    const isHealthy = await checkBackendHealth();
    setBackendOnline(isHealthy);
  };

  useEffect(() => {
    verifyBackend();
    const interval = setInterval(verifyBackend, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        backendOnline={backendOnline}
        studentId={studentId}
        groqModel={groqModel}
        onOpenSettings={() => setIsSettingsOpen(true)}
      />

      {/* Main View Router */}
      <main style={{ flex: 1 }}>
        {activeTab === 'chat' && (
          <ChatView
            studentId={studentId}
            groqApiKey={groqApiKey}
            groqModel={groqModel}
          />
        )}

        {activeTab === 'quiz' && (
          <QuizView
            studentId={studentId}
            groqApiKey={groqApiKey}
            groqModel={groqModel}
            onQuizCompleted={() => {
              // Optionally switch to progress or notify
            }}
          />
        )}

        {activeTab === 'progress' && (
          <ProgressView
            studentId={studentId}
          />
        )}

        {activeTab === 'notes' && (
          <StudyMaterialView />
        )}
      </main>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        groqApiKey={groqApiKey}
        setGroqApiKey={setGroqApiKey}
        groqModel={groqModel}
        setGroqModel={setGroqModel}
        studentId={studentId}
        setStudentId={setStudentId}
      />
    </div>
  );
}
