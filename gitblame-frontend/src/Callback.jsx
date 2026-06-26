import { useEffect, useRef } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'

const API = import.meta.env.VITE_API_URL

function Callback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const hasRun = useRef(false)

  useEffect(() => {
    if (hasRun.current) return
    hasRun.current = true

    const code = searchParams.get('code')
    console.log('Code from URL:', code)
    console.log('API URL:', API)
    
    if (!code) {
      console.log('No code found!')
      return
    }

    fetch(`${API}/auth/github/callback?code=${code}`)
      .then(response => {
        console.log('Response status:', response.status)
        return response.json()
      })
      .then(data => {
        console.log('Data received:', data)
        if (data.access_token) {
          localStorage.setItem('github_token', data.access_token)
          navigate('/')
        } else {
          console.log('No access token in response!')
        }
      })
      .catch(err => {
        console.log('Fetch error:', err)
      })
  }, [])

  return (
    <div>
      <h1>Logging you in...</h1>
    </div>
  )
}

export default Callback