import React from "react";
import { motion } from "framer-motion";

// Import project images (make sure these files exist in your public folder)
import BrainImg from "/brain.jpg";
import RobotImg from "/robot.jpg";
import FutureImg from "/future.jpg";

const projects = [
  {
    img: BrainImg,
    title: "Futuristic Human-AI Interaction",
    description:
      "JARVIS merges voice commands, gesture recognition, and intelligent automation to offer a truly sci-fi-inspired user experience. It transforms everyday computing into a hands-free, intuitive process.",
  },
  {
    img: RobotImg,
    title: "Powerful Technical Architecture",
    description:
      "Built on a three-layer system—Perception, Cognition, and Action—JARVIS uses OpenCV, MediaPipe, PyAutoGUI, and GPT to deliver real-time voice and gesture control, smart automation, and contextual responses.",
  },
  {
    img: FutureImg,
    title: "Future-Ready & Accessible",
    description:
      "With features like mood detection, voiceprint authentication, and smart home integration, JARVIS is designed for inclusivity, productivity, and innovation—paving the way for the future of spatial and assistive computing.",
  },
];

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.5,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 50 },
  show: {
    opacity: 1,
    y: 0,
    transition: {
      type: "spring",
      stiffness: 100,
      damping: 12,
    },
  },
};

const AboutProject = () => {
  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={container}
      className="min-h-screen bg-gradient-to-b from-gray-950 to-black text-white px-4 py-16 overflow-hidden"
    >
      <div className="max-w-7xl mx-auto pt-6 sm:pt-20 lg:pt-20">
        {/* Header */}
        <motion.h1
          className="text-center text-4xl sm:text-5xl font-extrabold bg-gradient-to-r from-cyan-400 to-blue-600 text-transparent bg-clip-text mb-6 sm:mb-8"
          variants={item}
        >
          🚀 JARVIS Projects Portfolio
        </motion.h1>
        <motion.p
          className="text-center text-gray-400 mb-10 sm:mb-12 text-base sm:text-lg max-w-3xl mx-auto px-4"
          variants={item}
        >
          Explore futuristic data visualizations and smart tech interfaces.
        </motion.p>

        {/* Project Cards Section */}
        <motion.div
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 sm:gap-10 mb-16 sm:mb-20 px-4 sm:px-0"
          variants={container}
        >
          {projects.map((project, index) => (
            <motion.div
              key={index}
              variants={item}
              whileHover={{ scale: 1.03 }}
              className="bg-black/60 border border-gray-800 rounded-2xl overflow-hidden backdrop-blur-xl shadow-2xl hover:shadow-blue-800/30 transition duration-300"
            >
              <div className="h-48 sm:h-52 overflow-hidden relative">
                <img
                  src={project.img}
                  alt={project.title}
                  className="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
                  loading="lazy"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-80" />
              </div>
              <div className="p-5 sm:p-6 space-y-3">
                <h3 className="text-lg sm:text-xl font-semibold text-cyan-300">
                  {project.title}
                </h3>
                <p className="text-xs sm:text-sm text-gray-400">{project.description}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Detailed Project Description */}
        <motion.div 
          className="space-y-6 sm:space-y-8 text-base sm:text-lg leading-relaxed px-4 sm:px-8"
          variants={item}
        >
          <motion.h2 className="text-2xl sm:text-3xl font-bold text-cyan-400">
            🧠 JARVIS: Next-Gen Multimodal AI Assistant
          </motion.h2>

          <p className="text-sm sm:text-base">
            JARVIS is an ambitious AI-driven interaction system combining voice recognition, gesture control, and smart automation to make computing seamless and intuitive.
          </p>

          <h3 className="text-xl sm:text-2xl font-semibold text-blue-400">Technical Architecture</h3>
          <ul className="list-disc list-inside space-y-2 text-sm sm:text-base">
            <li><strong>Perception Layer:</strong> Voice interface, MediaPipe hand tracking, webcam analysis</li>
            <li><strong>Cognitive Layer:</strong> GPT-3.5 NLP, Wolfram Alpha integration, decision engine</li>
            <li><strong>Action Layer:</strong> PyAutoGUI control, smart home readiness, voice + visual feedback</li>
          </ul>

          <h3 className="text-xl sm:text-2xl font-semibold text-blue-400">Core Features</h3>
          <ul className="list-disc list-inside space-y-2 text-sm sm:text-base">
            <li><strong>Voice Control:</strong> Wake word, context-aware commands, GPT integration</li>
            <li><strong>Gesture Interface:</strong> Cursor/volume/brightness control via hand gestures</li>
            <li><strong>Automation:</strong> Smart routines, predictive triggers</li>
            <li><strong>Security:</strong> Voiceprint auth, gesture-based locking</li>
          </ul>

          <h3 className="text-xl sm:text-2xl font-semibold text-blue-400">Applications</h3>
          <p className="text-sm sm:text-base">
            JARVIS boosts productivity, assists disabled users, and acts as a powerful educational and automation tool.
          </p>

          <h3 className="text-xl sm:text-2xl font-semibold text-blue-400">Future Roadmap</h3>
          <ul className="list-disc list-inside space-y-2 text-sm sm:text-base">
            <li>Emotion Recognition</li>
            <li>AR/HoloLens Support</li>
            <li>Edge AI with offline models</li>
            <li>Custom Skill Marketplace</li>
          </ul>

          <h3 className="text-xl sm:text-2xl font-semibold text-blue-400">Impact & Innovation</h3>
          <p className="text-sm sm:text-base">
            JARVIS redefines HCI by enabling spatial, hands-free, and adaptive control—setting a foundation for the future of immersive computing.
          </p>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default AboutProject