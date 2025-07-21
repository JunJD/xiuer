import React from "react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
  PopoverClose,
} from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";

interface DeleteConfirmationDialogProps {
  onConfirm: () => void;
  isPending?: boolean;
  itemCount?: number;
  children: React.ReactNode; // The trigger
  title?: string;
  description?: string;
  confirmText?: string;
  cancelText?: string;
}

export function DeleteConfirmationDialog({
  onConfirm,
  isPending = false,
  itemCount,
  children,
  title = "确认删除",
  description,
  confirmText = "确认",
  cancelText = "取消",
}: DeleteConfirmationDialogProps) {
  const defaultDescription = itemCount
    ? `您确定要删除所选的 ${itemCount} 个项目吗？`
    : "您确定要执行此操作吗？";

  return (
    <Popover>
      <PopoverTrigger asChild>{children}</PopoverTrigger>
      <PopoverContent
        className="w-auto p-4"
        onOpenAutoFocus={(e) => e.preventDefault()}
      >
        <div className="space-y-2">
          <p className="text-sm font-semibold">{title}</p>
          <p className="text-sm text-muted-foreground">
            {description || defaultDescription}
            <br />
            此操作将无法撤销。
          </p>
          <div className="flex justify-end space-x-2 pt-2">
            <PopoverClose asChild>
              <Button size="sm" variant="outline">
                {cancelText}
              </Button>
            </PopoverClose>
            <Button
              size="sm"
              variant="destructive"
              onClick={onConfirm}
              disabled={isPending}
            >
              {isPending ? "删除中..." : confirmText}
            </Button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
} 