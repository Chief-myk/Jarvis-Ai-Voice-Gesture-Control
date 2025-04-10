import { useEffect, useState } from 'react';
import axios from 'axios';
import Loader from './components/Loader';
import Navbar from "./components/Navbar";
import Footer from './components/Footer';
import Home from "./components/Home";
import AboutDevelopers from './components/AboutDevelopers';
import AboutProject from './components/AboutProject';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import './App.css';

// Configure axios to use the Flask backend URL
const flaskBaseURL = 'http://localhost:5000';
axios.defaults.baseURL = flaskBaseURL;

function App() {
  const [loading, setLoading] = useState(true);
  const [systemStatus, setSystemStatus] = useState({
    gestureActive: false,
    voiceActive: false,
    cameraStatus: false
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 1500);
    fetchSystemStatus();
    return () => clearTimeout(timer);
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const response = await axios.get('/api/system_status');
      setSystemStatus({
        gestureActive: response.data.gestureActive,
        voiceActive: response.data.voiceActive,
        cameraStatus: response.data.cameraStatus
      });
      setError(null);
    } catch (error) {
      console.error('Error fetching system status:', error);
      setError('Failed to connect to the JARVIS system. Please ensure the backend is running.');
    }
  };

  const toggleGestureControl = async () => {
    try {
      const response = await axios.post('/api/toggle_gestures', {
        enable: !systemStatus.gestureActive
      });
      
      if (response.data.status === 'success') {
        setSystemStatus(prev => ({
          ...prev,
          gestureActive: response.data.isActive,
          cameraStatus: response.data.isActive
        }));
        setError(null);
      }
    } catch (error) {
      console.error('Error toggling gesture control:', error);
      setError('Failed to toggle gesture control. Please try again.');
    }
  };

  const toggleVoiceControl = async () => {
    try {
      const response = await axios.post('/api/toggle_voice', {
        enable: !systemStatus.voiceActive
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.data.status === 'success') {
        setSystemStatus(prev => ({
          ...prev,
          voiceActive: response.data.isActive
        }));
      }
    } catch (error) {
      console.error('Error toggling voice control:', error);
    }
  };

  const sendVoiceCommand = async (command) => {
    try {
      await axios.post('/api/send_command', {
        command: command
      });
      setError(null);
    } catch (error) {
      console.error('Error sending command:', error);
      setError('Failed to send command to JARVIS.');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <Loader />
      </div>
    );
  }

  return (
    <Router>
      <div className="font-sans flex flex-col bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white min-h-screen transition-colors duration-300">
        <Navbar 
          systemStatus={systemStatus}
          toggleGestureControl={toggleGestureControl}
          toggleVoiceControl={toggleVoiceControl}
          error={error}
        />
        <main className="flex-grow transition-all duration-300">
          {error && (
            <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4" role="alert">
              <p>{error}</p>
            </div>
          )}
          <Routes>
            <Route path="/" element={
              <Home 
                systemStatus={systemStatus}
                toggleGestureControl={toggleGestureControl}
                toggleVoiceControl={toggleVoiceControl}
                sendVoiceCommand={sendVoiceCommand}
              />
            } />
            <Route path="/about_developers" element={<AboutDevelopers />} />
            <Route path="/about_project" element={<AboutProject />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;