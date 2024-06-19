import { z } from "zod";
import { getBaseURL } from "./utils";
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

export type UserFormType = z.TypeOf<typeof UserSchema>;
export type UserSigninType = z.TypeOf<typeof UserSigninSchema>;

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
  return (await res.json()).data as UserFormType;
}

export async function signIn(
  data: UserSigninType,
): Promise<{ message: string; }> {
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

  return (await res.json()).data as { message: string; };
}
