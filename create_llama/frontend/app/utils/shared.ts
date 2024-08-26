// utils/shared.ts

import jwt from "jsonwebtoken";
import { getCookie } from "../service/user-service";

export default function base64ToString(base64String: string): string {
  const binaryString = atob(base64String);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return new TextDecoder().decode(bytes);
}

/**
 * Decodes a JWT token and returns the decoded payload as a string.
 * @param {string} token - The JWT token to decode.
 * @param {string} secret - The secret or public key used to decode the token.
 * @returns {string} - The decoded payload as a string.
 */
export const decodeToken = (token: string) => {
  try {
    // Decode the token without verifying the signature
    const decoded = jwt.decode(token);
    // Convert the decoded payload to a string
    return decoded;
  } catch (error) {
    console.error("Failed to decode token:", error);
    return {};
  }
};

export function getAccessToken() {
  return localStorage
    ? localStorage.getItem("access_token") || getCookie("access_token")
    : "";
}
