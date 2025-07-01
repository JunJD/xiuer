import TasksDataTable from "@/components/TasksDataTable";
import { getTasks } from "@/components/actions/task-action";

export default async function TasksPage() {
  // 获取任务数据
  const tasksData = await getTasks({ size: 100 });
  
  return (
    <div className="container mx-auto py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">任务管理</h1>
        <p className="text-muted-foreground">管理爬取任务和查看任务状态</p>
      </div>
      
      <TasksDataTable tasks={tasksData.tasks} />
    </div>
  );
}
