"use client";

import { motion, useReducedMotion } from "motion/react";
import type { ReactNode } from "react";

type RevealProps = {
  as?: "div" | "li";
  children: ReactNode;
  className?: string;
  delay?: number;
  id?: string;
};

export function Reveal({ as = "div", children, className, delay = 0, id }: RevealProps) {
  const reducedMotion = useReducedMotion();
  const motionProps = {
    className,
    "data-reveal": "",
    id,
    ...(reducedMotion
      ? { initial: false }
      : {
          initial: { opacity: 0, y: 24 },
          transition: { delay, duration: 0.55, ease: [0.22, 1, 0.36, 1] as const },
          viewport: { amount: 0.15, once: true },
          whileInView: { opacity: 1, y: 0 },
        }),
  };

  if (as === "li") {
    return <motion.li {...motionProps}>{children}</motion.li>;
  }

  return <motion.div {...motionProps}>{children}</motion.div>;
}
