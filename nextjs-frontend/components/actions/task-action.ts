"use server";

import { cookies } from "next/headers";
import { 
  getTasks as getTasksApi,
  getTaskDetail as getTaskDetailApi,
  getTaskStats as getTaskStatsApi,
  createTask as createTaskApi,
  cancelTask as cancelTaskApi,
  triggerCrawlTask as triggerCrawlTaskApi
} from "@/app/clientService";
import type { TaskCreate, CrawlTaskRequest } from "@/app/openapi-client";

// 导出生成的类型
export type {
  TaskResponse,
  TaskListResponse,
  TaskStatsResponse,
  TaskActionResponse,
  TaskCreate,
  CrawlTaskRequest
} from "@/app/openapi-client";

/**
 * 获取任务列表
 */
export async function getTasks({
  page = 1,
  size = 10,
  status,
  keyword,
}: {
  page?: number;
  size?: number;
  status?: string;
  keyword?: string;
} = {}) {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken")?.value;

  if (!token) {
    return { message: "No access token found" };
  }

  const { data, error } = await getTasksApi({
    headers: {
      Authorization: `Bearer ${token}`,
    },
    query: {
      page,
      size,
      status,
      keyword,
    },
  });

  if (error) {
    return { message: error };
  }

  return data;
}

/**
 * 获取任务详情
 */
export async function getTaskDetail(taskId: string) {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken")?.value;

  if (!token) {
    return { message: "No access token found" };
  }

  const { data, error } = await getTaskDetailApi({
    headers: {
      Authorization: `Bearer ${token}`,
    },
    path: {
      task_id: taskId,
    },
  });

  if (error) {
    return { message: error };
  }

  return data;
}

/**
 * 获取任务统计
 */
export async function getTaskStats() {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken")?.value;

  if (!token) {
    return { message: "No access token found" };
  }

  const { data, error } = await getTaskStatsApi({
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (error) {
    return { message: error };
  }

  return data;
}

/**
 * 创建任务
 */
export async function createTask(taskData: TaskCreate) {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken")?.value;

  if (!token) {
    return { message: "No access token found" };
  }

  const { data, error } = await createTaskApi({
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: taskData,
  });

  if (error) {
    return { message: error };
  }

  return data;
}

/**
 * 取消任务
 */
export async function cancelTask(taskId: string) {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken")?.value;

  if (!token) {
    return { message: "No access token found" };
  }

  const { data, error } = await cancelTaskApi({
    headers: {
      Authorization: `Bearer ${token}`,
    },
    path: {
      task_id: taskId,
    },
  });

  if (error) {
    return { message: error };
  }

  return data;
}

/**
 * 触发爬取任务
 */
export async function triggerCrawlTask(taskData: CrawlTaskRequest) {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken")?.value;

  if (!token) {
    return { message: "No access token found" };
  }

  const { data, error } = await triggerCrawlTaskApi({
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: taskData,
  });

  if (error) {
    return { message: error };
  }

  return data;
} 