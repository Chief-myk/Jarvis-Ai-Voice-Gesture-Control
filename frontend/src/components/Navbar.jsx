// components/Navbar.js
import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { FaRobot } from "react-icons/fa";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setIsOpen(false); // Close on route change
  }, [location.pathname]);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navVariants = {
    hidden: { y: -100 },
    visible: { y: 0, transition: { type: "spring", stiffness: 100, damping: 10 } }
  };

  return (
    <motion.nav
      variants={navVariants}
      initial="hidden"
      animate="visible"
      className={`w-full fixed top-0 z-50 transition-all duration-300 ${
        scrolled ? "bg-black/70 shadow-xl backdrop-blur-md" : "bg-black/50 backdrop-blur-sm"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex justify-between items-center">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 text-cyan-400 font-bold text-2xl hover:scale-105 transition-transform duration-300">
          <FaRobot className="text-3xl animate-pulse" />
          JARVIS
        </Link>

        {/* Desktop Menu */}
        <ul className="hidden md:flex space-x-6 text-white font-medium tracking-wide text-lg">
          {navLinks.map((item) => (
            <NavItem key={item.path} item={item} currentPath={location.pathname} />
          ))}
        </ul>

        {/* Hamburger Button */}
        <div className="md:hidden z-50">
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="text-white p-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            aria-label="Toggle menu"
          >
            {isOpen ? (
              <motion.div initial={{ rotate: 0 }} animate={{ rotate: 90 }}>
                <svg className="w-8 h-8 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </motion.div>
            ) : (
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ x: "-100%" }}
            animate={{ x: 0 }}
            exit={{ x: "-100%" }}
            transition={{ type: "spring", stiffness: 100, damping: 15 }}
            className="md:hidden fixed top-0 left-0 w-full h-screen bg-black/90 backdrop-blur-lg flex flex-col justify-center items-center space-y-8 text-white text-2xl font-semibold z-40"
          >
            {navLinks.map((item) => (
              <MobileNavItem
                key={item.path}
                item={item}
                currentPath={location.pathname}
                onClick={() => setIsOpen(false)}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
};

const navLinks = [
  { path: "/", label: "Home" },
  { path: "/about_project", label: "About Project" },
  { path: "/about_devlopers", label: "About Developers" },
];

const NavItem = ({ item, currentPath }) => (
  <motion.li
    whileHover={{ scale: 1.1 }}
    transition={{ type: "spring", stiffness: 300 }}
  >
    <Link
      to={item.path}
      className={`relative px-3 py-2 hover:text-cyan-400 transition-all duration-300 ${
        currentPath === item.path ? "text-cyan-400" : ""
      }`}
    >
      {item.label}
      <span className={`absolute left-0 bottom-0 w-full h-0.5 bg-cyan-400 transform transition-transform duration-300 scale-x-0 hover:scale-x-100 ${currentPath === item.path ? "scale-x-100" : ""}`}></span>
    </Link>
  </motion.li>
);

const MobileNavItem = ({ item, currentPath, onClick }) => (
  <motion.li whileTap={{ scale: 0.95 }}>
    <Link
      to={item.path}
      onClick={onClick}
      className={`block px-6 py-3 rounded-lg w-64 text-center ${
        currentPath === item.path
          ? "bg-cyan-600 text-white shadow-md"
          : "hover:bg-cyan-700/20 text-white transition"
      }`}
    >
      {item.label}
    </Link>
  </motion.li>
);

export default Navbar;
