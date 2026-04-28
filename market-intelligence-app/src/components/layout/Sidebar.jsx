import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Home, BarChart3, Search, Star, Heart, MessageSquare, ChevronLeft, ChevronRight, Moon, Sun, Settings, Zap, Filter } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import { useRecentBanks } from '../../hooks/useRecentBanks';
import { scoreColor } from '../../data/scoring';

const NAV_ITEMS = [
  { path: '/', icon: Home, label: 'Home' },
  { path: '/pipeline', icon: BarChart3, label: 'Pipeline' },
  // Sprint 4 — portfolio change feed (what changed across all banks)
  { path: '/changes', icon: Zap, label: 'Changes' },
  // Sprint 5 — composable portfolio queries (find banks matching filters)
  { path: '/query', icon: Filter, label: 'Query' },
];

const TOOL_ITEMS = [
  { path: '/analytics', icon: BarChart3, label: 'Analytics' },
  { path: '/favorites', icon: Heart, label: 'Favorites' },
  { path: '/feedback', icon: MessageSquare, label: 'Feedback' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export default function Sidebar({ onSearchOpen }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const { recent } = useRecentBanks();
  const [collapsed, setCollapsed] = useState(false);

  const isActive = (path) => location.pathname === path;

  const NavButton = ({ path, icon: Icon, label, onClick }) => {
    const active = isActive(path);
    return (
      <button
        onClick={onClick || (() => navigate(path))}
        className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-[12px] font-semibold transition-all
          ${active ? 'bg-primary/10 text-primary' : 'text-fg-muted hover:text-fg hover:bg-surface-2'}`}
      >
        <Icon size={16} className="shrink-0" />
        {!collapsed && <span className="truncate">{label}</span>}
      </button>
    );
  };

  return (
    <aside className={`h-screen sticky top-0 flex flex-col bg-surface border-r border-border transition-all duration-200 no-print
      ${collapsed ? 'w-[52px]' : 'w-[200px]'}`}>

      {/* Logo */}
      <div className="flex items-center gap-2 px-3 py-4 border-b border-border">
        <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center shrink-0">
          <Star size={14} className="text-white" />
        </div>
        {!collapsed && <span className="text-sm font-black text-fg">Nova</span>}
      </div>

      {/* Primary nav */}
      <div className="px-2 py-3 space-y-0.5">
        {NAV_ITEMS.map(item => <NavButton key={item.path} {...item} />)}
        <NavButton path="/search" icon={Search} label="Search" onClick={onSearchOpen} />
      </div>

      {/* Recent banks */}
      {!collapsed && recent.length > 0 && (
        <div className="px-2 py-2 border-t border-border">
          <div className="px-3 py-1 text-[9px] font-bold text-fg-disabled uppercase tracking-wider">Recent</div>
          <div className="space-y-0.5">
            {recent.slice(0, 4).map(bank => (
              <button key={bank.key}
                onClick={() => navigate(`/bank/${encodeURIComponent(bank.key)}`)}
                className="w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-[11px] text-fg-muted hover:text-fg hover:bg-surface-2 transition-colors">
                <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ backgroundColor: scoreColor(bank.score || 5) }} />
                <span className="truncate">{bank.name}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Tools */}
      <div className="px-2 py-2 border-t border-border mt-auto">
        {!collapsed && <div className="px-3 py-1 text-[9px] font-bold text-fg-disabled uppercase tracking-wider">Tools</div>}
        {TOOL_ITEMS.map(item => <NavButton key={item.path} {...item} />)}
      </div>

      {/* Footer: theme + collapse */}
      <div className="px-2 py-3 border-t border-border flex items-center gap-1">
        <button onClick={toggleTheme} className="p-2 rounded-lg hover:bg-surface-2 text-fg-muted transition-colors" title={theme === 'dark' ? 'Light mode' : 'Dark mode'}>
          {theme === 'dark' ? <Sun size={14} /> : <Moon size={14} />}
        </button>
        {!collapsed && <div className="flex-1" />}
        <button onClick={() => setCollapsed(!collapsed)} className="p-2 rounded-lg hover:bg-surface-2 text-fg-muted transition-colors">
          {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </button>
      </div>
    </aside>
  );
}
