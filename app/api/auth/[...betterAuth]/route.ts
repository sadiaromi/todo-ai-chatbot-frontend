import { auth } from "../../../../auth.config";

// Destructure the handlers based on what's available in the auth object
const handlers = auth.handlers || auth;

// Export the required methods
export const GET = handlers.GET || handlers.get;
export const POST = handlers.POST || handlers.post;