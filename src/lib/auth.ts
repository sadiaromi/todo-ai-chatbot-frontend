import { createAuth } from "better-auth";
import { betterAuthConfig } from "../auth.config";

export const auth = createAuth(betterAuthConfig);