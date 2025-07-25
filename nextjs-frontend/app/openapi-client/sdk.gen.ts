// This file is auto-generated by @hey-api/openapi-ts

import {
  createClient,
  createConfig,
  type OptionsLegacyParser,
  urlSearchParamsBodySerializer,
} from "@hey-api/client-axios";
import type {
  AuthJwtLoginData,
  AuthJwtLoginError,
  AuthJwtLoginResponse,
  AuthJwtLogoutError,
  AuthJwtLogoutResponse,
  RegisterRegisterData,
  RegisterRegisterError,
  RegisterRegisterResponse,
  ResetForgotPasswordData,
  ResetForgotPasswordError,
  ResetForgotPasswordResponse,
  ResetResetPasswordData,
  ResetResetPasswordError,
  ResetResetPasswordResponse,
  VerifyRequestTokenData,
  VerifyRequestTokenError,
  VerifyRequestTokenResponse,
  VerifyVerifyData,
  VerifyVerifyError,
  VerifyVerifyResponse,
  UsersCurrentUserError,
  UsersCurrentUserResponse,
  UsersPatchCurrentUserData,
  UsersPatchCurrentUserError,
  UsersPatchCurrentUserResponse,
  UsersUserData,
  UsersUserError,
  UsersUserResponse,
  UsersPatchUserData,
  UsersPatchUserError,
  UsersPatchUserResponse,
  UsersDeleteUserData,
  UsersDeleteUserError,
  UsersDeleteUserResponse,
  GetKeywordsData,
  GetKeywordsError,
  GetKeywordsResponse,
  CreateKeywordData,
  CreateKeywordError,
  CreateKeywordResponse,
  UpdateKeywordData,
  UpdateKeywordError,
  UpdateKeywordResponse,
  DeleteKeywordData,
  DeleteKeywordError,
  DeleteKeywordResponse,
  ToggleKeywordStatusData,
  ToggleKeywordStatusError,
  ToggleKeywordStatusResponse,
  GetCategoriesError,
  GetCategoriesResponse,
  GetKeywordStatsError,
  GetKeywordStatsResponse,
  ReceiveXhsWebhookData,
  ReceiveXhsWebhookError,
  ReceiveXhsWebhookResponse,
  TestWebhookError,
  TestWebhookResponse,
  GetNotesStatsError,
  GetNotesStatsResponse,
  SearchNotesData,
  SearchNotesError,
  SearchNotesResponse,
  GetNoteDetailData,
  GetNoteDetailError,
  GetNoteDetailResponse,
  SoftDeleteNoteEndpointData,
  SoftDeleteNoteEndpointError,
  SoftDeleteNoteEndpointResponse,
  TriggerCrawlTaskData,
  TriggerCrawlTaskError,
  TriggerCrawlTaskResponse,
  GetTasksData,
  GetTasksError,
  GetTasksResponse,
  CreateTaskData,
  CreateTaskError,
  CreateTaskResponse,
  GetTaskStatsError,
  GetTaskStatsResponse,
  GetTaskDetailData,
  GetTaskDetailError,
  GetTaskDetailResponse,
  CancelTaskData,
  CancelTaskError,
  CancelTaskResponse,
} from "./types.gen";

export const client = createClient(createConfig());

/**
 * Auth:Jwt.Login
 */
export const authJwtLogin = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<AuthJwtLoginData, ThrowOnError>,
) => {
  return (options?.client ?? client).post<
    AuthJwtLoginResponse,
    AuthJwtLoginError,
    ThrowOnError
  >({
    ...options,
    ...urlSearchParamsBodySerializer,
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      ...options?.headers,
    },
    url: "/api/auth/jwt/login",
  });
};

/**
 * Auth:Jwt.Logout
 */
export const authJwtLogout = <ThrowOnError extends boolean = false>(
  options?: OptionsLegacyParser<unknown, ThrowOnError>,
) => {
  return (options?.client ?? client).post<
    AuthJwtLogoutResponse,
    AuthJwtLogoutError,
    ThrowOnError
  >({
    ...options,
    url: "/api/auth/jwt/logout",
  });
};

/**
 * Register:Register
 */
export const registerRegister = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<RegisterRegisterData, ThrowOnError>,
) => {
  return (options?.client ?? client).post<
    RegisterRegisterResponse,
    RegisterRegisterError,
    ThrowOnError
  >({
    ...options,
    url: "/api/auth/register",
  });
};

/**
 * Reset:Forgot Password
 */
export const resetForgotPassword = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<ResetForgotPasswordData, ThrowOnError>,
) => {
  return (options?.client ?? client).post<
    ResetForgotPasswordResponse,
    ResetForgotPasswordError,
    ThrowOnError
  >({
    ...options,
    url: "/api/auth/forgot-password",
  });
};

/**
 * Reset:Reset Password
 */
export const resetResetPassword = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<ResetResetPasswordData, ThrowOnError>,
) => {
  return (options?.client ?? client).post<
    ResetResetPasswordResponse,
    ResetResetPasswordError,
    ThrowOnError
  >({
    ...options,
    url: "/api/auth/reset-password",
  });
};

