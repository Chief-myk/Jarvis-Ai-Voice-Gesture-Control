import React from 'react';
import { motion } from "framer-motion";
import { FaRobot, FaMicrochip, FaCogs } from 'react-icons/fa';
import { GiMechanicalArm } from 'react-icons/gi';

const Home = ({ systemStatus, toggleGestureControl, toggleVoiceControl }) => {
  const floatingVariants = {
    initial: { y: -10 },
    animate: {
      y: [0, -15, 0],
      transition: { duration: 4, repeat: Infinity, ease: "easeInOut" }
    }
  };

  const staggerContainer = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.15 }
    }
  };

  const staggerItem = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  const features = [
    "🎙 Voice Commands like 'Open Google', 'Play music'",
    "🖐 Gesture-controlled mouse, click, and volume",
    "🤖 AI integration with ChatGPT and Wolfram Alpha",
    "⚙ Automate tasks: screenshots, screen record, system control",
    "🌤 Real-time info: weather, news, calculations",
    "🧠 Built with Python, OpenCV, MediaPipe, PyAudio"
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-indigo-800 to-black text-white flex flex-col items-center justify-center px-6 relative overflow-hidden">
      {/* Decorative Elements */}
      <div className="absolute top-20 right-20 opacity-5">
        <GiMechanicalArm className="text-blue-500 text-9xl" />
      </div>
      <div className="absolute bottom-20 left-20 opacity-5">
        <FaCogs className="text-blue-500 text-9xl" />
      </div>
      <div className="absolute top-1/3 left-1/4 opacity-5">
        <FaRobot className="text-blue-500 text-9xl" />
      </div>

      {/* Floating particles */}
      <div className="absolute inset-0 z-0 overflow-hidden">
        {[...Array(25)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full bg-white opacity-10"
            style={{
              width: `${Math.random() * 10 + 5}px`,
              height: `${Math.random() * 10 + 5}px`,
              top: `${Math.random() * 100}%`,
              left: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, Math.random() * 100 - 50],
              x: [0, Math.random() * 100 - 50],
              opacity: [0.1, 0.2, 0.1]
            }}
            transition={{
              duration: Math.random() * 10 + 10,
              repeat: Infinity,
              repeatType: "reverse",
              delay: Math.random() * 5
            }}
          />
        ))}
      </div>

      {/* Main Content */}
      <div className="max-w-5xl pt-24 sm:pt-32 lg:pt-20 text-center z-10">
        <motion.h1
          className="text-4xl sm:text-5xl md:text-6xl font-extrabold mb-6 flex justify-center items-center bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500"
          variants={floatingVariants}
          initial="initial"
          animate="animate"
        >
          <FaRobot className="mr-4" />
          JARVIS: AI Voice & Gesture Control
          <FaMicrochip className="ml-4" />
        </motion.h1>

        <motion.p
          className="text-lg sm:text-xl mb-10 text-indigo-200"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          A futuristic assistant combining voice, gesture, and AI for seamless control.
        </motion.p>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          className="grid gap-6 text-left sm:grid-cols-2 lg:grid-cols-2"
        >
          {/* Features */}
          {features.map((feature, idx) => (
            <motion.div
              key={idx}
              variants={staggerItem}
              className="bg-indigo-900 bg-opacity-40 rounded-2xl p-4 shadow-lg border border-indigo-700 hover:scale-105 transform transition duration-300"
            >
              {feature}
            </motion.div>
          ))}
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-6"
          initial={{ opacity: 0, scale: 0.8 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ type: "spring", stiffness: 100, damping: 8, delay: 0.2 }}
          viewport={{ once: true }}
        >
          <button 
            onClick={() => {
              toggleVoiceControl();
              toggleGestureControl();
            }}
            className={`bg-gradient-to-r text-lg font-semibold py-3 px-8 rounded-2xl shadow-md transition transform hover:scale-105 ${
              systemStatus.voiceActive && systemStatus.gestureActive
                ? "from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-500"
                : "from-cyan-500 to-blue-600 hover:from-blue-600 hover:to-cyan-500"
            } text-white`}
          >
            {systemStatus.voiceActive && systemStatus.gestureActive ? "JARVIS Active" : "Enable JARVIS"}
          </button>
          <button 
            onClick={() => {
              if (systemStatus.voiceActive) toggleVoiceControl();
              if (systemStatus.gestureActive) toggleGestureControl();
            }}
            className={`bg-gradient-to-r text-lg font-semibold py-3 px-8 rounded-2xl shadow-md transition transform hover:scale-105 ${
              !systemStatus.voiceActive && !systemStatus.gestureActive
                ? "from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-500"
                : "from-red-500 to-pink-600 hover:from-pink-600 hover:to-red-500"
            } text-white`}
          >
            {!systemStatus.voiceActive && !systemStatus.gestureActive ? "JARVIS Inactive" : "Disable JARVIS"}
          </button>
        </motion.div>
      </div>
    </div>
  );
};

export default Home;