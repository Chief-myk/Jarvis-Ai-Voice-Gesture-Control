import { useEffect, useState } from 'react'
import Loader from './components/Loader'
import "./App.css";
import Navbar from "./components/Navbar";
import Footer from './components/Footer';
import Home from "./components/Home";
import About_devlopers from './components/About_devlopers';
import About_project from './components/About_project';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

function App() {
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 1500);
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <Loader />
      </div>
    )
  }

  return (
 
      <Router>
        <div className="font-sans flex flex-col bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white min-h-screen transition-colors duration-300">
          <Navbar />
          <main className="flex-grow transition-all duration-300">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/about_devlopers" element={<About_devlopers />} />
              <Route path="/about_project" element={<About_project />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
   
  );
}

export default App;
