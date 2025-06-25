import React from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TableHeader,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

export interface ActionItem<T = Record<string, unknown>> {
  label: string;
  onClick: (row: T) => void;
  disabled?: boolean;
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link";
}

export interface ColumnDefinition<T = Record<string, unknown>> {
  key: keyof T;
  title: string;
  render?: (value: unknown, row: T) => React.ReactNode;
  width?: string;
  align?: "left" | "center" | "right";
  actions?: ActionItem<T>[];
}

interface EasyTableProps<T = Record<string, unknown>> {
  columns: ColumnDefinition<T>[];
  data: T[];
  loading?: boolean;
  emptyMessage?: string;
}

export default function EasyTable<T = Record<string, unknown>>({
  columns,
  data,
  loading = false,
  emptyMessage = "No results.",
}: EasyTableProps<T>) {
  const renderCell = (column: ColumnDefinition<T>, row: T) => {
    const value = row[column.key];

    // 如果有 actions，渲染下拉菜单
    if (column.actions && column.actions.length > 0) {
      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">Open menu</span>
              <span className="text-lg font-semibold">⋯</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {column.actions.map((action, index) => (
              <DropdownMenuItem
                key={index}
                onClick={() => action.onClick(row)}
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
      );
    }

    // 如果有自定义渲染函数
    if (column.render) {
      return column.render(value, row);
    }

    // 默认渲染
    return String(value);
  };

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
    <Table className="min-w-full text-sm">
      <TableHeader>
        <TableRow>
          {columns.map((column, index) => (
            <TableHead
              key={index}
              className={`${column.width ? `w-[${column.width}]` : ""} ${getAlignmentClass(
                column.align
              )}`}
            >
              {column.title}
            </TableHead>
          ))}
        </TableRow>
      </TableHeader>
      <TableBody>
        {!data.length ? (
          <TableRow>
            <TableCell colSpan={columns.length} className="text-center">
              {emptyMessage}
            </TableCell>
          </TableRow>
        ) : (
          data.map((row, rowIndex) => (
            <TableRow key={rowIndex}>
              {columns.map((column, colIndex) => (
                <TableCell
                  key={colIndex}
                  className={getAlignmentClass(column.align)}
                >
                  {renderCell(column, row)}
                </TableCell>
              ))}
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  );
} 