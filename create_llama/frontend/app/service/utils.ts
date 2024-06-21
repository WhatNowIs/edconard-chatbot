export function getBackendURL(): string {
    return process.env.NEXT_PUBLIC_BACKEND_URL as string;
    // If we are in development, use the local backend endpoint
    // if (process.env.ENVIRONMENT === "dev") {
    //   return "http://localhost:8000";
    // }
    // return typeof window !== "undefined" ? window.location.origin : "";
}

export function getBaseURL(): string {
    return process.env.NEXT_PUBLIC_BACKEND_URL as string;
}
  