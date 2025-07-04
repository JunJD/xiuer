import { getTasks } from "@/components/actions/task-action";
import { Badge } from "@/components/ui/badge";
import { getValidFilters } from "@/lib/data-table";
import type { SearchParams } from "@/types";
import TasksDataTable from "./_components/TasksDataTable";
import { searchParamsCache } from "./_lib/validations";
import { Suspense } from "react";

interface IndexPageProps {
  searchParams: Promise<SearchParams>;
}

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function TasksPage(props: IndexPageProps)  {
  const searchParams = await props.searchParams;
  const search = searchParamsCache.parse(searchParams);

  console.log('search==>',search);
  
  const validFilters = getValidFilters(search.filters);
  
  // 创建 Promise 但不等待它们完成
  const tasksPromise = getTasks({  ...search, size: search.perPage, filters: validFilters, status: search.status.join(",")});

  return (
    <Suspense fallback={<div>Loading...</div>}>

    <div className="h-full">
      {/* 任务列表 */}
      <section className="p-6 bg-white rounded-lg shadow-lg mt-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold">任务列表</h2>
            <p className="text-sm text-gray-500">
              查看和管理所有爬取任务的详细信息
            </p>
          </div>
        </div>
        <TasksDataTable tasksPromise={tasksPromise} />
      </section>
    </div>
    </Suspense>
  );
}
