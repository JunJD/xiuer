"use client";

import React from "react";
import { DataTable } from "@/components/data-table/data-table";
import { DataTableAdvancedToolbar } from "@/components/data-table/data-table-advanced-toolbar";
import { DataTableFilterMenu } from "@/components/data-table/data-table-filter-menu";
import { DataTableSortList } from "@/components/data-table/data-table-sort-list";
import { useDataTable } from "@/hooks/use-data-table";
import { Button } from "@/components/ui/button";
import { MoreHorizontal, Download, Trash2, Eye, X, Play, Square } from "lucide-react";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import type { ColumnDef, Table } from "@tanstack/react-table";
import { TaskResponse, cancelTask, triggerCrawlTask } from "@/components/actions/task-action";

interface TasksDataTableProps {
  tasks: TaskResponse[];
}

// 简单的自定义操作栏组件
function SimpleActionBar({ table, onExport, onDelete }: {
  table: Table<TaskResponse>;
  onExport: () => void;
  onDelete: () => void;
}) {
  const selectedCount = table.getFilteredSelectedRowModel().rows.length;
  
  if (selectedCount === 0) return null;

  return (
    <div className="fixed inset-x-0 bottom-6 z-50 mx-auto flex w-fit items-center gap-2 rounded-md border bg-background p-2 shadow-lg">
      <div className="flex items-center gap-2 rounded-md border px-3 py-1">
        <span className="text-sm">{selectedCount} 项已选择</span>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => table.toggleAllRowsSelected(false)}
          className="h-6 w-6 p-0"
        >
          <X className="h-3 w-3" />
        </Button>
      </div>
      <Button variant="secondary" size="sm" onClick={onExport}>
        <Download className="mr-1 h-3 w-3" />
        导出
      </Button>
      <Button variant="destructive" size="sm" onClick={onDelete}>
        <Trash2 className="mr-1 h-3 w-3" />
        批量取消
      </Button>
    </div>
  );
}

export default function TasksDataTable({ tasks }: TasksDataTableProps) {
  const [selectedRows, setSelectedRows] = React.useState<TaskResponse[]>([]);

  const handleViewDetail = React.useCallback(async (row: TaskResponse) => {
    // TODO: 实现查看详情功能
    console.log("查看详情", row);
  }, []);

  const handleCancelTask = React.useCallback(async (taskId: string) => {
    try {
      const result = await cancelTask(taskId);
      if (result.success) {
        console.log("任务取消成功", result);
        // TODO: 刷新数据
        window.location.reload();
      }
    } catch (error) {
      console.error("取消任务失败", error);
    }
  }, []);

  const handleRetryTask = React.useCallback(async (task: TaskResponse) => {
    try {
      // 重新触发任务
      const result = await triggerCrawlTask({
        task_name: `重试-${task.task_name}`,
        keyword: task.keyword,
        target_count: task.target_count,
        sort_type: task.sort_type,
        cookies: task.cookies || "",
        webhook_url: `${window.location.origin}/api/webhook`, // 假设的webhook URL
      });
      
      if (result.success) {
        console.log("任务重试成功", result);
        // TODO: 刷新数据
        window.location.reload();
      }
    } catch (error) {
      console.error("重试任务失败", error);
    }
  }, []);

  const handleBatchExport = React.useCallback(async () => {
    // TODO: 实现批量导出功能
    console.log("批量导出", selectedRows);
  }, [selectedRows]);

  const handleBatchCancel = React.useCallback(async () => {
    // TODO: 实现批量取消功能
    console.log("批量取消", selectedRows);
    for (const task of selectedRows) {
      if (task.status === "pending" || task.status === "running") {
        await handleCancelTask(task.id);
      }
    }
  }, [selectedRows, handleCancelTask]);

  const getStatusColor = (status: string) => {
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
  };

  const getStatusText = (status: string) => {
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
  };

  const columns: ColumnDef<TaskResponse>[] = React.useMemo(() => [
    {
      id: "select",
      enableSorting: false,
      enableHiding: false,
      enableColumnFilter: false,
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
          <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(value)}`}>
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
        const value = getValue() as string;
        return new Date(value).toLocaleDateString("zh-CN", {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        });
      },
      meta: {
        label: "创建时间",
        variant: "date",
      },
      enableColumnFilter: true,
      enableSorting: true,
      size: 120,
    },
    {
      id: "actions",
      header: "操作",
      cell: ({ row }) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">打开菜单</span>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => handleViewDetail(row.original)}>
              <Eye className="mr-2 h-4 w-4" />
              查看详情
            </DropdownMenuItem>
            {(row.original.status === "pending" || row.original.status === "running") && (
              <DropdownMenuItem 
                onClick={() => handleCancelTask(row.original.id)}
                className="text-destructive"
              >
                <Square className="mr-2 h-4 w-4" />
                取消任务
              </DropdownMenuItem>
            )}
            {row.original.status === "failed" && (
              <DropdownMenuItem onClick={() => handleRetryTask(row.original)}>
                <Play className="mr-2 h-4 w-4" />
                重试任务
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      ),
      enableSorting: false,
      enableHiding: false,
      enableColumnFilter: false,
      size: 100,
    },
  ], [handleViewDetail, handleCancelTask, handleRetryTask]);

  const { table } = useDataTable({
    data: tasks,
    columns,
    pageCount: Math.ceil(tasks.length / 10),
    initialState: {
      pagination: { pageIndex: 0, pageSize: 10 },
      sorting: [{ id: "created_at", desc: true }],
    },
    enableAdvancedFilter: true,
    enableRowSelection: true,
  });

  // 监听选中行变化
  React.useEffect(() => {
    const selectedRowModel = table.getFilteredSelectedRowModel();
    setSelectedRows(selectedRowModel.rows.map(row => row.original));
  }, [table]);

  return (
    <div className="space-y-4">
      <DataTable table={table}>
        <DataTableAdvancedToolbar table={table}>
          <DataTableFilterMenu table={table} />
          <DataTableSortList table={table} />
        </DataTableAdvancedToolbar>
      </DataTable>

      <SimpleActionBar 
        table={table} 
        onExport={handleBatchExport}
        onDelete={handleBatchCancel}
      />
    </div>
  );
} 