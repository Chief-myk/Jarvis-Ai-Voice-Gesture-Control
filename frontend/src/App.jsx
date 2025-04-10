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
const flaskBaseURL = 'http://localhost:5001';
axios.defaults.baseURL = flaskBaseURL;

function App() {
  const [loading, setLoading] = useState(true);

  const [error, setError] = useState(null);
  const [recognition, setRecognition] = useState(null);
  const [commandHistory, setCommandHistory] = useState([]);

  const [systemStatus, setSystemStatus] = useState({
    gestureActive: false,
    voiceActive: false,
    cameraStatus: false,
   
});

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 1500);
    fetchSystemStatus();
    initializeVoiceRecognition();
    
    // Set up status polling
    const statusInterval = setInterval(fetchSystemStatus, 5000);
    
    return () => {
      clearTimeout(timer);
      clearInterval(statusInterval);
      if (recognition) {
        recognition.stop();
      }
    };
  }, []);

  const initializeVoiceRecognition = () => {
    // Check microphone permission first
    navigator.permissions.query({name: 'microphone'}).then(permissionStatus => {
        if (permissionStatus.state === 'granted') {
            startRecognition();
        } else {
            // Request microphone access
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(() => startRecognition())
                .catch(err => {
                    console.error('Microphone access denied:', err);
                    setError('Microphone access is required for voice commands');
                });
        }
    });

    function startRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognizer = new SpeechRecognition();
            recognizer.continuous = true;
            recognizer.interimResults = true;
            recognizer.lang = 'en-US';
            
            recognizer.onstart = () => {
                console.log("Mic active - should show in taskbar");
                setSystemStatus(prev => ({...prev, micActive: true}));
            };
            
            recognizer.onend = () => {
                if (systemStatus.voiceActive) {
                    recognizer.start();
                }
            };

            recognizer.onresult = (event) => {
                const transcript = Array.from(event.results)
                    .map(result => result[0])
                    .map(result => result.transcript)
                    .join('');
                
                if (event.results[0].isFinal && systemStatus.voiceActive) {
                    processVoiceCommand(transcript);
                }
            };

            recognizer.onerror = (event) => {
                if (event.error !== 'no-speech') {
                    setError(`Voice error: ${event.error}`);
                }
            };

            setRecognition(recognizer);
            if (systemStatus.voiceActive) {
                recognizer.start();
            }
        } else {
            setError("Speech recognition not supported in this browser");
        }
    }
};

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
      setError('Backend connection failed. Ensure the Python server is running on port 5001.');
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
      });
      
      if (response.data.status === 'success') {
        const newVoiceActive = response.data.isActive;
        setSystemStatus(prev => ({
          ...prev,
          voiceActive: newVoiceActive
        }));
        
        // Start or stop listening based on new state
        if (newVoiceActive && recognition) {
          recognition.start();
        } else if (recognition) {
          recognition.stop();
        }
        
        setError(null);
      }
    } catch (error) {
      console.error('Error toggling voice control:', error);
      if (error.response) {
        setError(error.response.data.message || 'Failed to toggle voice control');
      } else {
        setError('Network error - cannot connect to backend');
      }
    }
  };

  const processVoiceCommand = async (command) => {
    try {
      const response = await axios.post('/api/process_command', {
        command: command
      });
      
      setCommandHistory(prev => [
        ...prev,
        {
          command,
          response: response.data.message,
          timestamp: new Date().toLocaleTimeString()
        }
      ]);
      
      console.log("Command processed:", command, "Response:", response.data.message);
    } catch (error) {
      console.error('Error processing command:', error);
      setError('Failed to process voice command.');
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
                commandHistory={commandHistory}
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