import { z } from "zod";
import { Article } from "../utils/multi-mode-select";
import { getBaseURL } from "./utils";

export const SUCCESS_MESSAGE = "Account verified successfully";

export const RoleSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
});
// Rag config scheme
export const UserSchema = z.object({
  id: z.string().optional(),
  first_name: z.string(),
  last_name: z.string(),
  email: z.string(),
  password: z.string().optional(),
  phone_number: z.string(),
  sex: z.string().optional(),
  role_id: z.string().optional(),
  role: RoleSchema.optional(),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
  deleted_at: z.string().optional(),
  status: z.string().optional(),
});

export const ChangePasswordSchema = z
  .object({
    current_password: z
      .string()
      .min(1, { message: "Current password is required" }),
    new_password: z
      .string()
      .min(8, { message: "New password must be at least 8 characters long" }),
    confirm_password: z.string().min(8, {
      message: "Confirm password must be at least 8 characters long",
    }),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "Passwords don't match",
    path: ["confirm_password"], // This will set the error on the confirm_password field
  });

export const MacroRoundupSchema = z.object({
  document_link: z.string(),
  order: z.string(),
});

export const AddMessageSchema = z.object({
  role: z.string(),
  content: z.string(),
});

export const UpdateMessagesSchema = z.object({
  messages: z.array(AddMessageSchema),
  thread_id: z.string(),
});

export const UserSigninSchema = z.object({
  email: z.string(),
  password: z.string(),
});

export const ForgotPasswordSchema = z.object({
  email: z.string(),
});

export const VerifyAccountSchema = z.object({
  code: z.string(),
});

export const VerifyOtpSchema = z.object({
  code: z.string(),
  email: z.string(),
  otp_type: z.string(),
});

export const ResetPasswordSchema = z.object({
  code: z.string(),
  email: z.string(),
  otp_type: z.string(),
  password: z.string(),
});

export const ResetPasswordFormSchema = z
  .object({
    new_password: z
      .string()
      .min(6, "Password must be at least 6 characters long"),
    confirm_password: z
      .string()
      .min(6, "Password must be at least 6 characters long"),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"], // path of error
  });

export type UserFormType = z.TypeOf<typeof UserSchema>;
export type UserSigninType = z.TypeOf<typeof UserSigninSchema>;
export type VerifyOtpType = z.TypeOf<typeof VerifyOtpSchema>;
export type ForgotPasswordType = z.TypeOf<typeof ForgotPasswordSchema>;
export type ResetPasswordType = z.TypeOf<typeof ResetPasswordSchema>;
export type MacroRoundupType = z.TypeOf<typeof MacroRoundupSchema>;
export type ChangePasswordType = z.infer<typeof ChangePasswordSchema>;
export type UpdateMessagesType = z.infer<typeof UpdateMessagesSchema>;

export async function createUserAccount(
  data: UserFormType,
): Promise<{ message: string; status: number; data: UserFormType | null }> {
  // Ignore configured attribute
  const { password, ...userData } = data;

  const res = await fetch(`${getBaseURL()}/api/auth/accounts/create`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      password,
      user_data: userData,
    }),
  });
  if (!res.ok) {
    const error = JSON.parse(await res.text());
    return { message: error.detail, status: 400, data: null };
  }
  const result = (await res.json()) as UserFormType;

  return { message: "Account created successfully", status: 200, data: result };
}

interface ErrorResponse {
  user: UserFormType | null;
  message: string;
}
export interface SignInResponse extends ErrorResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export async function signIn(
  data: UserSigninType,
): Promise<SignInResponse | ErrorResponse> {
  // Ignore configured attribute

  const formData = new URLSearchParams();
  formData.append("username", data.email);
  formData.append("password", data.password);

  const res = await fetch(`${getBaseURL()}/api/auth/accounts/signin`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData.toString(),
  });

  if (!res.ok) {
    const error = JSON.parse(await res.text());
    return {
      message: error?.detail,
      user: null,
    };
  }

  return (await res.json()) as {
    access_token: string;
    token_type: string;
    refresh_token: string;
    user: UserFormType;
    message: string;
  };
}

