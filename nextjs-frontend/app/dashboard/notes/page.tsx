import { getNotes } from "@/components/actions/notes-action";
import { getValidFilters } from "@/lib/data-table";
import type { SearchParams } from "@/types";
import NotesDataTable from "@/components/NotesDataTable";
import { searchParamsCache } from "./_lib/validations";
import { Suspense } from "react";

interface NotesPageProps {
  searchParams: Promise<SearchParams>;
}

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function NotesPage(props: NotesPageProps) {
  const searchParams = await props.searchParams;
  const search = searchParamsCache.parse(searchParams);

  console.log('notes search==>', search);
  
  const validFilters = getValidFilters(search.filters);
  
  // 创建 Promise 但不等待它们完成
  const notesPromise = getNotes({
    page: search.page,
    size: search.perPage,
    keyword: search.keyword || undefined,
    is_new: search.is_new ?? undefined,
    is_changed: search.is_changed ?? undefined,
    is_important: search.is_important ?? undefined,
    today_only: search.today_only,
  });

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <div className="h-full">
        {/* 笔记列表 */}
        <section className="p-6 bg-white rounded-lg shadow-lg mt-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-semibold">笔记列表</h2>
              <p className="text-sm text-gray-500">
                查看和分析所有爬取到的小红书笔记数据
              </p>
            </div>
          </div>
          <NotesDataTable notesPromise={notesPromise} />
        </section>
      </div>
    </Suspense>
  );
} 