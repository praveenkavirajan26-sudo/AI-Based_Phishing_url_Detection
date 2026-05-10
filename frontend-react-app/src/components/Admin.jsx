import React, { useState, useEffect } from 'react';
import {
  Users, BarChart3, Trash2, Shield, UserCheck, UserX,
  Search, RefreshCw, Eye, Crown, Activity, TrendingUp,
  AlertTriangle, CheckCircle, X, ChevronDown, ChevronUp
} from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// ── Mini Donut Chart (pure SVG, no lib needed) ──────────────────────────────
function DonutChart({ phishing, legitimate }) {
  const total = phishing + legitimate;
  if (total === 0) return <div className="text-gray-500 text-sm text-center">No scan data</div>;
  const r = 52, cx = 60, cy = 60, stroke = 14;
  const circ = 2 * Math.PI * r;
  const phishPct = phishing / total;
  const legitPct = legitimate / total;
  return (
    <svg width="120" height="120" viewBox="0 0 120 120">
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(34,197,94,0.25)" strokeWidth={stroke} />
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#ef4444"
        strokeWidth={stroke}
        strokeDasharray={`${phishPct * circ} ${circ}`}
        strokeDashoffset={circ * 0.25}
        strokeLinecap="round" />
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#22c55e"
        strokeWidth={stroke}
        strokeDasharray={`${legitPct * circ} ${circ}`}
        strokeDashoffset={-phishPct * circ + circ * 0.25}
        strokeLinecap="round" />
      <text x={cx} y={cy - 5} textAnchor="middle" fill="white" fontSize="14" fontWeight="bold">
        {Math.round(phishPct * 100)}%
      </text>
      <text x={cx} y={cy + 12} textAnchor="middle" fill="#9ca3af" fontSize="9">Phishing</text>
    </svg>
  );
}

// ── Stat Card ───────────────────────────────────────────────────────────────
function StatCard({ icon: Icon, value, label, color, glow }) {
  return (
    <div className={`glass p-5 rounded-2xl flex items-center gap-4 border ${glow}`} style={{borderColor: color + '40'}}>
      <div className="rounded-xl p-3" style={{background: color + '20'}}>
        <Icon className="w-6 h-6" style={{color}} />
      </div>
      <div>
        <div className="text-2xl font-bold font-mono" style={{color}}>{value}</div>
        <div className="text-gray-400 text-sm">{label}</div>
      </div>
    </div>
  );
}

// ── Mini Bar ─────────────────────────────────────────────────────────────────
function MiniBar({ day }) {
  const max = Math.max(day.total, 1);
  return (
    <div className="flex flex-col items-center gap-1 flex-1">
      <div className="w-full flex flex-col gap-0.5 justify-end" style={{height: 60}}>
        <div className="w-full rounded-sm bg-red-500 opacity-80 transition-all"
          style={{height: `${(day.phishing / max) * 60}px`}} />
        <div className="w-full rounded-sm bg-cyan-400 opacity-70 transition-all"
          style={{height: `${(day.legitimate / max) * 60}px`}} />
      </div>
      <span className="text-gray-500 text-xs">{day.date.split(' ')[1]}</span>
    </div>
  );
}

