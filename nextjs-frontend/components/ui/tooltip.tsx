"use client";

import React, { useState } from "react";
import {
  motion,
  useTransform,
  AnimatePresence,
  useMotionValue,
  useSpring,
} from "motion/react";

interface TooltipProps {
  content: string;
  children: React.ReactNode;
  position?: "top" | "bottom" | "left" | "right";
  delay?: number;
}

export const Tooltip = ({
  content,
  children,
  position = "top",
  delay = 0,
}: TooltipProps) => {
  const [isHovered, setIsHovered] = useState(false);
  const springConfig = { stiffness: 100, damping: 5 };
  const x = useMotionValue(0);

  // rotate the tooltip
  const rotate = useSpring(useTransform(x, [-100, 100], [-8, 8]), springConfig);

  // translate the tooltip
  const translateX = useSpring(
    useTransform(x, [-100, 100], [-20, 20]),
    springConfig,
  );

  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    const rect = (event.target as HTMLElement).getBoundingClientRect();
    const halfWidth = rect.width / 2;
    x.set(event.nativeEvent.offsetX - halfWidth);
  };

  const getPositionClasses = () => {
    switch (position) {
      case "top":
        return "-top-12 left-1/2 -translate-x-1/2";
      case "bottom":
        return "-bottom-12 left-1/2 -translate-x-1/2";
      case "left":
        return "top-1/2 -left-3 -translate-x-full -translate-y-1/2";
      case "right":
        return "top-1/2 -right-3 translate-x-full -translate-y-1/2";
      default:
        return "-top-12 left-1/2 -translate-x-1/2";
    }
  };

  const getArrowClasses = () => {
    switch (position) {
      case "top":
        return "absolute top-full left-1/2 -translate-x-1/2 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900 dark:border-t-gray-100";
      case "bottom":
        return "absolute bottom-full left-1/2 -translate-x-1/2 border-l-4 border-r-4 border-b-4 border-transparent border-b-gray-900 dark:border-b-gray-100";
      case "left":
        return "absolute left-full top-1/2 -translate-y-1/2 border-t-4 border-b-4 border-l-4 border-transparent border-l-gray-900 dark:border-l-gray-100";
      case "right":
        return "absolute right-full top-1/2 -translate-y-1/2 border-t-4 border-b-4 border-r-4 border-transparent border-r-gray-900 dark:border-r-gray-100";
      default:
        return "absolute top-full left-1/2 -translate-x-1/2 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900 dark:border-t-gray-100";
    }
  };

  return (
    <div
      className="relative inline-block"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onMouseMove={handleMouseMove}
    >
      {children}
      <AnimatePresence mode="wait">
        {isHovered && (
          <motion.div
            initial={{
              opacity: 0,
              y: position === "bottom" ? -10 : 10,
              scale: 0.8,
            }}
            animate={{
              opacity: 1,
              y: 0,
              scale: 1,
              transition: {
                type: "spring",
                stiffness: 260,
                damping: 20,
                delay: delay / 1000,
              },
            }}
            exit={{
              opacity: 0,
              y: position === "bottom" ? -10 : 10,
              scale: 0.8,
            }}
            style={{
              translateX:
                position === "top" || position === "bottom" ? translateX : 0,
              rotate: position === "top" || position === "bottom" ? rotate : 0,
            }}
            className={`absolute z-50 ${getPositionClasses()}`}
          >
            <div className="relative rounded-lg bg-gray-900 px-3 py-2 text-sm text-white shadow-lg dark:bg-gray-100 dark:text-gray-900">
              <div className="relative z-10 whitespace-nowrap font-medium">
                {content}
              </div>
              <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-cyan-500/20" />
              <div className={getArrowClasses()} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
