import TasksDataTable from "@/components/TasksDataTable";
import { getTasks, getTaskStats } from "@/components/actions/task-action";
import { AlertCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default async function TasksPage() {
  // 并行获取任务数据和统计信息
  const [tasksData, statsData] = await Promise.all([
    getTasks({ size: 100 }),
    getTaskStats(),
  ]);

  if (!("tasks" in tasksData)) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">加载失败</h3>
          <p className="text-muted-foreground">
            Error: {tasksData?.message as string}
          </p>
        </div>
      </div>
    );
  }

  // 统计数据（如果获取失败则使用默认值）
  const stats =
    statsData && "total_tasks" in statsData
      ? statsData
      : {
          total_tasks: tasksData.total || 0,
          pending_tasks: 0,
          running_tasks: 0,
          completed_tasks: 0,
          failed_tasks: 0,
        };

  return (
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

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">总任务数</h3>
          <p className="text-2xl font-bold text-blue-600">
            {stats.total_tasks}
          </p>
          <p className="text-xs text-gray-500">累计创建的任务数量</p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">正在执行</h3>
          <p className="text-2xl font-bold text-blue-600">
            {stats.running_tasks}
          </p>
          <p className="text-xs text-gray-500">正在执行中的任务</p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">执行成功</h3>
          <p className="text-2xl font-bold text-green-600">
            {stats.completed_tasks}
          </p>
          <p className="text-xs text-gray-500">已成功完成的任务</p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">执行失败</h3>
          <p className="text-2xl font-bold text-red-600">
            {stats.failed_tasks}
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
            共 {tasksData.total} 个任务
          </Badge>
        </div>
        <TasksDataTable tasks={tasksData.tasks} />
      </section>
    </div>
  );
}
