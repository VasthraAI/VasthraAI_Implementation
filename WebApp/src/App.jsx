import React from 'react'
import Navbar from './components/Navbar'
import UploadPage from './components/Upload'
import ViewDesigns from './components/ViewDesigns';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/view-designs" element={<ViewDesigns />} />
      </Routes>
    </Router>
  );
}

export default App