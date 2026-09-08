import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import ActivityHistoryPage from './pages/ActivityHistoryPage'
import AIPracticePage from './pages/AIPracticePage'
import ConversationChatPage from './pages/ConversationChatPage'
import ConversationHistoryPage from './pages/ConversationHistoryPage'
import ConversationScenariosPage from './pages/ConversationScenariosPage'
import DashboardPage from './pages/DashboardPage'
import FlashcardsPage from './pages/FlashcardsPage'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import MiniStoriesPage from './pages/MiniStoriesPage'
import MistakesPage from './pages/MistakesPage'
import OnboardingPage from './pages/OnboardingPage'
import ProgressPage from './pages/ProgressPage'
import QuizPage from './pages/QuizPage'
import RegisterPage from './pages/RegisterPage'
import SpeakingHistoryPage from './pages/SpeakingHistoryPage'
import SpeakingPracticePage from './pages/SpeakingPracticePage'
import TestHistoryPage from './pages/TestHistoryPage'
import TestResultPage from './pages/TestResultPage'
import TestsPage from './pages/TestsPage'
import TestTakingPage from './pages/TestTakingPage'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/onboarding"
            element={
              <ProtectedRoute>
                <OnboardingPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/flashcards"
            element={
              <ProtectedRoute>
                <FlashcardsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/quiz"
            element={
              <ProtectedRoute>
                <QuizPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/tests"
            element={
              <ProtectedRoute>
                <TestsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/tests/history"
            element={
              <ProtectedRoute>
                <TestHistoryPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/tests/results/:attemptId"
            element={
              <ProtectedRoute>
                <TestResultPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/tests/:testId"
            element={
              <ProtectedRoute>
                <TestTakingPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/progress"
            element={
              <ProtectedRoute>
                <ProgressPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/mistakes"
            element={
              <ProtectedRoute>
                <MistakesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/activity-history"
            element={
              <ProtectedRoute>
                <ActivityHistoryPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/ai-practice"
            element={
              <ProtectedRoute>
                <AIPracticePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/mini-stories"
            element={
              <ProtectedRoute>
                <MiniStoriesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/conversation"
            element={
              <ProtectedRoute>
                <ConversationScenariosPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/conversation/history"
            element={
              <ProtectedRoute>
                <ConversationHistoryPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/conversation/:sessionId"
            element={
              <ProtectedRoute>
                <ConversationChatPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/speaking"
            element={
              <ProtectedRoute>
                <SpeakingPracticePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/speaking/history"
            element={
              <ProtectedRoute>
                <SpeakingHistoryPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
