import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import { RouterProvider, Route } from "react-router";

import router from '@/routes';

// Styles
import './index.css'

// I18n
import '@/locales'

// Firebase
import '@/firebase';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
