import { useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'

function Callback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  useEffect(() => {
    const code = searchParams.get('code')
    if (!code) return

    fetch(`http://localhost:8000/auth/github/callback?code=${code}`)
      .then(response => response.json())
      .then(data => {
        if (data.access_token) {
          localStorage.setItem('github_token', data.access_token)
          navigate('/')
        }
      })
  }, [])

  return (
    <div>
      <h1>Logging you in...</h1>
    </div>
  )
}

export default Callback