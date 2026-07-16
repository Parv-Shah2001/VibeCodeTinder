import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuthStore } from './store/auth'
import TopBar from './components/TopBar'
import BottomNav from './components/BottomNav'
import ErrorBoundary from './components/ErrorBoundary'
import Login from './pages/Login'
import Feed from './pages/Feed'
import Matches from './pages/Matches'
import Chat from './pages/Chat'
import Profile from './pages/Profile'
import Settings from './pages/Settings'
import Onboarding from './pages/Onboarding'
import Verification from './pages/Verification'
import SubscriptionPage from './pages/SubscriptionPage'
import LikesYou from './pages/LikesYou'
import Explore from './pages/Explore'
import Safety from './pages/Safety'
import NotFound from './pages/NotFound'

function Protected({ children }: { children: React.ReactNode }) {
  const isAuth = useAuthStore(s => s.isAuthenticated)
  if (!isAuth) return <Navigate to="/login" replace />
  return <>{children}</>
}

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-100 pb-16 md:pb-0">
      <TopBar />
      <div className="flex justify-center">
        <div className="w-full max-w-md bg-white min-h-[calc(100vh-56px)] shadow-sm">
          {children}
        </div>
      </div>
      <BottomNav />
    </div>
  )
}

export default function App() {
  const init = useAuthStore(s => s.init)
  useEffect(() => { init() }, [])

  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/onboarding" element={<Protected><Onboarding /></Protected>} />
          <Route path="/" element={<Protected><Layout><Feed /></Layout></Protected>} />
          <Route path="/matches" element={<Protected><Layout><Matches /></Layout></Protected>} />
          <Route path="/chat/:id" element={<Protected><Layout><Chat /></Layout></Protected>} />
          <Route path="/profile" element={<Protected><Layout><Profile /></Layout></Protected>} />
          <Route path="/settings" element={<Protected><Layout><Settings /></Layout></Protected>} />
          <Route path="/verification" element={<Protected><Layout><Verification /></Layout></Protected>} />
          <Route path="/subscription" element={<Protected><Layout><SubscriptionPage /></Layout></Protected>} />
          <Route path="/likes-you" element={<Protected><Layout><LikesYou /></Layout></Protected>} />
          <Route path="/explore" element={<Protected><Layout><Explore /></Layout></Protected>} />
          <Route path="/safety" element={<Protected><Layout><Safety /></Layout></Protected>} />
          <Route path="*" element={<Layout><NotFound /></Layout>} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  )
}
