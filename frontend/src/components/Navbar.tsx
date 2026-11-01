import React, { useEffect, useState } from "react";
import { Scale, Moon, Sun, Github, Building2, FileSignature, Cpu } from "lucide-react";
import { motion } from "framer-motion";
import { Badge } from "./ui/badge";

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const [isDark, setIsDark] = useState<boolean>(() => {
    return (
      localStorage.getItem("theme") === "dark" ||
      (!localStorage.getItem("theme") &&
        window.matchMedia("(prefers-color-scheme: dark)").matches)
    );
  });

  const [backendHealth, setBackendHealth] = useState<"ok" | "checking" | "offline">("checking");

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [isDark]);

  useEffect(() => {
    fetch("/health")
      .then((res) => (res.ok ? setBackendHealth("ok") : setBackendHealth("offline")))
      .catch(() => setBackendHealth("offline"));
  }, []);

  const navItems = [
    { id: "scraper", label: "eCourts Scraper", icon: Building2 },
    { id: "drafting", label: "Legal Drafting Studio", icon: FileSignature },
    { id: "architecture", label: "System Architecture", icon: Cpu },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-zinc-200/80 bg-white/80 backdrop-blur-md dark:border-zinc-800 dark:bg-zinc-950/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-lg bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900 flex items-center justify-center font-bold shadow-xs">
            <Scale className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold tracking-tight text-base sm:text-lg text-zinc-900 dark:text-zinc-50">
                VakeelAI
              </span>
              <Badge variant="outline" className="text-[10px] font-mono px-1.5 py-0">
                v1.0
              </Badge>
            </div>
            <p className="text-[11px] text-zinc-500 dark:text-zinc-400 hidden sm:block">
              District Court Scraper & Pure-Python Legal Engine
            </p>
          </div>
        </div>

        {/* Navigation Tabs with Framer Motion Animated Slider */}
        <nav className="flex items-center space-x-1 bg-zinc-100 dark:bg-zinc-900 p-1 rounded-xl border border-zinc-200/60 dark:border-zinc-800">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            const IconComponent = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`relative px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-colors select-none cursor-pointer flex items-center space-x-1.5 ${
                  isActive
                    ? "text-zinc-900 dark:text-zinc-50"
                    : "text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-200"
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="activeNavIndicator"
                    className="absolute inset-0 bg-white dark:bg-zinc-800 rounded-lg shadow-xs"
                    transition={{ type: "spring", stiffness: 450, damping: 35 }}
                  />
                )}
                <IconComponent className="relative z-10 h-3.5 w-3.5" />
                <span className="relative z-10 hidden md:inline">{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Status & Actions */}
        <div className="flex items-center space-x-2">
          {/* Backend Health Badge */}
          <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 font-mono">
            <span
              className={`h-2 w-2 rounded-full ${
                backendHealth === "ok"
                  ? "bg-emerald-500 animate-pulse"
                  : backendHealth === "checking"
                  ? "bg-amber-400"
                  : "bg-red-500"
              }`}
            />
            <span className="text-[11px] text-zinc-600 dark:text-zinc-400">
              {backendHealth === "ok" ? "FastAPI Live" : "Connecting"}
            </span>
          </div>

          {/* GitHub Link */}
          <a
            href="https://github.com/DhruvSharma19/vakeelai-legal-engine"
            target="_blank"
            rel="noreferrer"
            className="p-2 rounded-lg text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-zinc-100 dark:hover:bg-zinc-850 transition-colors"
            title="GitHub Repository"
          >
            <Github className="h-4 w-4" />
          </a>

          {/* Theme Toggle */}
          <button
            onClick={() => setIsDark(!isDark)}
            className="p-2 rounded-lg text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-zinc-100 dark:hover:bg-zinc-850 transition-colors cursor-pointer"
            title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
          >
            {isDark ? <Sun className="h-4 w-4 text-amber-400" /> : <Moon className="h-4 w-4 text-zinc-700" />}
          </button>
        </div>
      </div>
    </header>
  );
};
