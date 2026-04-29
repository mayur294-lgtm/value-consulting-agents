import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import { LoadingState } from './components/common/DataState';

// Home page stays eagerly loaded (landing page, must be instant)
import HomePage from './pages/HomePage';

// All other pages are lazy-loaded — Vite creates separate chunks automatically
const MarketPage = lazy(() => import('./pages/MarketPage'));
const CountryPage = lazy(() => import('./pages/CountryPage'));
const BankPage = lazy(() => import('./pages/BankPage'));
const ComparePage = lazy(() => import('./pages/ComparePage'));
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'));
const FavoritesPage = lazy(() => import('./pages/FavoritesPage'));
const BriefFeedbackPage = lazy(() => import('./pages/BriefFeedbackPage'));
const AccountPlanPage = lazy(() => import('./pages/AccountPlanPage'));
const StrategicAccountPlanPage = lazy(() => import('./pages/StrategicAccountPlanPage'));
const PipelinePage = lazy(() => import('./pages/PipelinePage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));
const DesignSystemPage = lazy(() => import('./pages/DesignSystemPage'));
const PulsePage = lazy(() => import('./pages/PulsePage'));  // Strategic Repositioning Sprint 1
const ChangesPage = lazy(() => import('./pages/ChangesPage'));  // Strategic Repositioning Sprint 4 — diff-first portfolio view
const PortfolioQueryPage = lazy(() => import('./pages/PortfolioQueryPage'));  // Sprint 5 — composable portfolio queries
const TimelinePage = lazy(() => import('./pages/TimelinePage'));  // Engagement & Execution Timeline (per-bank)

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/market/:marketKey" element={<Suspense fallback={<LoadingState />}><MarketPage /></Suspense>} />
        <Route path="/country/:countryName" element={<Suspense fallback={<LoadingState />}><CountryPage /></Suspense>} />
        <Route path="/bank/:bankKey" element={<Suspense fallback={<LoadingState />}><BankPage /></Suspense>} />
        <Route path="/compare" element={<Suspense fallback={<LoadingState />}><ComparePage /></Suspense>} />
        <Route path="/analytics" element={<Suspense fallback={<LoadingState />}><AnalyticsPage /></Suspense>} />
        <Route path="/favorites" element={<Suspense fallback={<LoadingState />}><FavoritesPage /></Suspense>} />
        <Route path="/feedback" element={<Suspense fallback={<LoadingState />}><BriefFeedbackPage /></Suspense>} />
        <Route path="/account-plan/:bankKey" element={<Suspense fallback={<LoadingState />}><StrategicAccountPlanPage /></Suspense>} />
        <Route path="/account-plan-doc/:bankKey" element={<Suspense fallback={<LoadingState />}><AccountPlanPage /></Suspense>} />
        {/* Strategic Repositioning Sprint 1 — Quarterly Pulse review surface */}
        <Route path="/bank/:bankKey/pulse" element={<Suspense fallback={<LoadingState />}><PulsePage /></Suspense>} />
        <Route path="/bank/:bankKey/timeline" element={<Suspense fallback={<LoadingState />}><TimelinePage /></Suspense>} />
        {/* Sprint 4 — diff-first portfolio change feed */}
        <Route path="/changes" element={<Suspense fallback={<LoadingState />}><ChangesPage /></Suspense>} />
        {/* Sprint 5 — composable portfolio queries */}
        <Route path="/query" element={<Suspense fallback={<LoadingState />}><PortfolioQueryPage /></Suspense>} />
        <Route path="/pipeline" element={<Suspense fallback={<LoadingState />}><PipelinePage /></Suspense>} />
        <Route path="/settings" element={<Suspense fallback={<LoadingState />}><SettingsPage /></Suspense>} />
        <Route path="/design-system" element={<Suspense fallback={<LoadingState />}><DesignSystemPage /></Suspense>} />
      </Route>
    </Routes>
  );
}
