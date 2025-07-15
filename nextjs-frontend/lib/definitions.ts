import { z } from "zod";

const passwordSchema = z
  .string()
  .min(8, "Password should be at least 8 characters.") // Minimum length validation
  .refine((password) => /[A-Z]/.test(password), {
    message: "Password should contain at least one uppercase letter.",
  }) // At least one uppercase letter
  .refine((password) => /[!@#$%^&*(),.?":{}|<>]/.test(password), {
    message: "Password should contain at least one special character.",
  });

export const passwordResetConfirmSchema = z
  .object({
    password: passwordSchema,
    passwordConfirm: z.string(),
    token: z.string({ required_error: "Token is required" }),
  })
  .refine((data) => data.password === data.passwordConfirm, {
    message: "Passwords must match.",
    path: ["passwordConfirm"],
  });

export const registerSchema = z.object({
  password: passwordSchema,
  email: z.string().email({ message: "Invalid email address" }),
});

export const loginSchema = z.object({
  password: z.string().min(1, { message: "Password is required" }),
  username: z.string().min(1, { message: "Username is required" }),
});

export const itemSchema = z.object({
  name: z.string().min(1, { message: "Name is required" }),
  description: z.string().min(1, { message: "Description is required" }),
  quantity: z
    .string()
    .min(1, { message: "Quantity is required" })
    .transform((val) => parseInt(val, 10)) // Convert to integer
    .refine((val) => Number.isInteger(val) && val > 0, {
      message: "Quantity must be a positive integer",
    }),
});

export const keywordSchema = z.object({
  keyword: z.string().min(1, { message: "Keyword is required" }),
  category: z.string().optional(),
  weight: z
    .string()
    .optional()
    .transform((val) => (val ? parseInt(val, 10) : 1)) // Convert to integer, default to 1
    .refine((val) => Number.isInteger(val) && val >= 1 && val <= 10, {
      message: "Weight must be an integer between 1 and 10",
    }),
  is_active: z.boolean().optional().default(true),
  description: z.string().optional(),
});

export const noteSchema = z.object({
  title: z.string().optional(),
  desc: z.string().optional(),
  is_important: z.boolean().optional(),
  tags: z.array(z.string()).optional(),
});

export const noteQuerySchema = z.object({
  keyword: z.string().optional(),
  is_new: z.boolean().optional(),
  is_changed: z.boolean().optional(),
  is_important: z.boolean().optional(),
  author_user_id: z.string().optional(),
  limit: z.number().min(1).max(1000).optional().default(50),
  offset: z.number().min(0).optional().default(0),
  today_only: z.boolean().optional().default(true),
});

export type NotesQueryParams = z.infer<typeof noteQuerySchema>;
