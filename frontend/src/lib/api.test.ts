import {
  afterEach,
  describe,
  expect,
  it,
} from "vitest";

import {
  apiUrl,
  getApiBaseUrl,
} from "./api";


describe("API URL configuration", () => {
  const originalBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

  afterEach(() => {
    if (originalBaseUrl === undefined) {
      delete process.env.NEXT_PUBLIC_API_BASE_URL;
    } else {
      process.env.NEXT_PUBLIC_API_BASE_URL = originalBaseUrl;
    }
  });


  it("defaults to the local backend", () => {
    delete process.env.NEXT_PUBLIC_API_BASE_URL;

    expect(getApiBaseUrl()).toBe("http://localhost:8000");
    expect(apiUrl("/health")).toBe("http://localhost:8000/health");
  });


  it("uses and normalizes the configured production backend URL", () => {
    process.env.NEXT_PUBLIC_API_BASE_URL = " https://api.example.com/// ";

    expect(getApiBaseUrl()).toBe("https://api.example.com");
    expect(apiUrl("/research")).toBe("https://api.example.com/research");
  });
});