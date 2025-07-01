"use client";

import { useEffect, useState } from "react";
import { motion, type Variants } from "motion/react";
import { Button } from "@/components/ui/button";
import {
  ArrowRight,
  GitBranch,
  Brain,
  Target,
  ArrowUpRight,
  Star,
} from "lucide-react";
import Image from "next/image";

interface XiuerHeroProps {
  ToDashboard: () => void;
}

export default function XiuerHero({ ToDashboard }: XiuerHeroProps) {
  const [stats, setStats] = useState({
    posts: 0,
    comments: 0,
    accuracy: 0,
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setStats((prev) => {
        const newPosts = prev.posts >= 50000 ? 50000 : prev.posts + 1250;
        const newComments =
          prev.comments >= 2800000 ? 2800000 : prev.comments + 70000;
        const newAccuracy = prev.accuracy >= 95 ? 95 : prev.accuracy + 2.5;

        if (
          newPosts === 50000 &&
          newComments === 2800000 &&
          newAccuracy === 95
        ) {
          clearInterval(interval);
        }

        return {
          posts: newPosts,
          comments: newComments,
          accuracy: newAccuracy,
        };
      });
    }, 50);

    return () => clearInterval(interval);
  }, []);

  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.3,
      },
    },
  };

  const itemVariants: Variants = {
    hidden: { y: 30, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring" as const,
        stiffness: 80,
        damping: 20,
      },
    },
  };

  const floatingAnimation = {
    y: [0, -15, 0],
    transition: {
      duration: 6,
      repeat: Infinity,
      ease: "easeInOut" as const,
    },
  };

  const badgePulse = {
    scale: [1, 1.05, 1],
    opacity: [0.9, 1, 0.9],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: "easeInOut" as const,
    },
  };

  return (
    <section className="relative flex min-h-screen w-full flex-col items-center justify-center overflow-hidden bg-gradient-to-br from-slate-950 via-black to-slate-900 py-28 text-white">
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-orange-900/20 via-transparent to-transparent"></div>

        <div className="absolute inset-0 opacity-5">
          <div className="h-full w-full bg-[linear-gradient(to_right,rgba(255,255,255,0.1)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.1)_1px,transparent_1px)] bg-[size:6rem_6rem]"></div>
        </div>

        <div className="absolute -left-40 top-20 h-80 w-80 rounded-full bg-orange-600/10 blur-[120px]"></div>
        <div className="absolute -right-40 bottom-20 h-80 w-80 rounded-full bg-amber-600/10 blur-[120px]"></div>
      </div>

      <motion.main
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="relative z-10 mx-auto flex w-full max-w-7xl flex-col items-center justify-center px-8 text-center lg:flex-row lg:text-left"
      >
        <div className="flex flex-1 flex-col items-center lg:items-start lg:pr-16">
          <motion.div
            variants={itemVariants}
            animate={badgePulse}
            className="mb-6 inline-flex items-center rounded-full border border-orange-500/20 bg-orange-500/5 px-5 py-2.5 text-sm text-orange-300"
          >
            <span className="mr-2.5 rounded-full bg-orange-500 px-2.5 py-1 text-xs font-semibold text-white">
              Beta
            </span>
            新媒体智能截流工具
          </motion.div>

          <motion.h1
            variants={itemVariants}
            className="mb-10 text-4xl font-bold leading-tight sm:text-5xl lg:text-6xl"
          >
            让数据为你
            <br />
            <span className="bg-gradient-to-r from-orange-400 via-amber-400 to-yellow-400 bg-clip-text text-transparent">
              精准截流
            </span>
          </motion.h1>

          <motion.p
            variants={itemVariants}
            className="mb-12 max-w-lg text-lg leading-relaxed text-slate-300"
          >
            通过 GitHub Actions
            自动化采集公开帖子和评论，智能分析内容变化，精准识别意向用户。
          </motion.p>

          <motion.div
            variants={itemVariants}
            className="mb-12 flex flex-wrap justify-center gap-10 lg:justify-start"
          >
            <div className="text-center">
              <p className="text-3xl font-bold text-white">
                {stats.posts.toLocaleString()}+
              </p>
              <p className="mt-1.5 text-sm text-gray-400">监控帖子</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-white">
                {stats.comments.toLocaleString()}+
              </p>
              <p className="mt-1.5 text-sm text-gray-400">分析评论</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-white">{stats.accuracy}%</p>
              <p className="mt-1.5 text-sm text-gray-400">识别准确率</p>
            </div>
          </motion.div>

          <motion.div
            variants={itemVariants}
            className="mb-10 flex flex-col gap-4 sm:flex-row"
          >
            <Button
              className="group rounded-full bg-gradient-to-r from-orange-600 to-amber-600 px-8 py-6 text-base text-white shadow-lg shadow-orange-600/25 transition-all hover:shadow-orange-600/40"
              size="lg"
              onClick={() => ToDashboard()}
            >
              开始使用
              <ArrowRight className="ml-2.5 h-4 w-4 transition-transform duration-300 group-hover:translate-x-1" />
            </Button>

            <Button
              variant="outline"
              className="rounded-full border-orange-500/30 bg-transparent px-8 py-6 text-base text-white hover:bg-orange-500/10"
              size="lg"
            >
              查看演示
            </Button>
          </motion.div>

          {/* 社会证明 */}
          <motion.div
            variants={itemVariants}
            className="mb-8 flex items-center justify-center gap-3 rounded-full border border-slate-700/50 bg-slate-800/30 px-5 py-2.5 backdrop-blur-sm lg:justify-start"
          >
            <div className="flex -space-x-2">
              {[1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  className="h-8 w-8 overflow-hidden rounded-full border-2 border-slate-700 bg-slate-800"
                >
                  <div className="h-full w-full bg-gradient-to-br from-orange-500 to-amber-600 opacity-80"></div>
                </div>
              ))}
            </div>
            <span className="text-sm text-slate-300">
              <span className="font-semibold text-white">200+</span>{" "}
              新媒体人员正在使用
            </span>
            <ArrowUpRight className="h-4 w-4 text-orange-400" />
          </motion.div>

          {/* 用户评价 */}
          <motion.div
            variants={itemVariants}
            className="mb-10 flex items-center justify-center gap-2 lg:justify-start"
          >
            <div className="flex items-center gap-1">
              {[1, 2, 3, 4, 5].map((i) => (
                <Star
                  key={i}
                  className="h-4 w-4 fill-orange-400 text-orange-400"
                />
              ))}
            </div>
            <span className="text-sm text-slate-400">
              4.9/5 来自{" "}
              <span className="font-medium text-slate-300">150+ 用户评价</span>
            </span>
          </motion.div>

          {/* 技术栈 */}
          <motion.div
            variants={itemVariants}
            className="flex flex-wrap items-center justify-center gap-3 lg:justify-start"
          >
            <span className="text-sm text-gray-400">集成技术:</span>
            <div className="flex items-center gap-2 rounded-full border border-slate-700 bg-slate-800/50 px-3 py-1.5 text-sm text-slate-300">
              <div className="h-2 w-2 rounded-full bg-orange-400"></div>
              GitHub Actions
            </div>
            <div className="flex items-center gap-2 rounded-full border border-slate-700 bg-slate-800/50 px-3 py-1.5 text-sm text-slate-300">
              <div className="h-2 w-2 rounded-full bg-amber-400"></div>
              机器学习
            </div>
            <div className="flex items-center gap-2 rounded-full border border-slate-700 bg-slate-800/50 px-3 py-1.5 text-sm text-slate-300">
              <div className="h-2 w-2 rounded-full bg-yellow-400"></div>
              数据分析
            </div>
            <div className="flex items-center gap-2 rounded-full border border-slate-700 bg-slate-800/50 px-3 py-1.5 text-sm text-slate-300">
              <div className="h-2 w-2 rounded-full bg-green-400"></div>
              +5 更多
            </div>
          </motion.div>
        </div>

        {/* 右侧图像区域 */}
        <div className="mt-16 flex flex-1 items-center justify-center lg:mt-0">
          <motion.div animate={floatingAnimation} className="relative">
            <div className="relative h-[420px] w-[420px] lg:h-[480px] lg:w-[480px]">
              <Image
                src="https://blocks.mvp-subha.me/Adobe Express - file(1).png"
                alt="Xiuer 自动化数据分析平台"
                className="h-full w-full object-contain drop-shadow-[0_0_50px_#f59e0b40]"
                width={480}
                height={480}
              />

              {/* 简化的功能提示 */}
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 1.5, type: "spring" }}
                className="absolute -left-10 top-16 rounded-lg border border-orange-500/30 bg-black/80 p-3 backdrop-blur-sm lg:-left-16"
              >
                <div className="flex items-center gap-2">
                  <GitBranch className="h-4 w-4 text-orange-400" />
                  <span className="text-sm font-medium text-orange-200">
                    自动化采集
                  </span>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 1.8, type: "spring" }}
                className="absolute -right-10 top-1/2 rounded-lg border border-amber-500/30 bg-black/80 p-3 backdrop-blur-sm lg:-right-16"
              >
                <div className="flex items-center gap-2">
                  <Brain className="h-4 w-4 text-amber-400" />
                  <span className="text-sm font-medium text-amber-200">
                    智能分析
                  </span>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 2.1, type: "spring" }}
                className="absolute -left-10 bottom-16 rounded-lg border border-yellow-500/30 bg-black/80 p-3 backdrop-blur-sm lg:-left-16"
              >
                <div className="flex items-center gap-2">
                  <Target className="h-4 w-4 text-yellow-400" />
                  <span className="text-sm font-medium text-yellow-200">
                    精准截流
                  </span>
                </div>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </motion.main>
    </section>
  );
}
