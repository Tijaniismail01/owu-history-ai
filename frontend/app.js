const { useState, useEffect, useRef } = React;
const { createRoot } = ReactDOM;

console.log("App.js is executing...");


// --- API Service ---
const API_URL = "http://localhost:8000";

async function generateNarrative(query, age, education, tone) {
    try {
        const response = await fetch(`${API_URL}/generate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query,
                user_age: parseInt(age),
                education_level: education,
                tone: tone
            })
        });
        if (!response.ok) throw new Error("Network response was not ok");
        return await response.json();
    } catch (error) {
        console.error("API Error:", error);
        return null;
    }
}

// --- Icons ---
const Icon = ({ path, size = 20, className = "" }) => (
    <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className}>
        {path}
    </svg>
);
const Icons = {
    Menu: <path d="M3 12h18M3 6h18M3 18h18" />,
    Search: <path d="M11 11a8 8 0 1 0 0-1.06zM21 21l-4.35-4.35" />,
    Feather: <path d="M20.24 12.24a6 6 0 0 0-8.49-8.49L5 10.5V19h8.5zM16 8 2 22M17.5 15H9" />,
    Clock: <><circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" /></>,
    Settings: <><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" /></>,
    X: <path d="M18 6 6 18M6 6l12 12" />
};

// --- Components ---

const Sidebar = ({ activeTab, setActiveTab, onOpenSettings }) => (
    <aside className="fixed left-0 top-0 bottom-0 w-20 flex flex-col items-center py-8 z-50 border-r border-[#ffffff0a] bg-[#050505]/80 backdrop-blur-md">
        <div className="w-10 h-10 rounded-full border border-[#D4AF37] flex items-center justify-center text-[#D4AF37] font-display text-xl mb-12 shadow-[0_0_15px_rgba(212,175,55,0.2)]">O</div>
        <nav className="flex flex-col gap-8 w-full items-center">
            {[
                { id: 'narrative', icon: Icons.Feather, label: 'Narrative' },
                { id: 'timeline', icon: Icons.Clock, label: 'Timeline' },
            ].map((item) => (
                <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`group relative w-10 h-10 flex items-center justify-center rounded-xl transition-all duration-300
                        ${activeTab === item.id ? 'text-black bg-[#D4AF37]' : 'text-[#555] hover:text-[#EAEAEA] hover:bg-[#ffffff0a]'}`}
                >
                    <Icon path={item.icon} size={20} />
                </button>
            ))}

            <button onClick={onOpenSettings} className="mt-auto text-[#555] hover:text-[#D4AF37] transition-colors">
                <Icon path={Icons.Settings} size={20} />
            </button>
        </nav>
    </aside>
);

const CommandBar = ({ onSearch, loading }) => (
    <div className="fixed bottom-8 left-0 right-0 z-40 flex justify-center pointer-events-none fade-in">
        <div className="pointer-events-auto w-full max-w-2xl mx-4">
            <div className={`glass-panel rounded-2xl p-2 flex items-center gap-4 shadow-2xl transition-all ${loading ? 'opacity-50 pointer-events-none' : ''}`}>
                <div className="w-10 h-10 rounded-xl bg-[#0a0a0a] flex items-center justify-center text-[#D4AF37]">
                    <Icon path={Icons.Search} />
                </div>
                <input
                    type="text"
                    placeholder="Ask the archives about Owu history..."
                    className="flex-1 bg-transparent border-none outline-none text-[#EAEAEA] placeholder-[#555] text-lg font-light h-10"
                    onKeyDown={(e) => e.key === 'Enter' && onSearch(e.target.value)}
                />
                <button
                    onClick={() => {
                        const input = document.querySelector('input[type="text"]');
                        if (input) onSearch(input.value);
                    }}
                    className="h-10 px-6 bg-[#EAEAEA] text-black font-medium text-sm tracking-wide rounded-lg hover:bg-[#D4AF37] transition-colors">
                    {loading ? "SEARCHING..." : "EXPLORE"}
                </button>
            </div>
        </div>
    </div>
);

const SettingsModal = ({ isOpen, onClose, prefs, setPrefs }) => {
    if (!isOpen) return null;
    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm">
            <div className="bg-[#0a0a0a] border border-[#333] rounded-2xl p-8 w-full max-w-md shadow-2xl slide-up relative">
                <button onClick={onClose} className="absolute top-4 right-4 text-[#555] hover:text-white">
                    <Icon path={Icons.X} />
                </button>
                <h2 className="text-2xl font-display text-[#D4AF37] mb-6">Personalization</h2>

                <div className="space-y-6">
                    <div>
                        <label className="text-xs uppercase tracking-widest text-[#555] block mb-2">Age Group</label>
                        <input
                            type="range" min="8" max="80" value={prefs.age}
                            onChange={(e) => setPrefs({ ...prefs, age: e.target.value })}
                            className="w-full h-2 bg-[#333] rounded-lg appearance-none cursor-pointer"
                        />
                        <div className="text-right text-[#EAEAEA] mt-1">{prefs.age} Years</div>
                    </div>

                    <div>
                        <label className="text-xs uppercase tracking-widest text-[#555] block mb-2">Education Level</label>
                        <div className="flex bg-[#111] rounded-lg p-1">
                            {['Child', 'General', 'Academic'].map(level => (
                                <button
                                    key={level}
                                    onClick={() => setPrefs({ ...prefs, education: level })}
                                    className={`flex-1 py-2 text-sm rounded-md transition-all ${prefs.education === level ? 'bg-[#333] text-[#D4AF37]' : 'text-[#555]'}`}
                                >
                                    {level}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div>
                        <label className="text-xs uppercase tracking-widest text-[#555] block mb-2">Narrative Tone</label>
                        <div className="flex bg-[#111] rounded-lg p-1">
                            {['Storyteller', 'Neutral', 'Formal'].map(tone => (
                                <button
                                    key={tone}
                                    onClick={() => setPrefs({ ...prefs, tone: tone })}
                                    className={`flex-1 py-2 text-sm rounded-md transition-all ${prefs.tone === tone ? 'bg-[#333] text-[#D4AF37]' : 'text-[#555]'}`}
                                >
                                    {tone}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const NarrativeView = ({ data, loading }) => {
    if (loading) {
        return (
            <div className="h-full flex flex-col items-center justify-center text-[#555]">
                <div className="animate-spin mb-4 text-[#D4AF37]"><Icon path={Icons.Clock} size={40} /></div>
                <div className="text-sm tracking-widest uppercase">Consulting Archives...</div>
            </div>
        );
    }

    if (!data) return (
        <div className="h-full flex flex-col items-center justify-center text-[#333]">
            <div className="text-6xl font-display text-[#222] mb-4">Owu History</div>
            <div className="text-sm tracking-widest">Ask a question to begin</div>
        </div>
    );

    return (
        <div className="max-w-4xl mx-auto pt-10 pb-40 px-8 slide-up">
            <div className="flex items-center gap-4 text-xs tracking-[0.2em] text-[#D4AF37] mb-6 opacity-80">
                <span>GENERATED NARRATIVE</span>
                <span className="w-px h-3 bg-[#333]"></span>
                <span>CONFIDENCE: {data.sources[0]?.confidence_score ? Math.round(data.sources[0].confidence_score * 100) + '%' : 'N/A'}</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-12 gap-12">
                <div className="md:col-span-8 space-y-6 text-lg font-light leading-relaxed text-[#bbb]">
                    {/* Markdown-like rendering helper could go here, for now simple split */}
                    {data.narrative.split('\n').map((para, i) => (
                        <p key={i}>{para}</p>
                    ))}

                    {/* Sources Footnote */}
                    <div className="mt-12 pt-8 border-t border-[#ffffff0a]">
                        <h4 className="text-sm uppercase tracking-widest text-[#555] mb-4">Sources</h4>
                        <ul className="space-y-2 text-sm text-[#777]">
                            {data.sources.map((s, i) => (
                                <li key={i} className="flex items-center gap-2">
                                    <span className="w-1.5 h-1.5 rounded-full bg-[#D4AF37]"></span>
                                    {s.title} <span className="text-[#444]">({s.type})</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                <div className="md:col-span-4 space-y-8">
                    {/* Timeline Widget */}
                    {data.timeline.length > 0 && (
                        <div className="border-l border-[#ffffff0a] pl-6 space-y-8">
                            <h3 className="font-display text-2xl text-[#EAEAEA]">Timeline</h3>
                            {data.timeline.map((evt, i) => (
                                <div key={i} className="relative">
                                    <div className="absolute -left-[29px] top-1.5 w-1.5 h-1.5 rounded-full bg-[#D4AF37] ring-4 ring-[#050505]"></div>
                                    <div className="text-[#D4AF37] text-sm font-medium mb-1">{evt.year}</div>
                                    <div className="text-[#888] text-sm leading-snug">{evt.event}</div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

// --- Main App ---
function App() {
    const [activeTab, setActiveTab] = useState('narrative');
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState(null);
    const [showSettings, setShowSettings] = useState(false);

    // Personalization State
    const [prefs, setPrefs] = useState({
        age: 25,
        education: 'General',
        tone: 'Neutral'
    });

    const handleSearch = async (query) => {
        if (!query.trim()) return;
        setLoading(true);
        setData(null); // Clear previous

        const result = await generateNarrative(query, prefs.age, prefs.education, prefs.tone);
        setData(result);
        setLoading(false);
    };

    return (
        <div className="min-h-screen w-full bg-[#050505] text-[#EAEAEA]">
            <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} onOpenSettings={() => setShowSettings(true)} />

            <SettingsModal isOpen={showSettings} onClose={() => setShowSettings(false)} prefs={prefs} setPrefs={setPrefs} />

            <main className="pl-20 w-full h-screen overflow-y-auto custom-scrollbar relative">
                {/* Decor */}
                <div className="fixed top-0 right-0 w-[50vw] h-[50vh] bg-[#D4AF37] opacity-[0.03] blur-[100px] pointer-events-none rounded-full translate-x-1/2 -translate-y-1/2"></div>

                <NarrativeView data={data} loading={loading} />

                <CommandBar onSearch={handleSearch} loading={loading} />
            </main>
        </div>
    );
}

const root = createRoot(document.getElementById('root'));
root.render(<App />);
