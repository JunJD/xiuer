'use client';

import React, { useEffect, useId, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { useOutsideClick } from '@/hooks/use-outside-click';
import { XhsNoteResponse } from '@/app/openapi-client';
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";

interface ExpandableNoteGridProps {
  notes: XhsNoteResponse[];
}

// 处理小红书链接跳转的函数
const handleXhsLinkClick = (noteId: string, noteUrl?: string | null) => {
  // 小红书 app 的 URL scheme
  const xhsAppUrl = `xhsdiscover://item/${noteId}`;
  
  // 检测是否为移动端
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  
  if (isMobile) {
    // 移动端：尝试打开 app，失败时打开网页
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.src = xhsAppUrl;
    document.body.appendChild(iframe);
    
    // 设置超时，如果 app 没有打开，则打开网页
    const timeoutId = setTimeout(() => {
      document.body.removeChild(iframe);
      if (noteUrl) {
        window.open(noteUrl, '_blank');
      }
    }, 1500);
    
    // 如果页面失去焦点（说明 app 打开了），取消网页跳转
    const handleVisibilityChange = () => {
      if (document.hidden) {
        clearTimeout(timeoutId);
        document.body.removeChild(iframe);
        document.removeEventListener('visibilitychange', handleVisibilityChange);
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    // 清理定时器
    setTimeout(() => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    }, 3000);
  } else {
    // 桌面端：直接打开网页
    if (noteUrl) {
      window.open(noteUrl, '_blank');
    }
  }
};

export default function ExpandableNoteGrid({ notes }: ExpandableNoteGridProps) {
  const [active, setActive] = useState<XhsNoteResponse | null>(null);
  const id = useId();
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setActive(null);
      }
    }

    if (active) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "auto";
    }

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [active]);

  useOutsideClick(ref, () => setActive(null));

  return (
    <>
      {/* 背景遮罩 */}
      <AnimatePresence>
        {active && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 h-full w-full z-10"
          />
        )}
      </AnimatePresence>

      {/* 展开的详情卡片 */}
      <AnimatePresence>
        {active ? (
          <div className="fixed inset-0 grid place-items-center z-[100]">
            <motion.button
              key={`button-${active.note_id}-${id}`}
              layout
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0, transition: { duration: 0.05 } }}
              className="flex absolute top-2 right-2 lg:hidden items-center justify-center bg-white rounded-full h-8 w-8 z-[110]"
              onClick={() => setActive(null)}
            >
              <CloseIcon />
            </motion.button>
            
            <motion.div
              layoutId={`card-${active.note_id}-${id}`}
              ref={ref}
              className="w-full max-w-[500px] h-full md:h-fit md:max-h-[90%] flex flex-col bg-white dark:bg-neutral-900 sm:rounded-3xl overflow-hidden"
            >
              <motion.div layoutId={`image-${active.note_id}-${id}`}>
                {active.image_list && active.image_list.length > 0 ? (
                  <Carousel className="w-full">
                    <CarouselContent>
                      {active.image_list.map((image, index) => (
                        <CarouselItem key={index}>
                          <img
                            src={image}
                            alt={`${active.title || '笔记图片'} ${index + 1}`}
                            className="w-full h-80 lg:h-80 sm:rounded-tr-lg sm:rounded-tl-lg object-cover object-top"
                            referrerPolicy="no-referrer"
                          />
                        </CarouselItem>
                      ))}
                    </CarouselContent>
                    {active.image_list.length > 1 && (
                      <>
                        <CarouselPrevious className="left-4" />
                        <CarouselNext className="right-4" />
                        <div className="absolute top-4 right-4 bg-black/50 text-white px-2 py-1 rounded-full text-xs">
                          1/{active.image_list.length}
                        </div>
                      </>
                    )}
                  </Carousel>
                ) : (
                  <div className="w-full h-80 lg:h-80 sm:rounded-tr-lg sm:rounded-tl-lg bg-gradient-to-br from-red-400 to-pink-500 flex items-center justify-center text-white">
                    <div className="text-center">
                      <div className="text-4xl mb-2">📝</div>
                      <span className="text-sm opacity-90">小红书笔记</span>
                    </div>
                  </div>
                )}
              </motion.div>

              <div>
                <div className="flex justify-between items-start p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-red-400 to-pink-500 rounded-full flex items-center justify-center overflow-hidden flex-shrink-0">
                      {active.author_avatar ? (
                        <img 
                          src={active.author_avatar} 
                          alt="author avatar" 
                          className="w-full h-full object-cover rounded-full" 
                          referrerPolicy="no-referrer"
                        />
                      ) : (
                        <span className="text-white text-lg font-bold">
                          {active.author_nickname?.charAt(0) || '?'}
                        </span>
                      )}
                    </div>
                    <div className="flex-1">
                      <motion.h3
                        layoutId={`title-${active.note_id}-${id}`}
                        className="font-bold text-neutral-700 dark:text-neutral-200"
                      >
                        {active.title || '无标题'}
                      </motion.h3>
                      <motion.p
                        layoutId={`author-${active.note_id}-${id}`}
                        className="text-neutral-600 dark:text-neutral-400"
                      >
                        @{active.author_nickname || '未知作者'}
                      </motion.p>
                    </div>
                  </div>

                  <motion.button
                    layoutId={`button-${active.note_id}-${id}`}
                    onClick={() => handleXhsLinkClick(active.note_id, active.note_url)}
                    className="px-4 py-3 text-sm rounded-full font-bold bg-red-500 text-white hover:bg-red-600 transition-colors flex items-center gap-2"
                  >
                    <span>📱</span>
                    <span>在小红书中打开</span>
                  </motion.button>
                </div>
                
                <div className="pt-4 relative px-4">
                  <motion.div
                    layout
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="text-neutral-600 text-xs md:text-sm lg:text-base h-40 md:h-fit pb-10 flex flex-col items-start gap-4 overflow-auto dark:text-neutral-400 [mask:linear-gradient(to_bottom,white,white,transparent)] [scrollbar-width:none] [-ms-overflow-style:none] [-webkit-overflow-scrolling:touch]"
                  >
                    <div className="space-y-4 w-full">
                      <div>
                        <h4 className="font-semibold mb-2 text-neutral-700 dark:text-neutral-300">笔记内容</h4>
                        <p className="leading-relaxed whitespace-pre-wrap">
                          {active.desc || '暂无描述'}
                        </p>
                      </div>
                      
                      {active.current_tags && active.current_tags.length > 0 && (
                        <div>
                          <h4 className="font-semibold mb-2 text-neutral-700 dark:text-neutral-300">标签</h4>
                          <div className="flex flex-wrap gap-2">
                            {active.current_tags.map((tag, index) => (
                              <span key={index} className="bg-red-50 text-red-600 px-3 py-1 rounded-full text-sm border border-red-200">
                                #{tag}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="flex gap-4 text-sm text-gray-500">
                        <span className="flex items-center gap-1">
                          ❤️ {active.liked_count}
                        </span>
                        <span className="flex items-center gap-1">
                          💬 {active.comment_count}
                        </span>
                      </div>

                      <div className="pt-4 border-t border-gray-100 dark:border-gray-700">
                        <div className="text-xs text-gray-500 space-y-1">
                          <p>最后爬取: {new Date(active.last_crawl_time).toLocaleString()}</p>
                          <div className="flex gap-2 mt-2">
                            {active.is_new && <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-xs">新</span>}
                            {active.is_changed && <span className="bg-orange-100 text-orange-700 px-2 py-1 rounded text-xs">变更</span>}
                            {active.is_important && <span className="bg-red-100 text-red-700 px-2 py-1 rounded text-xs">重要</span>}
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </div>
              </div>
            </motion.div>
          </div>
        ) : null}
      </AnimatePresence>

      {/* 小红书风格笔记列表 */}
      <div className="max-w-4xl mx-auto w-full p-4">
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
          {notes.map((note) => (
            <motion.div
              layoutId={`card-${note.note_id}-${id}`}
              key={`card-${note.note_id}-${id}`}
              onClick={() => setActive(note)}
              className="group cursor-pointer"
            >
              <div className="bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-lg transition-all duration-300">
                {/* 图片区域 */}
                <motion.div 
                  layoutId={`image-${note.note_id}-${id}`}
                  className="relative aspect-[3/4] overflow-hidden"
                >
                  {note.image_list && note.image_list.length > 0 ? (
                    <img
                      src={note.image_list[0]}
                      alt={note.title || '笔记图片'}
                      className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                      referrerPolicy="no-referrer"
                    />
                  ) : (
                    <div className="w-full h-full bg-gradient-to-br from-red-400 to-pink-500 flex items-center justify-center text-white">
                      <div className="text-center">
                        <div className="text-3xl mb-2">📝</div>
                        <span className="text-xs opacity-90">小红书</span>                        
                      </div>
                    </div>
                  )}
                  
                  {/* 图片数量指示器 */}
                  {note.image_list && note.image_list.length > 1 && (
                    <div className="absolute top-3 right-3 bg-black/60 text-white px-2 py-1 rounded-full text-xs">
                      {note.image_list.length}
                    </div>
                  )}
                  
                  {/* 状态标签 */}
                  <div className="absolute top-3 left-3 flex gap-1">
                    {note.is_new && (
                      <span className="bg-green-500 text-white px-2 py-1 rounded-full text-xs">新</span>
                    )}
                    {note.is_important && (
                      <span className="bg-red-500 text-white px-2 py-1 rounded-full text-xs">重要</span>
                    )}
                  </div>
                </motion.div>

                {/* 内容区域 */}
                <div className="p-3">
                  <motion.h3
                    layoutId={`title-${note.note_id}-${id}`}
                    className="font-medium text-neutral-800 dark:text-neutral-200 text-sm line-clamp-2 mb-2"
                  >
                    {note.title || '无标题'}
                  </motion.h3>
                  
                  <motion.div
                    layoutId={`author-${note.note_id}-${id}`}
                    className="flex items-center justify-between"
                  >
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 bg-gradient-to-br from-red-400 to-pink-500 rounded-full flex items-center justify-center overflow-hidden">
                        {note.author_avatar ? (
                          <img 
                            src={note.author_avatar} 
                            alt="author avatar" 
                            className="w-full h-full object-cover rounded-full" 
                            referrerPolicy="no-referrer"
                          />
                        ) : (
                          <span className="text-white text-xs">
                            {note.author_nickname?.charAt(0) || '?'}
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-gray-600 truncate max-w-[80px]">
                        {note.author_nickname || '未知作者'}
                      </span>
                    </div>
                    
                    <motion.div
                      layoutId={`button-${note.note_id}-${id}`}
                      className="flex gap-2 text-xs text-gray-500"
                    >
                      <span>❤️ {note.liked_count}</span>
                    </motion.div>
                  </motion.div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </>
  );
}

export const CloseIcon = () => {
  return (
    <motion.svg
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, transition: { duration: 0.05 } }}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-4 w-4 text-black"
    >
      <path stroke="none" d="M0 0h24v24H0z" fill="none" />
      <path d="M18 6l-12 12" />
      <path d="M6 6l12 12" />
    </motion.svg>
  );
};
