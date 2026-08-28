"use client";

/**
 * Small localStorage wrapper used in this learning phase. The token is kept in
 * browser storage so the mechanics are visible; a production app should prefer
 * short-lived access tokens and a secure, HttpOnly refresh-token cookie to
 * reduce XSS exposure.
 */
const ACCESS_TOKEN_KEY = "bizreg.access_token";
const REFRESH_TOKEN_KEY = "bizreg.refresh_token";

export type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
};

export function getApiUrl(): string {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  if (!apiUrl) {
    throw new Error(
      "BizReg API URL is not configured. Add NEXT_PUBLIC_API_URL to frontend/.env and restart Next.js."
    );
  }
  return apiUrl;
}

export async function readApiBody(response: Response): Promise<{ detail?: string } & Record<string, unknown>> {
  // Calling response.json() blindly hides configuration/proxy mistakes behind
  // “Unexpected token <”. Read HTML/text responses safely and explain the fix.
  if (!response.headers.get("content-type")?.includes("application/json")) {
    return { detail: "The API returned HTML instead of JSON. Confirm the API is running and frontend/.env points to it." };
  }
  return response.json() as Promise<{ detail?: string } & Record<string, unknown>>;
}

export function saveTokens(tokens: TokenPair) {
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
}

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export async function apiFetch(path: string, init: RequestInit = {}) {
  const token = getAccessToken();
  const response = await fetch(`${getApiUrl()}${path}`, {
    ...init,
    headers: {
      ...init.headers,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  return response;
}
