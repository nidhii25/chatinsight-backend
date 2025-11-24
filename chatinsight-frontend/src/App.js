
  // ===========================
  // File: src/App.js
  // ===========================

  import React, { useState } from 'react';
  import { AuthProvider, useAuth } from './context/AuthContext';
  import LoginPage from './pages/LoginPage';
  import RegisterPage from './pages/RegisterPage';
  import DashboardPage from './pages/DashboardPage';
  import AnalyticsPage from './pages/AnalyticsPage';
  import Navbar from './components/Navbar';
  import ReportsPage from './pages/ReportsPage';
  console.log('page start')

  const AuthWrapper = ({ authPage, setAuthPage, currentPage, selectedChatId, onNavigate }) => {
    const { user } = useAuth();
    console.log(user)

    if (!user) {
      console.log("AUTHENTICATION ISSUES")
      return authPage === 'login'
        ? <LoginPage onSwitchToRegister={() => setAuthPage('register')} />
        : <RegisterPage onSwitchToLogin={() => setAuthPage('login')} />;
    }

    if (currentPage === 'analytics' && selectedChatId) {
    return (
      <>
        <Navbar onNavigate={onNavigate} />
        <AnalyticsPage chatId={selectedChatId} onNavigate={onNavigate} />
      </>
    );
  }

    if (currentPage === "reports") {
    return (
      <>
        <Navbar onNavigate={onNavigate} />
        <ReportsPage />
      </>
    );
  }



    return <DashboardPage onNavigate={onNavigate} />;
  };

  const App = () => {
    const [authPage, setAuthPage] = useState('login');
    const [currentPage, setCurrentPage] = useState('dashboard');
    const [selectedChatId, setSelectedChatId] = useState(null);

    const handleNavigate = (page, chatId = null) => {
      setCurrentPage(page);
      if (chatId) setSelectedChatId(chatId);
    };

    return (
      <AuthProvider>
        <AuthWrapper
          authPage={authPage}
          setAuthPage={setAuthPage}
          currentPage={currentPage}
          selectedChatId={selectedChatId}
          onNavigate={handleNavigate}
        />
      </AuthProvider>
    );
  };

  export default App;