// ── User Detail Modal ─────────────────────────────────────────────────────────
function UserModal({ user, token, onClose }) {
  const [scans, setScans] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/admin/users/${user.id}/scans`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.json()).then(d => { setScans(d); setLoading(false); }).catch(() => setLoading(false));
  }, [user.id]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="glass rounded-2xl border border-cyan-500/30 w-full max-w-2xl max-h-[85vh] flex flex-col shadow-[0_0_40px_rgba(0,212,255,0.15)]">
        <div className="flex items-center justify-between p-5 border-b border-gray-800">
          <div>
            <h3 className="text-xl font-bold font-mono text-cyan-400">{user.username}</h3>
            <p className="text-gray-400 text-sm">{user.email || 'No email'}</p>
          </div>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="overflow-y-auto p-5 space-y-3">
          {loading ? (
            <div className="text-center py-8 text-gray-400">Loading scans...</div>
          ) : scans?.scans?.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No scans found for this user</div>
          ) : (
            scans?.scans?.map(s => (
              <div key={s.id} className="flex items-center justify-between p-3 rounded-xl bg-gray-900/60 border border-gray-800 gap-3">
                <span className="font-mono text-xs text-gray-300 truncate flex-1">{s.url}</span>
                <span className={`shrink-0 px-2 py-0.5 rounded-full text-xs font-bold ${s.prediction === 'Phishing' ? 'bg-red-900/60 text-red-300' : 'bg-green-900/60 text-green-300'}`}>
                  {s.prediction}
                </span>
                <span className="shrink-0 text-xs text-gray-500">{s.timestamp?.slice(0,10)}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

// ── Main Admin Component ──────────────────────────────────────────────────────
export default function Admin({ token }) {
  const [stats, setStats] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tab, setTab] = useState('overview');
  const [search, setSearch] = useState('');
  const [filterAdmin, setFilterAdmin] = useState('all');
  const [selectedUser, setSelectedUser] = useState(null);
  const [sortField, setSortField] = useState('id');
  const [sortAsc, setSortAsc] = useState(true);
  const [confirmDelete, setConfirmDelete] = useState(null);

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const h = { Authorization: `Bearer ${token}` };
      const [sRes, aRes, uRes] = await Promise.all([
        fetch(`${API_URL}/admin/stats`, { headers: h }),
        fetch(`${API_URL}/admin/analytics`, { headers: h }),
        fetch(`${API_URL}/admin/users`, { headers: h }),
      ]);
      if (sRes.ok) setStats(await sRes.json());
      if (aRes.ok) setAnalytics(await aRes.json());
      if (uRes.ok) setUsers(await uRes.json());
    } catch { setError('Failed to load admin data'); }
    finally { setLoading(false); }
  };

  const toggleAdmin = async (userId) => {
    const r = await fetch(`${API_URL}/admin/users/${userId}/admin`, {
      method: 'PUT', headers: { Authorization: `Bearer ${token}` }
    });
    if (r.ok) fetchData();
  };

  const deleteUser = async (userId) => {
    const r = await fetch(`${API_URL}/admin/users/${userId}`, {
      method: 'DELETE', headers: { Authorization: `Bearer ${token}` }
    });
    if (r.ok) { setConfirmDelete(null); fetchData(); }
  };

  const filteredUsers = users
    .filter(u => {
      const q = search.toLowerCase();
      return (u.username.toLowerCase().includes(q) || (u.email || '').toLowerCase().includes(q));
    })
    .filter(u => filterAdmin === 'all' ? true : filterAdmin === 'admin' ? u.is_admin : !u.is_admin)
    .sort((a, b) => {
      let va = a[sortField], vb = b[sortField];
      if (typeof va === 'string') va = va.toLowerCase();
      if (typeof vb === 'string') vb = vb.toLowerCase();
      return sortAsc ? (va > vb ? 1 : -1) : (va < vb ? 1 : -1);
    });

  const SortIcon = ({ field }) => sortField === field
    ? (sortAsc ? <ChevronUp className="w-3 h-3 inline ml-1 text-cyan-400" /> : <ChevronDown className="w-3 h-3 inline ml-1 text-cyan-400" />)
    : <ChevronDown className="w-3 h-3 inline ml-1 text-gray-600" />;

  const handleSort = (field) => {
    if (sortField === field) setSortAsc(!sortAsc);
    else { setSortField(field); setSortAsc(true); }
  };

  if (loading) return (
    <div className="w-full max-w-6xl mx-auto p-6 flex flex-col items-center justify-center min-h-[60vh]">
      <div className="w-12 h-12 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin mb-4" />
      <p className="text-gray-400 font-mono">Loading Admin Panel...</p>
    </div>
  );

  return (
    <div className="w-full max-w-6xl mx-auto p-4 sm:p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/30">
            <Shield className="w-7 h-7 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold font-mono text-white">Admin <span className="text-cyan-400">Dashboard</span></h1>
            <p className="text-gray-500 text-xs">PhishGuard Control Center</p>
          </div>
        </div>
        <button onClick={fetchData}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white transition-all text-sm border border-gray-700">
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      {error && (
        <div className="bg-red-900/40 border border-red-500/50 text-red-300 p-4 rounded-xl flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" /> {error}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-800">
        {[['overview', Activity, 'Overview'], ['users', Users, 'Users']].map(([key, Icon, label]) => (
          <button key={key} onClick={() => setTab(key)}
            className={`flex items-center gap-2 px-4 py-2.5 text-sm font-mono font-medium transition-all border-b-2 -mb-px ${
              tab === key ? 'border-cyan-400 text-cyan-400' : 'border-transparent text-gray-400 hover:text-white'
            }`}>
            <Icon className="w-4 h-4" />{label}
          </button>
        ))}
      </div>

      {/* OVERVIEW TAB */}
      {tab === 'overview' && (
        <div className="space-y-6">
          {/* Stat Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard icon={Users} value={stats?.total_users ?? 0} label="Total Users" color="#00d4ff" glow="glow-blue" />
            <StatCard icon={BarChart3} value={stats?.total_scans ?? 0} label="Total Scans" color="#a78bfa" glow="" />
            <StatCard icon={UserCheck} value={stats?.verified_users ?? 0} label="Verified Users" color="#22c55e" glow="" />
            <StatCard icon={Crown} value={stats?.admin_users ?? 0} label="Admins" color="#f59e0b" glow="" />
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Donut */}
            <div className="glass rounded-2xl p-5 flex flex-col items-center gap-3">
              <h3 className="font-bold text-sm text-gray-300 self-start">Threat Breakdown</h3>
              <DonutChart phishing={analytics?.phishing_scans ?? 0} legitimate={analytics?.legitimate_scans ?? 0} />
              <div className="flex gap-4 text-xs">
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500 inline-block"/>Phishing ({analytics?.phishing_scans ?? 0})</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500 inline-block"/>Legit ({analytics?.legitimate_scans ?? 0})</span>
              </div>
            </div>

            {/* Bar chart - 7 day trend */}
            <div className="glass rounded-2xl p-5 md:col-span-2">
              <h3 className="font-bold text-sm text-gray-300 mb-4">7-Day Scan Trend</h3>
              <div className="flex items-end gap-1 h-20">
                {(analytics?.daily_trend ?? []).map((d, i) => <MiniBar key={i} day={d} />)}
              </div>
              <div className="flex gap-4 text-xs mt-3">
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-red-500 inline-block"/>Phishing</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-cyan-400 inline-block"/>Legitimate</span>
              </div>
            </div>
          </div>

          {/* Recent Scans + Top Users */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Recent Scans */}
            <div className="glass rounded-2xl p-5">
              <h3 className="font-bold text-sm text-gray-300 mb-3 flex items-center gap-2"><TrendingUp className="w-4 h-4 text-cyan-400"/>Recent Scans</h3>
              <div className="space-y-2">
                {(stats?.recent_scans ?? []).map(s => (
                  <div key={s.id} className="flex items-center justify-between p-2.5 rounded-lg bg-gray-900/60 gap-2">
                    <span className="font-mono text-xs text-gray-300 truncate flex-1">{s.url}</span>
                    <span className={`shrink-0 px-2 py-0.5 rounded-full text-xs font-semibold ${s.prediction === 'Phishing' ? 'bg-red-900/60 text-red-300' : 'bg-green-900/60 text-green-300'}`}>
                      {s.prediction}
                    </span>
                  </div>
                ))}
                {!stats?.recent_scans?.length && <p className="text-gray-500 text-sm text-center py-4">No scans yet</p>}
              </div>
            </div>

            {/* Top Users */}
            <div className="glass rounded-2xl p-5">
              <h3 className="font-bold text-sm text-gray-300 mb-3 flex items-center gap-2"><Crown className="w-4 h-4 text-yellow-400"/>Top Scanners</h3>
              <div className="space-y-2">
                {(analytics?.top_users ?? []).map((u, i) => (
                  <div key={i} className="flex items-center gap-3 p-2.5 rounded-lg bg-gray-900/60">
                    <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${i === 0 ? 'bg-yellow-500 text-black' : i === 1 ? 'bg-gray-400 text-black' : 'bg-amber-700 text-white'}`}>{i + 1}</span>
                    <span className="flex-1 font-mono text-sm text-gray-200">{u.username}</span>
                    <span className="text-cyan-400 font-bold text-sm">{u.scan_count} scans</span>
                  </div>
                ))}
                {!analytics?.top_users?.length && <p className="text-gray-500 text-sm text-center py-4">No data yet</p>}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* USERS TAB */}
      {tab === 'users' && (
        <div className="space-y-4">
          {/* Search + Filter */}
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text" value={search} onChange={e => setSearch(e.target.value)}
                placeholder="Search username or email..."
                className="w-full pl-10 pr-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-sm text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>
            <select value={filterAdmin} onChange={e => setFilterAdmin(e.target.value)}
              className="px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-sm text-gray-300 focus:outline-none focus:border-cyan-500 transition-colors">
              <option value="all">All Users ({users.length})</option>
              <option value="admin">Admins Only</option>
              <option value="user">Regular Users</option>
            </select>
          </div>

          {/* Users Table */}
          <div className="glass rounded-2xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-800 bg-gray-900/50">
                    {[['id','#'],['username','Username'],['email','Email']].map(([f,l]) => (
                      <th key={f} className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider cursor-pointer hover:text-white transition-colors"
                        onClick={() => handleSort(f)}>
                        {l}<SortIcon field={f} />
                      </th>
                    ))}
                    <th className="text-center py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Verified</th>
                    <th className="text-center py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Role</th>
                    <th className="text-center py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800/60">
                  {filteredUsers.map(user => (
                    <tr key={user.id} className="hover:bg-gray-800/30 transition-colors group">
                      <td className="py-3 px-4 text-gray-500 text-sm font-mono">#{user.id}</td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-full bg-cyan-900/50 border border-cyan-700/40 flex items-center justify-center text-cyan-400 font-bold text-sm">
                            {user.username[0].toUpperCase()}
                          </div>
                          <span className="font-medium text-gray-200">{user.username}</span>
                          {user.is_admin && <Crown className="w-3.5 h-3.5 text-yellow-400" title="Admin" />}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-gray-400 text-sm">{user.email || <span className="text-gray-600 italic">—</span>}</td>
                      <td className="py-3 px-4 text-center">
                        {user.is_verified
                          ? <CheckCircle className="w-4 h-4 text-green-500 mx-auto" />
                          : <X className="w-4 h-4 text-red-500 mx-auto" />}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${user.is_admin ? 'bg-yellow-900/50 text-yellow-300 border border-yellow-700/40' : 'bg-gray-800 text-gray-400'}`}>
                          {user.is_admin ? 'Admin' : 'User'}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center justify-center gap-2">
                          <button onClick={() => setSelectedUser(user)} title="View Scans"
                            className="p-1.5 rounded-lg bg-cyan-900/30 text-cyan-400 hover:bg-cyan-900/60 transition-colors">
                            <Eye className="w-3.5 h-3.5" />
                          </button>
                          <button onClick={() => toggleAdmin(user.id)} title={user.is_admin ? 'Remove Admin' : 'Make Admin'}
                            className={`p-1.5 rounded-lg transition-colors ${user.is_admin ? 'bg-yellow-900/30 text-yellow-400 hover:bg-yellow-900/60' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}`}>
                            <Crown className="w-3.5 h-3.5" />
                          </button>
                          <button onClick={() => setConfirmDelete(user)} title="Delete User"
                            className="p-1.5 rounded-lg bg-red-900/30 text-red-400 hover:bg-red-900/60 transition-colors">
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {filteredUsers.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  <UserX className="w-10 h-10 mx-auto mb-2 opacity-30" />
                  <p>No users found</p>
                </div>
              )}
            </div>
          </div>
          <p className="text-gray-600 text-xs text-right">{filteredUsers.length} of {users.length} users</p>
        </div>
      )}

      {/* User Detail Modal */}
      {selectedUser && <UserModal user={selectedUser} token={token} onClose={() => setSelectedUser(null)} />}

      {/* Delete Confirm Modal */}
      {confirmDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="glass rounded-2xl border border-red-500/40 p-6 w-full max-w-sm shadow-[0_0_30px_rgba(239,68,68,0.2)]">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-xl bg-red-900/40"><AlertTriangle className="w-5 h-5 text-red-400" /></div>
              <h3 className="font-bold text-white">Delete User?</h3>
            </div>
            <p className="text-gray-400 text-sm mb-5">
              This will permanently delete <strong className="text-white">{confirmDelete.username}</strong> and all their scan history. This cannot be undone.
            </p>
            <div className="flex gap-3">
              <button onClick={() => setConfirmDelete(null)}
                className="flex-1 py-2 rounded-xl bg-gray-800 text-gray-300 hover:bg-gray-700 transition-colors text-sm">
                Cancel
              </button>
              <button onClick={() => deleteUser(confirmDelete.id)}
                className="flex-1 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white transition-colors text-sm font-semibold">
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}