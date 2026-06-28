import { useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'

const API = import.meta.env.VITE_API_URL

function Callback() {
  const [searchParams] = useSearchParams()
  const hasRun = useRef(false)

  useEffect(() => {
    if (hasRun.current) return
    hasRun.current = true

    const code = searchParams.get('code')
    if (!code) return

    fetch(`${API}/auth/github/callback?code=${code}`)
      .then(response => response.json())
      .then(data => {
        if (data.access_token) {
          localStorage.setItem('github_token', data.access_token)
          setTimeout(() => {
            window.location.href = '/'
          }, 500)
        }
      })
      .catch(err => {
        console.error('Auth error:', err)
      })
  }, [])

  return (
    <div>
      <h1>Logging you in...</h1>
    </div>
  )
}

export default Callback