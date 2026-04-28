import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { NewIdea } from './pages/NewIdea'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/ideas/new" element={<NewIdea />} />
      </Routes>
    </BrowserRouter>
  )
}