/**
 * Verify:Request-Token
 */
export const verifyRequestToken = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<VerifyRequestTokenData, ThrowOnError>,
) => {
  return (options?.client ?? client).post<
    VerifyRequestTokenResponse,
    VerifyRequestTokenError,
    ThrowOnError
  >({
    ...options,
    url: "/api/auth/request-verify-token",
  });
};

/**
 * Verify:Verify
 */
export const verifyVerify = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<VerifyVerifyData, ThrowOnError>,
) => {
  return (options?.client ?? client).post<
    VerifyVerifyResponse,
    VerifyVerifyError,
    ThrowOnError
  >({
    ...options,
    url: "/api/auth/verify",
  });
};

/**
 * Users:Current User
 */
export const usersCurrentUser = <ThrowOnError extends boolean = false>(
  options?: OptionsLegacyParser<unknown, ThrowOnError>,
) => {
  return (options?.client ?? client).get<
    UsersCurrentUserResponse,
    UsersCurrentUserError,
    ThrowOnError
  >({
    ...options,
    url: "/api/users/me",
  });
};

/**
 * Users:Patch Current User
 */
export const usersPatchCurrentUser = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<UsersPatchCurrentUserData, ThrowOnError>,
) => {
  return (options?.client ?? client).patch<
    UsersPatchCurrentUserResponse,
    UsersPatchCurrentUserError,
    ThrowOnError
  >({
    ...options,
    url: "/api/users/me",
  });
};

/**
 * Users:User
 */
export const usersUser = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<UsersUserData, ThrowOnError>,
) => {
  return (options?.client ?? client).get<
    UsersUserResponse,
    UsersUserError,
    ThrowOnError
  >({
    ...options,
    url: "/api/users/{id}",
  });
};

/**
 * Users:Patch User
 */
export const usersPatchUser = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<UsersPatchUserData, ThrowOnError>,
) => {
  return (options?.client ?? client).patch<
    UsersPatchUserResponse,
    UsersPatchUserError,
    ThrowOnError
  >({
    ...options,
    url: "/api/users/{id}",
  });
};

/**
 * Users:Delete User
 */
export const usersDeleteUser = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<UsersDeleteUserData, ThrowOnError>,
) => {
  return (options?.client ?? client).delete<
    UsersDeleteUserResponse,
    UsersDeleteUserError,
    ThrowOnError
  >({
    ...options,
    url: "/api/users/{id}",
  });
};

/**
 * Get Keywords
 * 获取关键词列表
 */
export const getKeywords = <ThrowOnError extends boolean = false>(
  options?: OptionsLegacyParser<GetKeywordsData, ThrowOnError>,
) => {
  return (options?.client ?? client).get<
    GetKeywordsResponse,
    GetKeywordsError,
    ThrowOnError
  >({
    ...options,
    url: "/api/keywords/",
  });
};

/**
 * Create Keyword
 * 创建新关键词
 */
export const createKeyword = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<CreateKeywordData, ThrowOnError>,
) => {
  return (options?.client ?? client).post<
    CreateKeywordResponse,
    CreateKeywordError,
    ThrowOnError
  >({
    ...options,
    url: "/api/keywords/",
  });
};

/**
 * Update Keyword
 * 更新关键词
 */
export const updateKeyword = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<UpdateKeywordData, ThrowOnError>,
) => {
  return (options?.client ?? client).put<
    UpdateKeywordResponse,
    UpdateKeywordError,
    ThrowOnError
  >({
    ...options,
    url: "/api/keywords/{keyword_id}",
  });
};

/**
 * Delete Keyword
 * 删除关键词
 */
export const deleteKeyword = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<DeleteKeywordData, ThrowOnError>,
) => {
  return (options?.client ?? client).delete<
    DeleteKeywordResponse,
    DeleteKeywordError,
    ThrowOnError
  >({
    ...options,
    url: "/api/keywords/{keyword_id}",
  });
};

/**
 * Toggle Keyword Status
 * 切换关键词启用/禁用状态
 */
export const toggleKeywordStatus = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<ToggleKeywordStatusData, ThrowOnError>,
) => {
  return (options?.client ?? client).patch<
    ToggleKeywordStatusResponse,
    ToggleKeywordStatusError,
    ThrowOnError
  >({
    ...options,
    url: "/api/keywords/{keyword_id}/toggle",
  });
};

/**
 * Get Categories
 * 获取所有关键词分类
 */
export const getCategories = <ThrowOnError extends boolean = false>(
  options?: OptionsLegacyParser<unknown, ThrowOnError>,
) => {
  return (options?.client ?? client).get<
    GetCategoriesResponse,
    GetCategoriesError,
    ThrowOnError
  >({
    ...options,
    url: "/api/keywords/categories",
  });
};

/**
 * Get Keyword Stats
 * 获取关键词统计信息
 */
