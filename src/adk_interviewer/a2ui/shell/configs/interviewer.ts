/*
 AI Interviewer A2UI Frontend Configuration
 v4.7.1 - Enhanced Conversation Experience
 */

import { AppConfig } from "./types.js";

export const config: AppConfig = {
    key: "interviewer",
    title: "AI Technical Interviewer",
    heroImage: "/interviewer-hero.png",
    heroImageDark: "/interviewer-hero-dark.png",
    background: `radial-gradient(
    at 0% 0%,
    light-dark(rgba(66, 133, 244, 0.3), rgba(66, 133, 244, 0.15)) 0px,
    transparent 50%
  ),
  radial-gradient(
    at 100% 0%,
    light-dark(rgba(234, 67, 53, 0.2), rgba(234, 67, 53, 0.1)) 0px,
    transparent 50%
  ),
  radial-gradient(
    at 100% 100%,
    light-dark(rgba(251, 188, 5, 0.2), rgba(251, 188, 5, 0.1)) 0px,
    transparent 50%
  ),
  radial-gradient(
    at 0% 100%,
    light-dark(rgba(52, 168, 83, 0.2), rgba(52, 168, 83, 0.1)) 0px,
    transparent 50%
  ),
  linear-gradient(
    120deg,
    light-dark(#f8f9fa, #0f172a) 0%,
    light-dark(#e8eaed, #1e293b) 100%
  )`,
    // Conversation-optimized messages
    placeholder: "Type your answer or question...",
    loadingText: [
        "Analyzing your response...",
        "Preparing personalized feedback...",
        "Thinking about the next challenge...",
        "Evaluating your approach...",
    ],
    // A2A Bridge server URL - connects to ADK via bridge
    serverUrl: "http://localhost:10002",
};
