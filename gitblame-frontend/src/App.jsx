import { useState, useEffect, useRef } from 'react'
import { Routes, Route } from 'react-router-dom'
import Callback from './Callback.jsx'
import './App.css'
const API = import.meta.env.VITE_API_URL

function App() {
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)
  const [darkMode, setDarkMode] = useState(true)
  const [repos, setRepos] = useState([])
  const [selectedRepo, setSelectedRepo] = useState(null)
  const [since, setSince] = useState('')
  const [until, setUntil] = useState('')
  const [commits, setCommits] = useState([])
  const [bugDescription, setBugDescription] = useState('')
  const [analysisResults, setAnalysisResults] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [fetching, setFetching] = useState(false)
  const [error, setError] = useState(null)

  const step2Ref = useRef(null)
  const step3Ref = useRef(null)
  const step4Ref = useRef(null)

  useEffect(() => {
    const savedToken = localStorage.getItem('github_token')
    if (savedToken) {
      setToken(savedToken)
    }
    setLoading(false)
  }, [])

  useEffect(() => {
    document.body.classList.toggle('light', !darkMode)
  }, [darkMode])

  useEffect(() => {
    if (!token) return
    fetch(`${API}/github/repos?token=${token}`)
      .then(r => r.json())
      .then(data => setRepos(data))
  }, [token])

  function scrollTo(ref) {
    setTimeout(() => {
      ref.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }, 120)
  }

  function handleLogin() {
    fetch(`${API}/auth/github/login`)
      .then(r => r.json())
      .then(data => { window.location.href = data.url })
  }

  function handleLogout() {
    localStorage.removeItem('github_token')
    setToken(null)
    setRepos([])
    setSelectedRepo(null)
    setCommits([])
    setSince('')
    setUntil('')
    setBugDescription('')
    setAnalysisResults(null)
  }

  function handleSelectRepo(repo) {
    setSelectedRepo(repo.full_name)
    setCommits([])
    setAnalysisResults(null)
    scrollTo(step2Ref)
  }

  function handleFetchCommits() {
    if (!since || !until || !selectedRepo) return
    setFetching(true)
    fetch(`${API}/github/commits?repo=${selectedRepo}&token=${token}&since=${since}&until=${until}`)
      .then(r => r.json())
      .then(data => {
        setCommits(data)
        setFetching(false)
        scrollTo(step3Ref)
      })
  }

  function chunkDiffs(diffs) {
    const chunks = []
    diffs.forEach(commit => {
      commit.files.forEach(file => {
        if (file.patch) {
          chunks.push({
            sha: commit.sha,
            message: commit.message,
            filename: file.filename,
            patch: file.patch
          })
        }
      })
    })
    return chunks
  }

  function handleAnalyze() {
    if (!bugDescription.trim()) return
    setAnalyzing(true)
    setAnalysisResults(null)
    setError(null)

    fetch(`${API}/github/all-diffs?repo=${selectedRepo}&token=${token}&since=${since}&until=${until}`)
      .then(r => r.json())
      .then(diffs => {
        const chunks = chunkDiffs(diffs)
        return fetch(`${API}/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ chunks, bug_description: bugDescription })
        })
      })
      .then(r => r.json())
      .then(data => {
        setAnalysisResults(Array.isArray(data) ? data : [])
        setAnalyzing(false)
        scrollTo(step4Ref)
      })
      .catch(err => {
        setAnalyzing(false)
        setError('Analysis failed. Make sure Ollama is running and try again.')
      })
  }

  function getScoreClass(confidence) {
    if (confidence >= 75) return 'hi'
    if (confidence >= 50) return 'md'
    return 'lo'
  }

  function getCardClass(confidence) {
    if (confidence >= 75) return 's-card s-high'
    if (confidence >= 50) return 's-card s-med'
    return 's-card s-low'
  }

  function copyText(text, e) {
    navigator.clipboard.writeText(text).then(() => {
      e.target.textContent = 'copied ✓'
      e.target.style.color = 'var(--low)'
      setTimeout(() => {
        e.target.textContent = 'copy'
        e.target.style.color = ''
      }, 1500)
    })
  }

  return (
    <Routes>
      <Route path="/" element={
        <div>
          {/* NAV */}
          <nav>
            <div className="logo">Git<span>Blame</span> AI</div>
            <div className="nav-r">
              {token && (
                <div className="connected">
                  <div className="status-dot"></div>
                  {repos[0]?.owner?.login || 'GitHub'}
                </div>
              )}
              <button className="mode-btn" onClick={() => setDarkMode(!darkMode)}>
                {darkMode ? '☀️' : '🌙'}
              </button>
              {token && (
                <button className="btn-signout" onClick={handleLogout}>Sign out</button>
              )}
            </div>
          </nav>

          {loading ? null : !token ? (

            /* ── LOGIN PAGE ── */
            <div className="login-page">
              <span className="hero-eyebrow">Commit forensics</span>
              <h1>Find the commit<br />that <em>broke</em> everything.</h1>
              <p className="hero-sub">Describe the bug in plain English. We search your entire git history and rank the suspects.</p>
              <button className="btn-primary" onClick={handleLogin}>
                Login with GitHub
              </button>
            </div>

          ) : (
            <>
              {/* ── STEP 1 — REPO ── */}
              <div className="step">
                <div className="step-meta">
                  <span className="step-num">01</span>
                  <div className="step-line"></div>
                </div>
                <h2>Which repo are we<br /><em>investigating?</em></h2>
                <div className="repo-grid">
                  {repos.map(repo => (
                    <button
                      key={repo.id}
                      className={`repo-chip ${selectedRepo === repo.full_name ? 'active' : ''}`}
                      onClick={() => handleSelectRepo(repo)}
                    >
                      {repo.name}
                    </button>
                  ))}
                </div>
              </div>

              {/* ── STEP 2 — DATE ── */}
              <div className="step" ref={step2Ref}>
                <div className="step-meta">
                  <span className="step-num">02</span>
                  <div className="step-line"></div>
                </div>
                <h2>When did things<br /><em>go wrong?</em></h2>
                <div className="date-row">
                  <div className="field-wrap">
                    <span className="field-lbl">From</span>
                    <input type="date" value={since} onChange={e => setSince(e.target.value)} />
                  </div>
                  <div className="field-wrap">
                    <span className="field-lbl">Until</span>
                    <input type="date" value={until} onChange={e => setUntil(e.target.value)} />
                  </div>
                </div>
                <div className="btn-row">
                  <button
                    className="btn-outline"
                    onClick={handleFetchCommits}
                    disabled={fetching || !selectedRepo || !since || !until}
                  >
                    {fetching ? 'Fetching commits...' : commits.length > 0 ? `${commits.length} commits loaded — refetch` : 'Fetch commits'}
                  </button>
                </div>
              </div>

              {/* ── STEP 3 — COMMITS + BUG ── */}
              {commits.length > 0 && (
                <div className="step" ref={step3Ref}>
                  <div className="step-meta">
                    <span className="step-num">03</span>
                    <div className="step-line"></div>
                  </div>
                  <h2>What<br /><em>broke?</em></h2>
                  <div className="commit-list">
                    {commits.map(commit => (
                      <div className="commit-item" key={commit.sha}>
                        <span className="c-sha">{commit.sha.slice(0, 7)}</span>
                        <span className="c-msg">{commit.commit.message}</span>
                      </div>
                    ))}
                  </div>
                  <textarea
                    rows={4}
                    placeholder="e.g. login stopped working after Tuesday's deploy, users getting 401 errors on the dashboard..."
                    value={bugDescription}
                    onChange={e => setBugDescription(e.target.value)}
                  />
                  <div className="btn-row">
                    <button
                      className="btn-primary"
                      onClick={handleAnalyze}
                      disabled={analyzing || !bugDescription.trim()}
                    >
                      {analyzing ? (
                        <span style={{ display: 'flex', alignItems: 'center', gap: '10px', justifyContent: 'center' }}>
                          <span className="spinner"></span>
                          Analyzing commits...
                        </span>
                      ) : 'Analyze commits'}
                    </button>
                    {analyzing && (
                      <p style={{ fontSize: '12px', color: 'var(--text3)', marginTop: '0.75rem', letterSpacing: '0.04em' }}>
                        Running semantic search + LLM reasoning — this takes 30–60s
                      </p>
                    )}
                    {error && (
                      <p style={{ fontSize: '13px', color: 'var(--high)', marginTop: '0.75rem' }}>
                        ⚠ {error}
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* ── STEP 4 — RESULTS ── */}
              {analysisResults && (
                <div className="step" ref={step4Ref}>
                  <div className="step-meta">
                    <span className="step-num">04</span>
                    <div className="step-line"></div>
                  </div>
                  <h2>The<br /><em>suspects.</em></h2>
                  <div>
                    <div className="results-hdr">
                      <span className="results-ttl">Ranked by likelihood</span>
                      <span className="results-ct">{analysisResults.length} suspects found</span>
                    </div>
                    {analysisResults.map((suspect, i) => (
                      <div key={i} className={getCardClass(suspect.confidence)}>
                        <div className="s-top">
                          <div className="s-left">
                            <div className="s-msg">{suspect.message}</div>
                            <div className="s-file">{suspect.filename} · {suspect.sha?.slice(0, 7)}</div>
                          </div>
                          <div className="s-score">
                            <div className={`s-num ${getScoreClass(suspect.confidence)}`}>
                              {suspect.confidence}%
                            </div>
                            <div className="s-bar-wrap">
                              <div
                                className={`s-bar ${getScoreClass(suspect.confidence)}`}
                                style={{ width: `${suspect.confidence}%` }}
                              ></div>
                            </div>
                          </div>
                        </div>

                        <div className="s-section">
                          <div className="s-sect-lbl">Why suspicious</div>
                          <div className="s-sect-txt">{suspect.explanation}</div>
                        </div>

                        {suspect.suspicious_lines && (
                          <div className="s-section">
                            <div className="s-sect-lbl">Suspicious lines</div>
                            <div className="s-sect-txt" style={{ fontFamily: 'monospace', fontSize: '13px' }}>
                              {suspect.suspicious_lines}
                            </div>
                          </div>
                        )}

                        <div className="s-bottom">
                          <div>
                            <div className="s-sect-lbl">Rollback</div>
                            <div className="code-pill">
                              <span>{suspect.rollback_command}</span>
                              <button className="cp-btn" onClick={e => copyText(suspect.rollback_command, e)}>copy</button>
                            </div>
                          </div>
                          <div>
                            <div className="s-sect-lbl">Fix suggestion</div>
                            <div className="fix-pill">{suspect.fix_suggestion}</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <footer>
                <span className="ft-l">GitBlame AI</span>
                <span className="ft-r">llama3.2 · ChromaDB · local inference</span>
              </footer>
            </>
          )}
        </div>
      } />
      <Route path="/callback" element={<Callback />} />
    </Routes>
  )
}

export default App