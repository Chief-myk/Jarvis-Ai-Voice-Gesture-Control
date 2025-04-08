import React from "react";
import { motion } from "framer-motion";
import { FaUserSecret, FaPalette, FaBug, FaHandsHelping } from "react-icons/fa";

const team = [
  {
    name: "Mayank Mittal",
    role: "Team Leader",
    responsibility: "Project Architect & AI Integration",
    description:
      "Architecting the core system, overseeing vision execution, and ensuring technical excellence.",
    tagline: "Turning Vision into Reality",
    img: "/Mayank.jpg",
    icon: <FaUserSecret className="text-cyan-400 text-3xl" />,
  },
  {
    name: "Siddhi Sharma",
    role: "UI/UX Designer",
    responsibility: "Visual Identity & Front-End Magic",
    description:
      "Designing intuitive, futuristic interfaces that merge style with smooth user experiences.",
    tagline: "Designing the Future, One Pixel at a Time",
    img: "/siddhi.jpg",
    icon: <FaPalette className="text-pink-400 text-3xl" />,
  },
  {
    name: "Yash Chopra",
    role: "QA & Testing",
    responsibility: "Quality Control & Debugging",
    description:
      "Performing quality checks, debugging, and ensuring stability across the JARVIS ecosystem.",
    tagline: "Precision in Every Line of Code",
    img: "/yash.jpeg",
    icon: <FaBug className="text-yellow-400 text-3xl" />,
  },
  {
    name: "Bhavik",
    role: "Support Engineer",
    responsibility: "Tech Support & Resource Management",
    description:
      "Ensuring backend integration and assisting with feature enhancements and deployment.",
    tagline: "Behind the Scenes, Ahead of the Curve",
    img: "/bhavik.jpeg",
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

const About_developers = () => {
  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={container}
      className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black text-white px-6 py-20 overflow-hidden"
    >
      <div className="max-w-7xl mx-auto">
        <motion.h1
          className="text-center text-5xl font-extrabold bg-gradient-to-r from-cyan-400 to-blue-600 text-transparent bg-clip-text mb-10"
          variants={item}
        >
          🧠 Meet The Minds Behind JARVIS
        </motion.h1>
        <motion.p
          className="text-center text-gray-400 mb-20 text-lg max-w-2xl mx-auto"
          variants={item}
        >
          A dedicated team transforming futuristic ideas into real-time AI interactions.
        </motion.p>

        <motion.div
          className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4"
          variants={container}
        >
          {team.map((member, idx) => (
            <motion.div
              key={idx}
              variants={item}
              whileHover={{ scale: 1.05, rotate: 1 }}
              className="bg-white/5 backdrop-blur-xl rounded-3xl shadow-lg overflow-hidden p-6 relative border border-white/10 hover:border-cyan-400 transition-all duration-300"
            >
              <img
                src={member.img}
                alt={member.name}
                className="w-full h-48 object-cover rounded-xl mb-4 border border-gray-700 transition-transform duration-300 hover:scale-105"
              />
              <div className="text-left space-y-2">
                <h3 className="text-xl font-bold text-cyan-300 flex items-center gap-2">
                  {member.icon} {member.name}
                </h3>
                <p className="text-sm text-gray-300 font-medium">{member.role}</p>
                <p className="text-sm text-gray-400 italic">{member.responsibility}</p>
                <p className="text-xs text-gray-500 pt-2">{member.description}</p>
                <p className="text-[13px] text-gray-400 italic animate-pulse">
                  "{member.tagline}"
                </p>
              </div>
              <div className="absolute -bottom-3 left-1/2 transform -translate-x-1/2 w-2/3 h-1 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500"></div>
            </motion.div>
          ))}
        </motion.div>

        <motion.div
          variants={item}
          className="mt-24 text-center text-gray-400 max-w-3xl mx-auto"
        >
          <h2 className="text-3xl font-semibold text-white mb-4">🛠️ Our Mission</h2>
          <p className="text-base text-gray-400">
            To build an intelligent system that adapts to human interaction naturally. We believe in pushing the
            boundaries of AI and making tech feel magical yet real.
          </p>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default About_developers;
