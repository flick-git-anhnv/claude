import { Navigate, Route, Routes } from 'react-router-dom'
import AppHeader from './components/layout/AppHeader'
import SidebarNav from './components/layout/SidebarNav'
import ToastNotification from './components/common/ToastNotification'
import AgentStatusPage from './pages/AgentStatusPage'
import TokenAnalyticsPage from './pages/TokenAnalyticsPage'
import SessionHistoryPage from './pages/SessionHistoryPage'
import AccountManagerPage from './pages/AccountManagerPage'

export default function App() {
  return (
    <div className="flex flex-col h-screen overflow-hidden">
      {/* Fixed header */}
      <AppHeader />

      {/* Body: sidebar + main */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <SidebarNav />

        {/* Main content */}
        <main
          className="flex-1 overflow-y-auto bg-white p-6"
          id="main-content"
          tabIndex={-1}
        >
          <Routes>
            <Route path="/" element={<Navigate to="/agents" replace />} />
            <Route path="/agents"   element={<AgentStatusPage />} />
            <Route path="/tokens"   element={<TokenAnalyticsPage />} />
            <Route path="/sessions" element={<SessionHistoryPage />} />
            <Route path="/accounts" element={<AccountManagerPage />} />
            {/* Fallback */}
            <Route path="*" element={<Navigate to="/agents" replace />} />
          </Routes>
        </main>
      </div>

      {/* Global toast overlay */}
      <ToastNotification />
    </div>
  )
}
