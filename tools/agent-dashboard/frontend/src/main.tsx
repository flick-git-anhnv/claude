import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import './styles/tokens.css'
import { installMockInterceptor } from './api/interceptor'
import { WsProvider } from './contexts/WsContext'
import { ToastProvider } from './contexts/ToastContext'
import App from './App'

// Install mock fetch interceptor BEFORE first render (dev only)
installMockInterceptor()

const root = document.getElementById('root')
if (!root) throw new Error('Root element #root not found')

createRoot(root).render(
  <StrictMode>
    <HashRouter>
      <ToastProvider>
        <WsProvider>
          <App />
        </WsProvider>
      </ToastProvider>
    </HashRouter>
  </StrictMode>
)