export async function signOut(
  access_token: string,
): Promise<{ message: string }> {
  const res = await fetch(`${getBaseURL()}/api/auth/accounts/signout`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${access_token}`,
    },
  });

  if (!res.ok) {
    const error = await res.text();
    throw new Error(error);
  }

  return (await res.json()) as { message: string };
}

export async function getChatMode(
  user_id: string,
  access_token: string,
): Promise<{ mode: boolean }> {
  const res = await fetch(`${getBaseURL()}/api/chat/chat-mode/${user_id}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${access_token}`,
    },
  });

  if (!res.ok) {
    const error = JSON.parse(await res.text());
    throw new Error(error.detail);
  }

  return (await res.json()) as { mode: boolean };
}

export async function updateChatMode(
  checked: boolean,
  user_id: string,
  access_token: string,
): Promise<{ message: string; status: number }> {
  const res = await fetch(`${getBaseURL()}/api/chat/chat-mode/${user_id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${access_token}`,
    },
    body: JSON.stringify({ is_research_exploration: checked }),
  });

  if (!res.ok) {
    const error = JSON.parse(await res.text());
    return { message: error.detail, status: 400 };
  }

  return (await res.json()) as { message: string; status: number };
}

export async function verifyOtp(
  data: VerifyOtpType,
): Promise<{ message: string; status: number }> {
  // Ignore configured attribute

  console.log(data);

  const res = await fetch(`${getBaseURL()}/api/auth/accounts/verify-otp`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const error = JSON.parse(await res.text());
    return { message: error.detail, status: 400 };
  }

  return { ...((await res.json()) as { message: string; status: number }) };
}

export async function forgotPassword(
  data: ForgotPasswordType,
): Promise<{ message: string; status: number }> {
  // Ignore configured attribute

  const res = await fetch(`${getBaseURL()}/api/auth/accounts/forgot-password`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const error = JSON.parse(await res.text());
    return { message: error.detail, status: 400 };
  }

  return { ...((await res.json()) as { message: string; status: number }) };
}

export async function resendActivationOtp(
  data: string,
): Promise<{ message: string; status: number }> {
  // Ignore configured attribute

  const res = await fetch(
    `${getBaseURL()}/api/auth/accounts/resend-otp/${data}`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    },
  );

  if (!res.ok) {
    const error = JSON.parse(await res.text());
    return { message: error.detail, status: 400 };
  }

  return { ...((await res.json()) as { message: string; status: number }) };
}

export async function resetPassword(data: ResetPasswordType) {
  const { password, ...verifyPasswordData } = data;
  const response = await verifyOtp(verifyPasswordData);

  if (response.status === 200) {
    const res = await fetch(
      `${getBaseURL()}/api/auth/accounts/reset-password`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: verifyPasswordData.email,
          password,
        }),
      },
    );

    if (!res.ok) {
      const error = JSON.parse(await res.text());
      return { message: error.detail, status: 400 };
    }

    return { ...((await res.json()) as { message: string; status: number }) };
  }

  return response;
}
export async function saveMacroRoundupData(
  data: MacroRoundupType,
): Promise<Article | { message: string; status: number }> {
  const access_token =
    localStorage.getItem("access_token") || getCookie("access_token");
  const res = await fetch(`${getBaseURL()}/api/chat/article`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${access_token}`,
    },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const error = JSON.parse(await res.text());
    return { message: error?.detail as string, status: 400 };
  }

  return { ...((await res.json()) as Article) };
}

export async function addChatMessage(data: UpdateMessagesType) {
  const access_token =
    localStorage.getItem("access_token") || getCookie("access_token");
  const res = await fetch(`${getBaseURL()}/api/chat`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${access_token}`,
    },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const error = JSON.parse(await res.text());
    return { message: error.detail, status: 400 };
  }

  return await res.json();
}

export async function getMacroRoundupData(): Promise<
  Article | { message: string; status: number }
> {
  const access_token =
    localStorage.getItem("access_token") || getCookie("access_token");

  const res = await fetch(`${getBaseURL()}/api/chat/article`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${access_token}`,
    },
  });

  if (!res.ok) {
    const error = JSON.parse(await res.text());
    return { message: error?.detail as string, status: 400 };
  }

  return (await res.json()) as Article;
}

export async function refreshToken(token: string): Promise<{
  access_token: string | null;
  token_type: string | null;
}> {
  const res = await fetch(`${getBaseURL()}/api/auth/accounts/refresh`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      refresh_token: token,
    }),
  });

  if (!res.ok) {
    return { access_token: null, token_type: null };
  }

  return {
    ...((await res.json()) as { access_token: string; token_type: string }),
  };
}

export async function changePassword(
  data: ChangePasswordType,
): Promise<{ message: string; status: number }> {
  const access_token =
    localStorage.getItem("access_token") || getCookie("access_token");
  const res = await fetch(`${getBaseURL()}/api/auth/accounts/change-password`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${access_token}`,
    },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const error = JSON.parse(await res.text());
    return { message: error.detail, status: 400 };
  }

  return {
    ...((await res.json()) as { message: string; status: number }),
  };
}

export function getCookie(name: string): string {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);

  if (parts.length === 2) {
    const last = parts.pop() as string;
    return last.split(";").shift() as string;
  } else return "";
}

export async function getUsersNotInWorkspace(
  token: string,
  workspaceId: string,
  options: RequestInit = {},
): Promise<{ message: string; status: number; data: UserFormType[] | null }> {
  const res = await fetch(
    `${getBaseURL()}/api/auth/accounts/users/${workspaceId}`,
    {
      ...options,
      headers: {
        ...options.headers,
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    },
  );

  if (!res.ok) {
    const error = JSON.parse(await res.text());
    return { message: error.detail, status: 400, data: null };
  }

  const response = res.json() as unknown as UserFormType[];

  return { message: "Successfully fetched user", status: 200, data: response };
}
