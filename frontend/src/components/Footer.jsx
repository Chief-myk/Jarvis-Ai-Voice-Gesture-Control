import React from "react";
import { FaHeart, FaCode } from "react-icons/fa";
import { motion } from "framer-motion";

const Footer = () => {
  return (
    <motion.footer
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, delay: 0.2, type: "spring" }}
      className="w-full bg-black/70 text-white backdrop-blur-md shadow-inner border-t border-cyan-500/20"
    >
      <div className="max-w-7xl mx-auto py-6 px-4 flex flex-col sm:flex-row items-center justify-between">
        <div className="text-center sm:text-left text-sm sm:text-base flex items-center gap-2">
          <FaCode className="text-cyan-400 animate-pulse" />
          <span className="text-gray-300 hover:text-cyan-400 transition-colors duration-300">
            Built with passion and precision by <strong className="text-white">Team Innovators</strong>
          </span>
          <FaHeart className="text-red-500 animate-bounce" />
        </div>

        <div className="mt-4 sm:mt-0">
          <span className="text-xs text-gray-500 hover:text-cyan-400 transition duration-300">
            © {new Date().getFullYear()} All rights reserved.
          </span>
        </div>
      </div>
    </motion.footer>
  );
};

export default Footer;
