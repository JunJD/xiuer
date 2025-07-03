"use client";

import React from "react";
import { DataTable } from "@/components/data-table/data-table";
import { DataTableAdvancedToolbar } from "@/components/data-table/data-table-advanced-toolbar";
import { useDataTable } from "@/hooks/use-data-table";
import { Button } from "@/components/ui/button";
import { MoreHorizontal, Eye, Play, Square } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { ColumnDef } from "@tanstack/react-table";
import {
  TaskResponse,
  TaskListResponse,
  cancelTask,
  triggerCrawlTask,
} from "@/components/actions/task-action";
import type { HTTPValidationError } from "@/app/openapi-client/types.gen";
import { Checkbox } from "@/components/ui/checkbox";

interface TasksDataTableProps {
  tasksPromise: Promise<TaskListResponse | { message: string } | { message: HTTPValidationError }>;
}

export default function TasksDataTable({ tasksPromise }: TasksDataTableProps) {
  const tasksData = React.use(tasksPromise);
  
  const handleViewDetail = React.useCallback(async (row: TaskResponse) => {
    console.log("查看详情", row);
  }, []);

  const handleCancelTask = React.useCallback(async (taskId: string) => {
    try {
      const result = await cancelTask(taskId);
      if ("success" in result && result.success) {
        console.log("任务取消成功", result);
        window.location.reload();
      }
    } catch (error) {
      console.error("取消任务失败", error);
    }
  }, []);

  const handleRetryTask = React.useCallback(async (task: TaskResponse) => {
    try {
      const result = await triggerCrawlTask({
        task_name: `重试-${task.task_name}`,
        keyword: task.keyword,
        target_count: task.target_count,
        sort_type: task.sort_type,
        cookies: task.cookies || "",
        webhook_url: `${window.location.origin}/api/webhook`,
      });
      if ("success" in result && result.success) {
        console.log("任务重试成功", result);
        window.location.reload();
      }
    } catch (error) {
      console.error("重试任务失败", error);
    }
  }, []);

  const getStatusColor = React.useCallback((status: string) => {
    switch (status) {
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      case "running":
        return "bg-blue-100 text-blue-800";
      case "completed":
        return "bg-green-100 text-green-800";
      case "failed":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-600";
    }
  }, []);

  const getStatusText = React.useCallback((status: string) => {
    switch (status) {
      case "pending":
        return "待执行";
      case "running":
        return "执行中";
      case "completed":
        return "已完成";
      case "failed":
        return "失败";
      default:
        return status;
    }
  }, []);

  const columns: ColumnDef<TaskResponse>[] = React.useMemo(
    () => [
      {
        id: "select",
        header: ({ table }) => (
          <Checkbox
            checked={
              table.getIsAllPageRowsSelected() ||
              (table.getIsSomePageRowsSelected() && "indeterminate")
            }
            onCheckedChange={(value) =>
              table.toggleAllPageRowsSelected(!!value)
            }
            aria-label="Select all"
          />
        ),
        cell: ({ row }) => (
          <Checkbox
            checked={row.getIsSelected()}
            onCheckedChange={(value) => row.toggleSelected(!!value)}
            aria-label="Select row"
          />
        ),
        size: 32,
        enableSorting: false,
        enableHiding: false,
      },
      {
        id: "task_name",
        accessorKey: "task_name",
        header: "任务名称",
        cell: ({ getValue }) => {
          const value = getValue() as string;
          return (
            <div className="truncate max-w-[200px]" title={value}>
              {value || "无名称"}
            </div>
          );
        },
        meta: {
          label: "任务名称",
          variant: "text",
        },
        enableColumnFilter: true,
        enableSorting: true,
        size: 200,
      },
      {
        id: "keyword",
        accessorKey: "keyword",
        header: "关键词",
        cell: ({ getValue }) => (getValue() as string) || "无关键词",
        meta: {
          label: "关键词",
          variant: "text",
        },
        enableColumnFilter: true,
        enableSorting: true,
        size: 120,
      },
      {
        id: "status",
        accessorKey: "status",
        header: "状态",
        cell: ({ getValue }) => {
          const value = getValue() as string;
          return (
            <span
              className={`px-2 py-1 rounded-full text-xs ${getStatusColor(value)}`}
            >
              {getStatusText(value)}
            </span>
          );
        },
        meta: {
          label: "状态",
          variant: "select",
          options: [
            { value: "pending", label: "待执行" },
            { value: "running", label: "执行中" },
            { value: "completed", label: "已完成" },
            { value: "failed", label: "失败" },
          ],
        },
        enableColumnFilter: true,
        enableSorting: true,
        size: 100,
      },
      {
        id: "target_count",
        accessorKey: "target_count",
        header: "目标数量",
        cell: ({ getValue }) => Number(getValue()).toLocaleString(),
        meta: {
          label: "目标数量",
          variant: "number",
        },
        enableColumnFilter: true,
        enableSorting: true,
        size: 100,
      },
      {
        id: "total_crawled",
        accessorKey: "total_crawled",
        header: "已爬取",
        cell: ({ getValue }) => Number(getValue()).toLocaleString(),
        meta: {
          label: "已爬取",
          variant: "number",
        },
        enableColumnFilter: true,
        enableSorting: true,
        size: 80,
      },
      {
        id: "new_notes",
        accessorKey: "new_notes",
        header: "新笔记",
        cell: ({ getValue }) => Number(getValue()).toLocaleString(),
        meta: {
          label: "新笔记",
          variant: "number",
        },
        enableColumnFilter: true,
        enableSorting: true,
        size: 80,
      },
      {
        id: "changed_notes",
        accessorKey: "changed_notes",
        header: "变更笔记",
        cell: ({ getValue }) => Number(getValue()).toLocaleString(),
        meta: {
          label: "变更笔记",
          variant: "number",
        },
        enableColumnFilter: true,
        enableSorting: true,
        size: 80,
      },
      {
        id: "important_notes",
        accessorKey: "important_notes",
        header: "重要笔记",
        cell: ({ getValue }) => Number(getValue()).toLocaleString(),
        meta: {
          label: "重要笔记",
          variant: "number",
        },
        enableColumnFilter: true,
        enableSorting: true,
        size: 80,
      },
      {
        id: "created_at",
        accessorKey: "created_at",
        header: "创建时间",
        cell: ({ getValue }) => {
          const date = new Date(getValue() as string);
          return date.toLocaleString("zh-CN", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
          });
        },
        meta: {
          label: "创建时间",
          variant: "date",
        },
        enableColumnFilter: true,
        enableSorting: true,
        size: 150,
      },
      {
        id: "actions",
        cell: ({ row }) => (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">Open menu</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => handleViewDetail(row.original)}>
                <Eye className="mr-2 h-4 w-4" />
                查看详情
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => handleRetryTask(row.original)}
                disabled={!["failed", "completed"].includes(row.original.status)}
              >
                <Play className="mr-2 h-4 w-4" />
                重新执行
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => handleCancelTask(row.original.id)}
                disabled={!["pending", "running"].includes(row.original.status)}
              >
                <Square className="mr-2 h-4 w-4" />
                取消任务
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ),
        size: 64,
        enableSorting: false,
        enableHiding: false,
      },
    ],
    [handleViewDetail, handleCancelTask, handleRetryTask, getStatusColor, getStatusText],
  );

  const tasks = tasksData && "tasks" in tasksData ? tasksData.tasks : [];
  const pageCount = tasksData && "tasks" in tasksData ? Math.ceil(tasksData.total / tasksData.size) : 0;
  const { table } = useDataTable<TaskResponse>({
    data: tasks,
    columns,
    pageCount,
    initialState: {
      sorting: [{ id: "created_at", desc: true }],
      columnPinning: { right: ["actions"] },
    },
    getRowId: (originalRow) => originalRow.id,
    shallow: false,
    clearOnDefault: true,
  }); 

  if (!tasksData || !("tasks" in tasksData)) {
    let errorMessage = "Unknown error";
    if (tasksData && "message" in tasksData) {
      if (typeof tasksData.message === "string") {
        errorMessage = tasksData.message;
      } else if (tasksData.message && typeof tasksData.message === "object") {
        errorMessage = "Validation error";
      }
    }
    
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <h3 className="text-lg font-semibold mb-2">加载失败</h3>
          <p className="text-muted-foreground">
            Error: {errorMessage}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full space-y-4 overflow-auto">
      <DataTableAdvancedToolbar table={table} />
      <DataTable table={table} />
    </div>
  );
}
