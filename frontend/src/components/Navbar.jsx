import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { FaRobot } from "react-icons/fa";
import { GiHamburgerMenu } from "react-icons/gi";
import { IoClose } from "react-icons/io5";

const Navbar = ({ systemStatus, toggleGestureControl, toggleVoiceControl, error }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  // Close mobile menu on route change
  useEffect(() => {
    setIsOpen(false);
  }, [location.pathname]);

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Animation variants
  const navVariants = {
    hidden: { y: -100 },
    visible: { 
      y: 0, 
      transition: { 
        type: "spring", 
        stiffness: 100, 
        damping: 10 
      } 
    }
  };

  // Navigation links
  const navLinks = [
    { path: "/", label: "Home" },
    { path: "/about_project", label: "About Project" },
    { path: "/about_developers", label: "About Developers" },
  ];

  return (
    <motion.nav
      variants={navVariants}
      initial="hidden"
      animate="visible"
      className={`w-full fixed top-0 z-50 transition-all duration-300 ${
        scrolled 
          ? "bg-gray-900/90 shadow-xl backdrop-blur-md" 
          : "bg-gray-900/50 backdrop-blur-sm"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex justify-between items-center">
        {/* Logo */}
        <Link 
          to="/" 
          className="flex items-center gap-2 text-cyan-400 font-bold text-2xl hover:scale-105 transition-transform duration-300"
          aria-label="Home"
        >
          <FaRobot className="text-3xl animate-pulse" />
          JARVIS
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-8">
          <ul className="flex space-x-6 text-white font-medium tracking-wide text-lg">
            {navLinks.map((item) => (
              <NavItem 
                key={item.path} 
                item={item} 
                currentPath={location.pathname} 
              />
            ))}
          </ul>
          
          {/* System Controls */}
          <div className="flex items-center gap-4 ml-6">
            <button
              onClick={toggleVoiceControl}
              className={`px-4 py-2 rounded-md font-medium transition-all ${
                systemStatus.voiceActive
                  ? "bg-green-600 hover:bg-green-700 text-white"
                  : "bg-gray-700 hover:bg-gray-600 text-gray-200"
              }`}
              aria-label={systemStatus.voiceActive ? "Disable voice control" : "Enable voice control"}
            >
              Voice {systemStatus.voiceActive ? "ON" : "OFF"}
            </button>
            <button
              onClick={toggleGestureControl}
              className={`px-4 py-2 rounded-md font-medium transition-all ${
                systemStatus.gestureActive
                  ? "bg-blue-600 hover:bg-blue-700 text-white"
                  : "bg-gray-700 hover:bg-gray-600 text-gray-200"
              }`}
              aria-label={systemStatus.gestureActive ? "Disable gesture control" : "Enable gesture control"}
            >
              Gesture {systemStatus.gestureActive ? "ON" : "OFF"}
            </button>
          </div>
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="md:hidden z-50 p-2 text-gray-200 hover:text-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 rounded-md transition-all"
          aria-label={isOpen ? "Close menu" : "Open menu"}
        >
          {isOpen ? (
            <IoClose className="w-8 h-8 text-cyan-400" />
          ) : (
            <GiHamburgerMenu className="w-8 h-8" />
          )}
        </button>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, x: "-100%" }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: "-100%" }}
            transition={{ type: "spring", stiffness: 100, damping: 15 }}
            className="md:hidden fixed inset-0 w-full h-screen bg-gray-900/95 backdrop-blur-lg flex flex-col justify-center items-center space-y-8 z-40 pt-20"
          >
            {navLinks.map((item) => (
              <MobileNavItem
                key={item.path}
                item={item}
                currentPath={location.pathname}
                onClick={() => setIsOpen(false)}
              />
            ))}
            
            {/* Mobile Controls */}
            <div className="flex flex-col gap-4 w-full px-8 mt-8">
              <button
                onClick={() => {
                  toggleVoiceControl();
                  setIsOpen(false);
                }}
                className={`w-full py-3 rounded-md font-medium text-lg ${
                  systemStatus.voiceActive
                    ? "bg-green-600 hover:bg-green-700 text-white"
                    : "bg-gray-700 hover:bg-gray-600 text-gray-200"
                }`}
              >
                Voice Control: {systemStatus.voiceActive ? "ON" : "OFF"}
              </button>
              <button
                onClick={() => {
                  toggleGestureControl();
                  setIsOpen(false);
                }}
                className={`w-full py-3 rounded-md font-medium text-lg ${
                  systemStatus.gestureActive
                    ? "bg-blue-600 hover:bg-blue-700 text-white"
                    : "bg-gray-700 hover:bg-gray-600 text-gray-200"
                }`}
              >
                Gesture Control: {systemStatus.gestureActive ? "ON" : "OFF"}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
};

// Desktop Nav Item Component
const NavItem = ({ item, currentPath }) => (
  <motion.li
    whileHover={{ scale: 1.05 }}
    whileTap={{ scale: 0.95 }}
    transition={{ type: "spring", stiffness: 300 }}
  >
    <Link
      to={item.path}
      className={`relative px-3 py-2 hover:text-cyan-400 transition-all duration-300 ${
        currentPath === item.path ? "text-cyan-400 font-semibold" : "text-gray-200"
      }`}
      aria-current={currentPath === item.path ? "page" : undefined}
    >
      {item.label}
      <span 
        className={`absolute left-0 bottom-0 w-full h-0.5 bg-cyan-400 transform transition-transform duration-300 scale-x-0 hover:scale-x-100 ${
          currentPath === item.path ? "scale-x-100" : ""
        }`}
      />
    </Link>
  </motion.li>
);

// Mobile Nav Item Component
const MobileNavItem = ({ item, currentPath, onClick }) => (
  <motion.li 
    className="w-full px-8"
    whileHover={{ scale: 1.02 }}
    whileTap={{ scale: 0.98 }}
  >
    <Link
      to={item.path}
      onClick={onClick}
      className={`block px-6 py-4 rounded-lg w-full text-center text-xl ${
        currentPath === item.path
          ? "bg-cyan-600 text-white shadow-md font-medium"
          : "hover:bg-gray-800 text-gray-200 transition"
      }`}
      aria-current={currentPath === item.path ? "page" : undefined}
    >
      {item.label}
    </Link>
  </motion.li>
);

export default Navbar;