export const getKeywordStats = <ThrowOnError extends boolean = false>(
  options?: OptionsLegacyParser<unknown, ThrowOnError>,
) => {
  return (options?.client ?? client).get<
    GetKeywordStatsResponse,
    GetKeywordStatsError,
    ThrowOnError
  >({
    ...options,
    url: "/api/keywords/stats",
  });
};

/**
 * Receive Xhs Webhook
 * 接收小红书爬虫结果的webhook端点
 */
export const receiveXhsWebhook = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<ReceiveXhsWebhookData, ThrowOnError>,
) => {
  return (options?.client ?? client).post<
    ReceiveXhsWebhookResponse,
    ReceiveXhsWebhookError,
    ThrowOnError
  >({
    ...options,
    url: "/api/webhook/xhs-result",
  });
};

/**
 * Test Webhook
 * 测试webhook端点
 */
export const testWebhook = <ThrowOnError extends boolean = false>(
  options?: OptionsLegacyParser<unknown, ThrowOnError>,
) => {
  return (options?.client ?? client).post<
    TestWebhookResponse,
    TestWebhookError,
    ThrowOnError
  >({
    ...options,
    url: "/api/webhook/test",
  });
};

/**
 * Get Notes Stats
 * 获取笔记统计信息
 */
export const getNotesStats = <ThrowOnError extends boolean = false>(
  options?: OptionsLegacyParser<unknown, ThrowOnError>,
) => {
  return (options?.client ?? client).get<
    GetNotesStatsResponse,
    GetNotesStatsError,
    ThrowOnError
  >({
    ...options,
    url: "/api/notes/stats",
  });
};

/**
 * Search Notes
 * 搜索和筛选笔记 - 支持分页、筛选和排序
 */
export const searchNotes = <ThrowOnError extends boolean = false>(
  options?: OptionsLegacyParser<SearchNotesData, ThrowOnError>,
) => {
  return (options?.client ?? client).get<
    SearchNotesResponse,
    SearchNotesError,
    ThrowOnError
  >({
    ...options,
    url: "/api/notes/",
  });
};

/**
 * Get Note Detail
 * 获取单个笔记详情
 */
export const getNoteDetail = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<GetNoteDetailData, ThrowOnError>,
) => {
  return (options?.client ?? client).get<
    GetNoteDetailResponse,
    GetNoteDetailError,
    ThrowOnError
  >({
    ...options,
    url: "/api/notes/{note_id}",
  });
};

/**
 * Soft Delete Note Endpoint
 * 软删除一个笔记
 */
export const softDeleteNoteEndpoint = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<SoftDeleteNoteEndpointData, ThrowOnError>,
) => {
  return (options?.client ?? client).delete<
    SoftDeleteNoteEndpointResponse,
    SoftDeleteNoteEndpointError,
    ThrowOnError
  >({
    ...options,
    url: "/api/notes/{note_id}",
  });
};

/**
 * Trigger Crawl Task
 * 触发爬取任务
 */
export const triggerCrawlTask = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<TriggerCrawlTaskData, ThrowOnError>,
) => {
  return (options?.client ?? client).post<
    TriggerCrawlTaskResponse,
    TriggerCrawlTaskError,
    ThrowOnError
  >({
    ...options,
    url: "/api/tasks/trigger-crawl",
  });
};

/**
 * Get Tasks
 * 获取任务列表
 */
export const getTasks = <ThrowOnError extends boolean = false>(
  options?: OptionsLegacyParser<GetTasksData, ThrowOnError>,
) => {
  return (options?.client ?? client).get<
    GetTasksResponse,
    GetTasksError,
    ThrowOnError
  >({
    ...options,
    url: "/api/tasks/",
  });
};

/**
 * Create Task
 * 创建新任务
 */
export const createTask = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<CreateTaskData, ThrowOnError>,
) => {
  return (options?.client ?? client).post<
    CreateTaskResponse,
    CreateTaskError,
    ThrowOnError
  >({
    ...options,
    url: "/api/tasks/",
  });
};

/**
 * Get Task Stats
 * 获取任务统计信息
 */
export const getTaskStats = <ThrowOnError extends boolean = false>(
  options?: OptionsLegacyParser<unknown, ThrowOnError>,
) => {
  return (options?.client ?? client).get<
    GetTaskStatsResponse,
    GetTaskStatsError,
    ThrowOnError
  >({
    ...options,
    url: "/api/tasks/stats",
  });
};

/**
 * Get Task Detail
 * 获取任务详情
 */
export const getTaskDetail = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<GetTaskDetailData, ThrowOnError>,
) => {
  return (options?.client ?? client).get<
    GetTaskDetailResponse,
    GetTaskDetailError,
    ThrowOnError
  >({
    ...options,
    url: "/api/tasks/detail/{task_id}",
  });
};

/**
 * Cancel Task
 * 取消任务
 */
export const cancelTask = <ThrowOnError extends boolean = false>(
  options: OptionsLegacyParser<CancelTaskData, ThrowOnError>,
) => {
  return (options?.client ?? client).delete<
    CancelTaskResponse,
    CancelTaskError,
    ThrowOnError
  >({
    ...options,
    url: "/api/tasks/{task_id}",
  });
};
