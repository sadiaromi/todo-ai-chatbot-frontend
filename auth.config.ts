import { betterAuth } from "better-auth";

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET || "your-default-secret-change-in-production",
  plugins: [],
});