"use client";

import React from "react";
import { DataTable } from "@/components/data-table/data-table";
import { DataTableAdvancedToolbar } from "@/components/data-table/data-table-advanced-toolbar";
import { DataTableFilterMenu } from "@/components/data-table/data-table-filter-menu";
import { DataTableSortList } from "@/components/data-table/data-table-sort-list";
import { DataTableActionBar, DataTableActionBarAction, DataTableActionBarSelection } from "@/components/data-table/data-table-action-bar";
import { useDataTable } from "@/hooks/use-data-table";
import { Button } from "@/components/ui/button";
import { MoreHorizontal, Download, Trash2, Eye } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Checkbox } from "@/components/ui/checkbox";
import type { ColumnDef } from "@tanstack/react-table";
import { XhsNoteResponse } from "@/app/openapi-client";
import type { HTTPValidationError, NotesListResponse } from "@/app/openapi-client/types.gen";

interface NotesDataTableProps {
  notesPromise: Promise<NotesListResponse | { message: string } | { message: HTTPValidationError }>;
}

export default function NotesDataTable({ notesPromise }: NotesDataTableProps) {
  const notesData = React.use(notesPromise);

  const handleViewDetail = React.useCallback(async (row: XhsNoteResponse) => {
    // TODO: 实现查看详情功能
    console.log("查看详情", row);
  }, []);

  const handleBatchExport = React.useCallback(async () => {
    // TODO: 实现批量导出功能
    console.log("批量导出");
  }, []);

  const handleBatchDelete = React.useCallback(async () => {
    // TODO: 实现批量删除功能
    console.log("批量删除");
  }, []);

  const columns: ColumnDef<XhsNoteResponse>[] = React.useMemo(
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
        enableColumnFilter: false,
      },
      {
        id: "title",
        accessorKey: "title",
        header: "标题",
        cell: ({ getValue }) => {
          const value = getValue() as string;
          return (
            <div className="truncate max-w-[200px]" title={value}>
              {value || "无标题"}
            </div>
          );
        },
        meta: {
          label: "标题",
          variant: "text",
        },
        enableColumnFilter: true,
        enableSorting: true,
        size: 200,
      },
      {
        id: "author_nickname",
        accessorKey: "author_nickname",
        header: "作者",
        cell: ({ getValue }) => (getValue() as string) || "未知作者",
        meta: {
          label: "作者",
          variant: "text",
        },
        enableColumnFilter: true,
        enableSorting: true,
        size: 120,
      },
      {
        id: "liked_count",
        accessorKey: "liked_count",
        header: "点赞数",
        cell: ({ getValue }) => Number(getValue()).toLocaleString(),
        meta: {
          label: "点赞数",
          variant: "number",
        },
        enableColumnFilter: true,
        enableSorting: true,
        size: 80,
      },
      {
        id: "comment_count",
        accessorKey: "comment_count",
        header: "评论数",
        cell: ({ getValue }) => Number(getValue()).toLocaleString(),
        meta: {
          label: "评论数",
          variant: "number",
        },
        enableColumnFilter: true,
        enableSorting: true,
        size: 80,
      },
      {
        id: "is_new",
        accessorKey: "is_new",
        header: "新笔记",
        cell: ({ getValue }) => {
          const value = getValue() as boolean;
          return (
            <span
              className={`px-2 py-1 rounded-full text-xs ${
                value
                  ? "bg-blue-100 text-blue-800"
                  : "bg-gray-100 text-gray-600"
              }`}
            >
              {value ? "新" : "-"}
            </span>
          );
        },
        meta: {
          label: "新笔记",
          variant: "boolean",
          options: [
            { value: "true", label: "是" },
            { value: "false", label: "否" },
          ],
        },
        enableColumnFilter: true,
        enableSorting: true,
        size: 80,
      },
      {
        id: "is_changed",
        accessorKey: "is_changed",
        header: "已变更",
        cell: ({ getValue }) => {
          const value = getValue() as boolean;
          return (
            <span
              className={`px-2 py-1 rounded-full text-xs ${
                value
                  ? "bg-orange-100 text-orange-800"
                  : "bg-gray-100 text-gray-600"
              }`}
            >
              {value ? "变更" : "-"}
            </span>
          );
        },
        meta: {
          label: "已变更",
          variant: "boolean",
          options: [
            { value: "true", label: "是" },
            { value: "false", label: "否" },
          ],
        },
        enableColumnFilter: true,
        enableSorting: true,
        size: 80,
      },
      {
        id: "is_important",
        accessorKey: "is_important",
        header: "重要",
        cell: ({ getValue }) => {
          const value = getValue() as boolean;
          return (
            <span
              className={`px-2 py-1 rounded-full text-xs ${
                value ? "bg-red-100 text-red-800" : "bg-gray-100 text-gray-600"
              }`}
            >
              {value ? "重要" : "-"}
            </span>
          );
        },
        meta: {
          label: "重要",
          variant: "boolean",
          options: [
            { value: "true", label: "是" },
            { value: "false", label: "否" },
          ],
        },
        enableColumnFilter: true,
        enableSorting: true,
        size: 80,
      },
      {
        id: "last_crawl_time",
        accessorKey: "last_crawl_time",
        header: "最后爬取",
        cell: ({ getValue }) => {
          const value = getValue() as string;
          return new Date(value).toLocaleDateString("zh-CN");
        },
        meta: {
          label: "最后爬取",
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
              <DropdownMenuItem
                onClick={() => {
                  if (row.original.note_url) {
                    window.open(row.original.note_url, "_blank");
                  }
                }}
              >
                查看原文
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ),
        enableSorting: false,
        enableHiding: false,
        enableColumnFilter: false,
        size: 100,
      },
    ],
    [handleViewDetail],
  );

  const notes = notesData && "notes" in notesData ? notesData.notes : [];
  const pageCount = notesData && "notes" in notesData ? Math.ceil(notesData.total / notesData.size) : 0;
  
  const { table } = useDataTable<XhsNoteResponse>({
    data: notes,
    columns,
    pageCount,
    initialState: {
      sorting: [{ id: "last_crawl_time", desc: true }],
      columnPinning: { right: ["actions"] },
    },
    getRowId: (originalRow) => originalRow.id,
    shallow: false,
    clearOnDefault: true,
  });

  if (!notesData || !("notes" in notesData)) {
    let errorMessage = "Unknown error";
    if (notesData && "message" in notesData) {
      if (typeof notesData.message === "string") {
        errorMessage = notesData.message;
      } else if (notesData.message && typeof notesData.message === "object") {
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
    <div className="space-y-4">
      <DataTable
        table={table}
        actionBar={
          <DataTableActionBar table={table}>
            <DataTableActionBarAction isPending={false}>
              <DataTableActionBarSelection table={table} />
              <Button variant="secondary" size="sm" onClick={handleBatchExport}>
                <Download className="mr-1 h-3 w-3" />
                导出
              </Button>
              <Button variant="destructive" size="sm" onClick={handleBatchDelete}>
                <Trash2 className="mr-1 h-3 w-3" />
                删除
              </Button>
            </DataTableActionBarAction>
          </DataTableActionBar>
        }
      >
        <DataTableAdvancedToolbar table={table}>
          <DataTableFilterMenu table={table} />
          <DataTableSortList table={table} />
        </DataTableAdvancedToolbar>
      </DataTable>
    </div>
  );
}
