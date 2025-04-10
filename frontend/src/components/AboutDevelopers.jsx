import React from "react";
import { motion } from "framer-motion";
import { FaUserSecret, FaPalette, FaBug, FaHandsHelping } from "react-icons/fa";

// Import team member images (make sure these files exist in your public folder)
import MayankImg from "/Mayank.jpg";
import SiddhiImg from "/siddhi.jpg";
import YashImg from "/yash.jpeg";
import BhavikImg from "/bhavik.jpeg";

const team = [
  {
    name: "Mayank Mittal",
    role: "Team Leader",
    responsibility: "Project Architect & AI Integration",
    description:
      "Architecting the core system, overseeing vision execution, and ensuring technical excellence.",
    tagline: "Turning Vision into Reality",
    img: MayankImg,
    icon: <FaUserSecret className="text-cyan-400 text-3xl" />,
  },
  {
    name: "Siddhi Sharma",
    role: "UI/UX Designer",
    responsibility: "Visual Identity & Front-End Magic",
    description:
      "Designing intuitive, futuristic interfaces that merge style with smooth user experiences.",
    tagline: "Designing the Future, One Pixel at a Time",
    img: SiddhiImg,
    icon: <FaPalette className="text-pink-400 text-3xl" />,
  },
  {
    name: "Yash Chopra",
    role: "QA & Testing",
    responsibility: "Quality Control & Debugging",
    description:
      "Performing quality checks, debugging, and ensuring stability across the JARVIS ecosystem.",
    tagline: "Precision in Every Line of Code",
    img: YashImg,
    icon: <FaBug className="text-yellow-400 text-3xl" />,
  },
  {
    name: "Bhavik",
    role: "Support Engineer",
    responsibility: "Tech Support & Resource Management",
    description:
      "Ensuring backend integration and assisting with feature enhancements and deployment.",
    tagline: "Behind the Scenes, Ahead of the Curve",
    img: BhavikImg,
    icon: <FaHandsHelping className="text-green-400 text-3xl" />,
  },
];

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
      delayChildren: 0.4,
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

const AboutDevelopers = () => {
  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={container}
      className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black text-white px-6 py-20 overflow-hidden"
    >
      <div className="max-w-7xl mx-auto">
        <motion.h1
          className="text-center text-4xl sm:text-5xl font-extrabold bg-gradient-to-r from-cyan-400 to-blue-600 text-transparent bg-clip-text mb-8 sm:mb-10"
          variants={item}
        >
          🧠 Meet The Minds Behind JARVIS
        </motion.h1>
        <motion.p
          className="text-center text-gray-400 mb-12 sm:mb-20 text-base sm:text-lg max-w-2xl mx-auto px-4"
          variants={item}
        >
          A dedicated team transforming futuristic ideas into real-time AI interactions.
        </motion.p>

        <motion.div
          className="grid gap-8 sm:gap-10 md:grid-cols-2 lg:grid-cols-4 px-4 sm:px-0"
          variants={container}
        >
          {team.map((member, idx) => (
            <motion.div
              key={idx}
              variants={item}
              whileHover={{ scale: 1.03 }}
              className="bg-white/5 backdrop-blur-xl rounded-3xl shadow-lg overflow-hidden p-5 sm:p-6 relative border border-white/10 hover:border-cyan-400/50 transition-all duration-300"
            >
              <div className="w-full h-48 overflow-hidden rounded-xl mb-4">
                <img
                  src={member.img}
                  alt={member.name}
                  className="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
                  loading="lazy"
                />
              </div>
              <div className="text-left space-y-2">
                <h3 className="text-lg sm:text-xl font-bold text-cyan-300 flex items-center gap-2">
                  {member.icon} {member.name}
                </h3>
                <p className="text-xs sm:text-sm text-gray-300 font-medium">{member.role}</p>
                <p className="text-xs sm:text-sm text-gray-400 italic">{member.responsibility}</p>
                <p className="text-xs text-gray-500 pt-2">{member.description}</p>
                <p className="text-xs sm:text-[13px] text-gray-400 italic animate-pulse mt-2">
                  "{member.tagline}"
                </p>
              </div>
              <div className="absolute -bottom-3 left-1/2 transform -translate-x-1/2 w-2/3 h-1 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500"></div>
            </motion.div>
          ))}
        </motion.div>

        <motion.div
          variants={item}
          className="mt-16 sm:mt-24 text-center text-gray-400 max-w-3xl mx-auto px-4"
        >
          <h2 className="text-2xl sm:text-3xl font-semibold text-white mb-3 sm:mb-4">🛠️ Our Mission</h2>
          <p className="text-sm sm:text-base text-gray-400">
            To build an intelligent system that adapts to human interaction naturally. We believe in pushing the
            boundaries of AI and making tech feel magical yet real.
          </p>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default AboutDevelopers;