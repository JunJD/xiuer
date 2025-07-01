"use client";

import * as React from "react";
import { ColumnDef } from "@tanstack/react-table";

import { DataTable } from "@/components/data-table/data-table";
import { DataTableColumnHeader } from "@/components/data-table/data-table-column-header";
import { DataTableToolbar } from "@/components/data-table/data-table-toolbar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useDataTable } from "@/hooks/use-data-table";
import { MoreHorizontal } from "lucide-react";

// 保持与原EasyTable的类型兼容
export interface ActionItem<T = Record<string, unknown>> {
  label: string;
  onClick: (row: T) => void;
  disabled?: boolean;
  variant?:
    | "default"
    | "destructive"
    | "outline"
    | "secondary"
    | "ghost"
    | "link";
}

export interface ColumnDefinition<T = Record<string, unknown>> {
  key: keyof T;
  title: string;
  render?: (value: unknown, row: T) => React.ReactNode;
  width?: string;
  align?: "left" | "center" | "right";
  actions?: ActionItem<T>[];
  sortable?: boolean;
  filterable?: boolean;
}

interface AdvancedDataTableProps<T = Record<string, unknown>> {
  columns: ColumnDefinition<T>[];
  data: T[];
  loading?: boolean;
  emptyMessage?: string;
  showToolbar?: boolean;
  pageSize?: number;
  enablePagination?: boolean;
  enableSorting?: boolean;
  enableFiltering?: boolean;
}

export default function AdvancedDataTable<T = Record<string, unknown>>({
  columns,
  data,
  loading = false,
  emptyMessage = "暂无数据",
  showToolbar = true,
  pageSize = 10,
  enablePagination = true,
  enableSorting = true,
  enableFiltering = true,
}: AdvancedDataTableProps<T>) {
  // 将EasyTable的ColumnDefinition转换为TanStack Table的ColumnDef
  const tanStackColumns = React.useMemo<ColumnDef<T>[]>(() => {
    return columns.map((column) => {
      const {
        key,
        title,
        render,
        align,
        actions,
        sortable = true,
        filterable = false,
      } = column;

      // 构建基础column定义
      const columnDef: ColumnDef<T> = {
        id: key as string,
        accessorKey: key as string,
        header: ({ column: tanStackColumn }) => (
          <DataTableColumnHeader
            column={tanStackColumn}
            title={title}
            className={getAlignmentClass(align)}
          />
        ),
        cell: ({ cell, row }) => {
          const value = cell.getValue();

          // 如果有actions，渲染下拉菜单
          if (actions && actions.length > 0) {
            return (
              <div className={getAlignmentClass(align)}>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="h-8 w-8 p-0">
                      <span className="sr-only">打开菜单</span>
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    {actions.map((action, index) => (
                      <DropdownMenuItem
                        key={index}
                        onClick={() => action.onClick(row.original)}
                        disabled={action.disabled}
                        className={
                          action.variant === "destructive"
                            ? "text-red-600 focus:text-red-600"
                            : ""
                        }
                      >
                        {action.label}
                      </DropdownMenuItem>
                    ))}
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            );
          }

          // 如果有自定义渲染函数
          if (render) {
            return (
              <div className={getAlignmentClass(align)}>
                {render(value, row.original)}
              </div>
            );
          }

          // 默认渲染
          return (
            <div className={getAlignmentClass(align)}>
              {String(value || "")}
            </div>
          );
        },
        enableSorting: enableSorting && sortable,
        enableColumnFilter: enableFiltering && filterable,
        size: column.width
          ? parseInt(column.width.replace(/\D/g, ""))
          : undefined,
      };

      // 如果启用筛选，添加meta信息
      if (enableFiltering && filterable) {
        columnDef.meta = {
          label: title,
          placeholder: `搜索${title}...`,
          variant: "text",
        };
      }

      return columnDef;
    });
  }, [columns, enableSorting, enableFiltering]);

  const { table } = useDataTable({
    data,
    columns: tanStackColumns,
    pageCount: enablePagination ? Math.ceil(data.length / pageSize) : 1,
    initialState: {
      pagination: {
        pageIndex: 0,
        pageSize: pageSize,
      },
    },
    getRowId: (row: T, index: number) => {
      // 尝试使用id字段，如果没有则使用index
      return (
        (row as Record<string, unknown>).id?.toString() || index.toString()
      );
    },
  });

  const getAlignmentClass = (align?: string) => {
    switch (align) {
      case "center":
        return "text-center";
      case "right":
        return "text-right";
      default:
        return "text-left";
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="data-table-container">
      <DataTable table={table}>
        {showToolbar && <DataTableToolbar table={table} />}
      </DataTable>
      {data.length === 0 && (
        <div className="text-center py-8 text-gray-500">{emptyMessage}</div>
      )}
    </div>
  );
}

// 注意：类型定义已在组件内部，避免与EasyTable冲突
