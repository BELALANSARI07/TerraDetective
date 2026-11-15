import React, { useState, useEffect } from 'react';
import { 
  Sparkles, Compass, ShieldCheck, Database, 
  GraduationCap, Microscope, UploadCloud, X, FileText, CheckCircle2, Loader2, ChevronDown 
} from 'lucide-react';

export default function Navbar({
  mode = 'student',
  onToggleMode,
  activeCaseId,
  onSelectCase,
  dataSource = 'Verified NASA Archive',
  isCustom = false,
  onUploadSuccess,
}) {
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFileA, setUploadFileA] = useState(null);
  const [uploadFileB, setUploadFileB] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  const cases = [
    { id: 'case_1_monsoon_paradox', title: 'Monsoon Paradox', icon: '🌧️', label: 'Marathwada vs. NE India' },
    { id: 'case_2_land_thermal_paradox', title: 'Thermal Paradox', icon: '🔥', label: 'Amazon vs. Punjab' },
    { id: 'case_3_vegetation_paradox', title: 'Vegetation Paradox', icon: '🌱', label: 'Amazon vs. Punjab' },
  ];

  const isLight = mode === 'student';

  // Handle Escape key to close modal
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && showUploadModal) {
        setShowUploadModal(false);
      }
    };
    if (showUploadModal) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [showUploadModal]);

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!uploadFileA) return;

    setUploadLoading(true);
    setUploadError(null);

    const formData = new FormData();
    formData.append('file', uploadFileA);
    if (uploadFileB) {
      formData.append('file_b', uploadFileB);
    }

    try {
      const res = await fetch('/api/upload/csv', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `HTTP ${res.status}: Upload failed`);
      }

      const payload = await res.json();
      if (onUploadSuccess) {
        onUploadSuccess(payload);
      }
      setShowUploadModal(false);
      setUploadFileA(null);
      setUploadFileB(null);
    } catch (err) {
      console.error('CSV upload error:', err);
      setUploadError(err.message);
    } finally {
      setUploadLoading(false);
    }
  };

  return (
    <>
      <header className={`sticky top-0 z-50 border-b transition-colors duration-200 ${
        isLight 
          ? 'bg-[#FAF8F5]/95 border-[#DCD7C9] text-archival-ink' 
          : 'bg-[#0A0E15]/95 border-[#1E2636] text-obsidian-text'
      } backdrop-blur-md`}>
        <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14 gap-2">
            
            {/* Logo & NASA Branding */}
            <div className="flex items-center space-x-2 sm:space-x-3 flex-shrink-0">
              <div className={`w-7 h-7 sm:w-8 sm:h-8 rounded-lg flex items-center justify-center font-bold text-white shadow-xs ${
                isLight ? 'bg-archival-terracotta' : 'bg-gradient-to-br from-cyan-500 to-blue-600'
              }`}>
                <Compass className="w-4 h-4" />
              </div>
              <div className="flex items-center space-x-1.5 sm:space-x-2">
                <span className={`font-bold text-base sm:text-lg tracking-tight ${isLight ? 'font-serif text-xl sm:text-2xl' : 'font-mono'}`}>
                  TerraDetective
                </span>
                <span className={`hidden sm:inline-block text-[10px] font-mono uppercase px-2 py-0.5 rounded font-semibold ${
                  isLight 
                    ? 'bg-archival-sand text-archival-ink border border-[#DCD7C9]' 
                    : 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/30'
                }`}>
                  NASA Space Apps
                </span>
              </div>
            </div>

            {/* Desktop Navigation (>= lg 1024px): Full Case Pills + Upload Button */}
            <nav className="hidden lg:flex items-center space-x-1.5">
              {cases.map((c) => {
                const isActive = activeCaseId === c.id && !isCustom;
                return (
                  <button
                    key={c.id}
                    onClick={() => onSelectCase(c.id)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all flex items-center space-x-1.5 focus-visible:ring-2 focus-visible:ring-archival-terracotta dark:focus-visible:ring-cyan-400 focus-visible:outline-none ${
                      isActive
                        ? isLight
                          ? 'bg-archival-ink text-white font-bold shadow-xs'
                          : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-xs'
                        : isLight
                          ? 'bg-white border border-[#DCD7C9] text-archival-ink hover:bg-archival-sand/40'
                          : 'bg-[#0C1017] text-slate-300 hover:bg-[#141B26] border border-[#1E2636]'
                    }`}
                  >
                    <span>{c.icon}</span>
                    <span className="font-sans font-semibold">{c.title}</span>
                  </button>
                );
              })}

              {/* Upload NASA CSV Trigger Button (Desktop) */}
              <button
                onClick={() => setShowUploadModal(true)}
                data-testid="upload-nasa-csv-btn"
                aria-label="Upload NASA CSV"
                className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all flex items-center space-x-1 border focus-visible:ring-2 focus-visible:ring-archival-viridian dark:focus-visible:ring-cyan-400 focus-visible:outline-none ${
                  isLight
                    ? 'bg-archival-viridian/10 text-archival-viridian border-archival-viridian/30 hover:bg-archival-viridian/20'
                    : 'bg-emerald-950/40 text-emerald-300 border-emerald-700/50 hover:bg-emerald-900/50'
                }`}
                title="Upload custom NASA Giovanni, AppEEARS, or NOAA CSV"
              >
                <UploadCloud className="w-3.5 h-3.5" />
                <span>Upload NASA CSV</span>
              </button>
            </nav>

            {/* Mobile / Tablet (< lg 1024px): Compact Dropdown + Icon Upload Button */}
            <div className="flex lg:hidden items-center space-x-1.5 flex-1 justify-center max-w-[280px]">
              <div className="relative w-full max-w-[190px]">
                <select
                  value={activeCaseId}
                  onChange={(e) => onSelectCase(e.target.value)}
                  aria-label="Select Flagship NASA Paradox Case"
                  className={`w-full text-xs font-semibold py-1.5 pl-2 pr-6 rounded-lg border appearance-none cursor-pointer focus-visible:ring-2 focus-visible:ring-archival-terracotta dark:focus-visible:ring-cyan-400 focus-visible:outline-none truncate transition-all ${
                    isLight 
                      ? 'bg-white border-[#DCD7C9] text-archival-ink' 
                      : 'bg-[#0C1017] border-[#1E2636] text-cyan-300'
                  }`}
                >
                  {cases.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.icon} {c.title}
                    </option>
                  ))}
                </select>
                <ChevronDown className="w-3 h-3 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400" />
              </div>

              {/* Compact Upload NASA CSV trigger for mobile/tablet */}
              <button
                onClick={() => setShowUploadModal(true)}
                data-testid="upload-nasa-csv-mobile-btn"
                aria-label="Upload NASA CSV"
                className={`p-1.5 rounded-lg text-xs font-semibold transition-all flex items-center space-x-1 border focus-visible:ring-2 focus-visible:ring-archival-viridian dark:focus-visible:ring-cyan-400 focus-visible:outline-none flex-shrink-0 ${
                  isLight
                    ? 'bg-archival-viridian/10 text-archival-viridian border-archival-viridian/30 hover:bg-archival-viridian/20'
                    : 'bg-emerald-950/40 text-emerald-300 border-emerald-700/50 hover:bg-emerald-900/50'
                }`}
                title="Upload custom NASA CSV"
              >
                <UploadCloud className="w-3.5 h-3.5" />
                <span className="hidden sm:inline text-[11px]">Upload</span>
              </button>
            </div>

            {/* Right Controls: Data Source Badge + Segmented Mode Switcher */}
            <div className="flex items-center space-x-1.5 sm:space-x-2 flex-shrink-0">
              {/* Live Data Badge */}
              <div className={`hidden md:flex items-center space-x-1.5 px-2 py-0.5 rounded text-[10px] font-mono border ${
                isCustom
                  ? isLight
                    ? 'bg-amber-50 text-amber-800 border-amber-300'
                    : 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                  : isLight
                    ? 'bg-archival-sand text-archival-ink border-[#DCD7C9]'
                    : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
              }`}>
                <Database className="w-2.5 h-2.5" />
                <span>{isCustom ? 'POWER LIVE' : 'NASA ARCHIVE'}</span>
              </div>

              {/* Segmented Dual-Mode Morphing Switch */}
              <div className={`flex items-center p-0.5 rounded-lg border transition-colors ${
                isLight ? 'bg-archival-sand/70 border-[#DCD7C9]' : 'bg-[#0C1017] border-[#1E2636]'
              }`}>
                <button
                  onClick={() => onToggleMode('student')}
                  aria-label="Switch to Explorer Story Mode"
                  className={`flex items-center space-x-1 sm:space-x-1.5 px-2 sm:px-2.5 py-1 rounded-md text-xs font-semibold transition-all focus-visible:ring-2 focus-visible:ring-archival-terracotta focus-visible:outline-none ${
                    mode === 'student'
                      ? 'bg-white text-archival-ink shadow-xs border border-[#DCD7C9]'
                      : 'text-archival-muted hover:text-archival-ink'
                  }`}
                  title="Explorer Story Mode (Editorial Field Atlas)"
                >
                  <GraduationCap className="w-3.5 h-3.5 text-archival-terracotta flex-shrink-0" />
                  <span className="hidden md:inline">Explorer Story</span>
                </button>

                <button
                  onClick={() => onToggleMode('scientist')}
                  aria-label="Switch to Telemetry Workbench Mode"
                  className={`flex items-center space-x-1 sm:space-x-1.5 px-2 sm:px-2.5 py-1 rounded-md text-xs font-semibold transition-all focus-visible:ring-2 dark:focus-visible:ring-cyan-400 focus-visible:outline-none ${
                    mode === 'scientist'
                      ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-xs'
                      : isLight ? 'text-archival-muted hover:text-archival-ink' : 'text-slate-400 hover:text-slate-200'
                  }`}
                  title="Telemetry Workbench Mode (NASA Ops IDE)"
                >
                  <Microscope className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
                  <span className="hidden md:inline">Telemetry</span>
                </button>
              </div>

            </div>

          </div>
        </div>
      </header>

      {/* Upload NASA CSV Modal */}
      {showUploadModal && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in"
          role="dialog"
          aria-modal="true"
          aria-labelledby="upload-modal-title"
          onClick={(e) => {
            if (e.target === e.currentTarget) setShowUploadModal(false);
          }}
        >
          <div className={`relative w-full max-w-lg p-5 sm:p-6 rounded-2xl border shadow-2xl ${
            isLight ? 'bg-white border-[#DCD7C9] text-archival-ink' : 'bg-[#0C1017] border-[#1E2636] text-slate-100'
          }`}>
            <button
              onClick={() => setShowUploadModal(false)}
              aria-label="Close upload dialog"
              className="absolute top-4 right-4 p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-slate-600 focus-visible:ring-2 focus-visible:ring-archival-terracotta dark:focus-visible:ring-cyan-400 focus-visible:outline-none"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center flex-shrink-0">
                <UploadCloud className="w-6 h-6" />
              </div>
              <div>
                <h3 id="upload-modal-title" className="font-extrabold text-lg">Bring Your Own NASA CSV</h3>
                <p className="text-xs text-slate-600 dark:text-slate-300">
                  Upload raw NASA Giovanni, AppEEARS, MODIS, or NOAA climate time series.
                </p>
              </div>
            </div>

            <form onSubmit={handleUploadSubmit} className="space-y-4">
              {/* File A Input */}
              <div>
                <label className="block text-xs font-semibold mb-1 text-slate-700 dark:text-slate-300">
                  Primary CSV (Region A or Multi-Region File) *
                </label>
                <input
                  type="file"
                  accept=".csv,text/csv"
                  onChange={(e) => setUploadFileA(e.target.files[0] || null)}
                  required
                  className={`w-full text-xs p-2.5 rounded-xl border file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold focus-visible:ring-2 focus-visible:ring-archival-terracotta dark:focus-visible:ring-cyan-400 focus-visible:outline-none ${
                    isLight
                      ? 'border-[#DCD7C9] bg-slate-50 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
                      : 'border-[#1E2636] bg-slate-800 file:bg-cyan-500/20 file:text-cyan-300 hover:file:bg-cyan-500/30'
                  }`}
                />
              </div>

              {/* Optional File B Input */}
              <div>
                <label className="block text-xs font-semibold mb-1 text-slate-700 dark:text-slate-300">
                  Optional Second CSV (Region B Comparator)
                </label>
                <input
                  type="file"
                  accept=".csv,text/csv"
                  onChange={(e) => setUploadFileB(e.target.files[0] || null)}
                  className={`w-full text-xs p-2.5 rounded-xl border file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold focus-visible:ring-2 focus-visible:ring-archival-terracotta dark:focus-visible:ring-cyan-400 focus-visible:outline-none ${
                    isLight
                      ? 'border-[#DCD7C9] bg-slate-50 file:bg-slate-200 file:text-slate-700 hover:file:bg-slate-300'
                      : 'border-[#1E2636] bg-slate-800 file:bg-slate-700 file:text-slate-300 hover:file:bg-slate-600'
                  }`}
                />
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                  Upload two files to analyze regional divergence, or upload a single file (auto-detects multiple regions).
                </p>
              </div>

              {uploadError && (
                <div className="p-3 rounded-lg bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300 text-xs">
                  {uploadError}
                </div>
              )}

              <div className="flex items-center justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 focus-visible:ring-2 focus-visible:ring-archival-terracotta dark:focus-visible:ring-cyan-400 focus-visible:outline-none"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  data-testid="upload-submit-btn"
                  disabled={uploadLoading || !uploadFileA}
                  className="px-5 py-2 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 dark:bg-cyan-500 dark:text-slate-950 dark:hover:bg-cyan-400 shadow-md flex items-center space-x-1.5 disabled:opacity-50 focus-visible:ring-2 focus-visible:ring-blue-500 dark:focus-visible:ring-cyan-400 focus-visible:outline-none"
                >
                  {uploadLoading ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Processing Decomposition...</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Upload & Analyze Trajectories</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
