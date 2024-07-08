import { z } from "zod";
import { getBaseURL } from "./utils";

export const SUCCESS_MESSAGE = "Account verified successfully";
// Rag config scheme
export const UserSchema = z.object({
  id: z.string().optional(),
  first_name: z.string(),
  last_name: z.string(),
  email: z.string(),
  password: z.string().optional(),
  phone_number: z.string(),
  sex: z.string().optional(),
  role: z.string().optional(),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
  deleted_at: z.string().optional(),
  status: z.string().optional(),
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
  otp_type: z.string()
});

export const ResetPasswordSchema = z.object({
  code: z.string(),
  email: z.string(),
  otp_type: z.string(),
  password: z.string()
});

export const ResetPasswordFormSchema = z.object({
  new_password: z.string().min(6, "Password must be at least 6 characters long"),
  confirm_password: z.string().min(6, "Password must be at least 6 characters long")
}).refine(data => data.new_password === data.confirm_password, {
  message: "Passwords do not match",
  path: ["confirm_password"] // path of error
});

export type UserFormType = z.TypeOf<typeof UserSchema>;
export type UserSigninType = z.TypeOf<typeof UserSigninSchema>;
export type VerifyOtpType = z.TypeOf<typeof VerifyOtpSchema>;
export type ForgotPasswordType = z.TypeOf<typeof ForgotPasswordSchema>;
export type ResetPasswordType = z.TypeOf<typeof ResetPasswordSchema>;

export async function createUserAccount(
  data: UserFormType,
): Promise<UserFormType> {
  // Ignore configured attribute
  const { password, ...userData} = data;

  const res = await fetch(`${getBaseURL()}/api/auth/accounts/create`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      password,
      user_data: userData
    }),
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(error);
  }
  return (await res.json()) as UserFormType;
}

export async function signIn(
  data: UserSigninType,
): Promise<{ access_token: string; token_type: string; user: UserFormType, message: string; }> {
  // Ignore configured attribute

  const formData = new URLSearchParams();
  formData.append('username', data.email);
  formData.append('password', data.password);

  const res = await fetch(`${getBaseURL()}/api/auth/accounts/signin`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData.toString(),
  });

  if (!res.ok) {
    const error = await res.text();
    throw new Error(error);
  }

  return (await res.json()) as { access_token: string; token_type: string; user: UserFormType, message: string; };
}

export async function signOut(access_token: string): Promise<{ message: string; }> {
  const res = await fetch(`${getBaseURL()}/api/auth/accounts/signout`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${access_token}`
    },
  });

  if (!res.ok) {
    const error = await res.text();
    throw new Error(error);
  }

  return (await res.json()) as { message: string; };
}


export async function getChatMode(user_id: string, access_token: string): Promise<{ mode: boolean;  }> {
  const res = await fetch(`${getBaseURL()}/api/chat/chat-mode/${user_id}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${access_token}`
    },
  });

  if (!res.ok) {
    const error = await res.text();
    throw new Error(error);
  }

  return (await res.json()) as { mode: boolean; };
}

export async function updateChatMode(checked: boolean, user_id: string, access_token: string): Promise<{ message: string;  }> {
  const res = await fetch(`${getBaseURL()}/api/chat/chat-mode/${user_id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${access_token}`
    },
    body: JSON.stringify({is_research_exploration: checked})
  });

  if (!res.ok) {
    const error = await res.text();
    throw new Error(error);
  }

  return (await res.json()) as { message: string; };
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
    body: JSON.stringify(data)
  });

  if (!res.ok) {
    const error = await res.text();
    return { message: error, status: 400 }
  }

  return { ...((await res.json()) as { message: string; status: number })};
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
    body: JSON.stringify(data)
  });

  if (!res.ok) {
    const error = await res.text();
    return { message: error, status: 400 }
  }

  return { ...((await res.json()) as { message: string; status: number })};
}


export async function resendActivationOtp(
  data: string,
): Promise<{ message: string; status: number }> {
  // Ignore configured attribute

  const res = await fetch(`${getBaseURL()}/api/auth/accounts/resend-otp/${data}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    }
  });

  if (!res.ok) {
    const error = await res.text();
    return { message: error, status: 400 }
  }

  return { ...((await res.json()) as { message: string; status: number })};
}

export async function resetPassword(data: ResetPasswordType){
  const { password, ...verifyPasswordData } = data;
  const response = await verifyOtp(verifyPasswordData)

  if(response.status === 200){    
    const res = await fetch(`${getBaseURL()}/api/auth/accounts/reset-password`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: verifyPasswordData.email,
        password
      })
    });

    if (!res.ok) {
      const error = await res.text();
      return { message: error, status: 400 }
    }

    return { ...((await res.json()) as { message: string; status: number })};
  }

  return response;
}