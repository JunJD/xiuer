import { getTasks } from "@/components/actions/task-action";
import { Badge } from "@/components/ui/badge";
import { getValidFilters } from "@/lib/data-table";
import type { SearchParams } from "@/types";
import TasksDataTable from "./_components/TasksDataTable";
import { searchParamsCache } from "./_lib /validations";
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
      {/* 页面头部 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-semibold">任务管理</h2>
          <p className="text-lg text-muted-foreground">
            管理和监控小红书数据爬取任务的执行状态
          </p>
        </div>
      </div>

      {/* 统计卡片 - 这里可以用 Suspense 包装 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">总任务数</h3>
          <p className="text-2xl font-bold text-blue-600">
            加载中...
          </p>
          <p className="text-xs text-gray-500">累计创建的任务数量</p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">正在执行</h3>
          <p className="text-2xl font-bold text-blue-600">
            加载中...
          </p>
          <p className="text-xs text-gray-500">正在执行中的任务</p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">执行成功</h3>
          <p className="text-2xl font-bold text-green-600">
            加载中...
          </p>
          <p className="text-xs text-gray-500">已成功完成的任务</p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">执行失败</h3>
          <p className="text-2xl font-bold text-red-600">
            加载中...
          </p>
          <p className="text-xs text-gray-500">执行失败的任务</p>
        </div>
      </div>

      {/* 任务列表 */}
      <section className="p-6 bg-white rounded-lg shadow-lg mt-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold">任务列表</h2>
            <p className="text-sm text-gray-500">
              查看和管理所有爬取任务的详细信息
            </p>
          </div>
          <Badge variant="secondary" className="text-sm">
            数据加载中...
          </Badge>
        </div>
        <TasksDataTable tasksPromise={tasksPromise} />
      </section>
    </div>
    </Suspense>
  );
}
