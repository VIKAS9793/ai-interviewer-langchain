"""
A2A Protocol Bridge for ADK

This module bridges the A2A (Agent-to-Agent) protocol used by A2UI
with the ADK (Agent Development Kit) protocol.

v4.7.0: Initial A2UI integration.
v4.7.1: Fixed function call handling, empty response handling.
v5.0.0: Rich A2UI components (Card layout, markdown support).

Architecture:
  A2UI Frontend (localhost:3000)
       |
       v (A2A protocol)
  A2A Bridge (localhost:10002)
       |
       v (ADK protocol)
  ADK Backend (localhost:8000)
"""


import asyncio
import json
import logging
import uuid
from typing import Any

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="A2A-ADK Bridge", version="0.1.0")

# CORS for A2UI frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ADK backend configuration
ADK_BASE_URL = "http://localhost:8000"
ADK_APP_NAME = "adk_interviewer"

# Session storage for conversation persistence (v4.7.1)
# Maps user_id -> session_id to maintain conversation across turns
user_sessions: dict[str, str] = {}

# A2A Agent Card (required by A2UI client)
AGENT_CARD = {
    "name": "AI Technical Interviewer",
    "description": "Technical interview assistant powered by Google ADK and Gemini",
    "version": "4.7.0",
    "url": "http://localhost:10002",
    "capabilities": {
        "streaming": False,
        "pushNotifications": False,
    },
    "skills": [
        {
            "id": "interview",
            "name": "Technical Interview",
            "description": "Conduct technical interviews with adaptive questions",
        },
        {
            "id": "code_analysis",
            "name": "Code Analysis",
            "description": "Analyze and review Python code",
        },
    ],
    "extensions": [
        {
            "uri": "https://a2ui.org/a2a-extension/a2ui/v0.8",
            "required": True,
        }
    ],
}


@app.get("/.well-known/agent-card.json")
async def get_agent_card():
    """A2A protocol: Agent discovery endpoint."""
    logger.info("Agent card requested")
    return JSONResponse(content=AGENT_CARD)


@app.post("/")
@app.post("/task/send")
async def send_task(request: Request):
    """
    A2A protocol: Handle task/send requests from A2UI client.
    Translates to ADK protocol and returns A2UI-formatted response.
    """
    try:
        body = await request.json()
        logger.info(f"Received A2A request: {json.dumps(body, indent=2)[:500]}")
        
        # Extract user message from A2A format
        user_message = extract_user_message(body)
        logger.info(f"Extracted message: {user_message}")
        
        # Forward to ADK backend
        adk_response = await forward_to_adk(user_message)
        logger.info(f"ADK response: {adk_response[:500] if adk_response else 'None'}")
        
        # Parse A2UI JSON from ADK response
        a2ui_messages = parse_a2ui_from_response(adk_response)
        
        # Format as A2A task response
        response = format_a2a_response(body, adk_response, a2ui_messages)
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "internal_error", "message": str(e)}}
        )


def extract_user_message(body: dict) -> str:
    """Extract user message from A2A request format (JSON-RPC)."""
    # Handle JSON-RPC format: {"jsonrpc": "2.0", "method": "message/send", "params": {...}}
    if "params" in body:
        params = body["params"]
        message = params.get("message", {})
    else:
        message = body.get("message", {})
    
    parts = message.get("parts", [])
    
    for part in parts:
        if part.get("kind") == "text":
            return part.get("text", "")
        if part.get("kind") == "data":
            # Handle A2UI client events
            data = part.get("data", {})
            if "userAction" in data:
                action = data["userAction"]
                return f"User action: {action.get('name', 'unknown')}"
    
    return ""


async def forward_to_adk(message: str) -> str:
    """Forward message to ADK backend and get response.
    
    v4.7.1: Sessions are now persistent per user for conversation continuity.
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        user_id = "a2ui_user"
        
        # Reuse existing session or create new one (v4.7.1 - conversation persistence)
        is_new_session = user_id not in user_sessions
        if is_new_session:
            user_sessions[user_id] = str(uuid.uuid4())
        session_id = user_sessions[user_id]
        
        logger.info(f"Session: {session_id} ({'new' if is_new_session else 'existing'})")
        
        # Step 1: Create session on first message only
        if is_new_session:
            session_url = f"{ADK_BASE_URL}/apps/{ADK_APP_NAME}/users/{user_id}/sessions/{session_id}"
            logger.info(f"Creating session at: {session_url}")
            
            try:
                session_response = await client.post(session_url, json={"state": {}})
                logger.info(f"Session creation response: {session_response.status_code}")
            except httpx.HTTPError as e:
                logger.warning(f"Session creation failed (may not be required): {e}")
        
        # Step 2: Send message via run_sse (streaming) endpoint
        run_url = f"{ADK_BASE_URL}/run_sse"
        
        payload = {
            "app_name": ADK_APP_NAME,
            "user_id": user_id,
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": message}]
            },
            "streaming": False
        }
        
        logger.info(f"Forwarding to ADK: {run_url}")
        logger.info(f"Payload: {json.dumps(payload)}")
        
        try:
            response = await client.post(run_url, json=payload)
            
            # If run_sse fails, try direct session message endpoint
            if response.status_code == 404:
                logger.info("run_sse not found, trying session message endpoint")
                msg_url = f"{ADK_BASE_URL}/apps/{ADK_APP_NAME}/users/{user_id}/sessions/{session_id}"
                response = await client.post(msg_url, json={"message": message})
            
            logger.info(f"ADK response status: {response.status_code}")
            
            if response.status_code == 404:
                # Last resort: Check available endpoints
                return f"ADK endpoint not found. Status: {response.status_code}. Try 'adk api_server src' instead of 'adk web src' for REST API."
            
            response.raise_for_status()
            
            # Handle SSE response format (text/event-stream)
            content_type = response.headers.get("content-type", "")
            if "text/event-stream" in content_type:
                # Parse SSE events
                text = response.text
                logger.info(f"SSE response: {text[:500]}")
                
                # Extract JSON data from SSE format
                full_text = []
                has_function_call = False
                for line in text.split('\n'):
                    if line.startswith('data:'):
                        try:
                            data = json.loads(line[5:].strip())
                            # Check for error response (e.g., 429 quota exceeded)
                            if "error" in data:
                                error_info = data.get("error", "Unknown error")
                                logger.warning(f"ADK returned error: {error_info}")
                                return f"⚠️ API Error: The service is temporarily unavailable. Please try again in a moment. (Rate limit may have been exceeded)"
                            if "content" in data:
                                parts = data["content"].get("parts", [])
                                for part in parts:
                                    if "text" in part:
                                        full_text.append(part["text"])
                                    elif "functionCall" in part:
                                        # ADK internal function call (e.g., transfer_to_agent)
                                        # This is an internal operation, wait for next response
                                        func_name = part["functionCall"].get("name", "unknown")
                                        logger.info(f"ADK function call: {func_name}")
                                        has_function_call = True
                        except json.JSONDecodeError:
                            # Handle non-JSON data lines (like error strings)
                            data_content = line[5:].strip()
                            if data_content.startswith('"error"') or 'error' in data_content.lower():
                                logger.warning(f"SSE error line: {data_content[:200]}")
                                return f"⚠️ Service temporarily unavailable. Please try again."
                if full_text:
                    return ''.join(full_text)
                elif has_function_call:
                    # Only function call, no text - return processing message
                    return "Processing your request... (internal routing)"
                else:
                    # Empty response from ADK (no text, no function call)
                    logger.warning("ADK returned empty content response")
                    return "I'm processing your input. Please continue with your next question."

            # Only reach here if NOT text/event-stream

            logger.info(f"ADK raw response: {json.dumps(data)[:1000] if isinstance(data, (dict, list)) else str(data)[:1000]}")
            
            # Extract response text from ADK format
            if isinstance(data, list):
                # ADK returns list of events
                for event in data:
                    if isinstance(event, dict):
                        content = event.get("content", {})
                        parts = content.get("parts", [])
                        for part in parts:
                            if isinstance(part, dict) and "text" in part:
                                return part["text"]
            elif isinstance(data, dict):
                # Handle single response
                if "content" in data:
                    content = data["content"]
                    if isinstance(content, dict):
                        parts = content.get("parts", [])
                        for part in parts:
                            if isinstance(part, dict) and "text" in part:
                                return part["text"]
                if "response" in data:
                    return data["response"]
                if "text" in data:
                    return data["text"]
                # Return full JSON if format unknown
                return json.dumps(data)
            
            return str(data)
            
        except httpx.HTTPError as e:
            logger.error(f"ADK request failed: {e}")
            return f"Error connecting to ADK: {e}"


def parse_a2ui_from_response(response: str) -> list[dict[str, Any]]:
    """Parse A2UI JSON from response if present."""
    if not response or "---a2ui_JSON---" not in response:
        return []
    
    try:
        _, json_part = response.split("---a2ui_JSON---", 1)
        json_str = json_part.strip()
        
        # Clean markdown code blocks
        if json_str.startswith("```"):
            json_str = json_str.lstrip("```json").lstrip("```").rstrip("```").strip()
        
        return json.loads(json_str)
    except (ValueError, json.JSONDecodeError) as e:
        logger.warning(f"Failed to parse A2UI JSON: {e}")
        return []


def format_a2a_response(
    request: dict, 
    text_response: str, 
    a2ui_messages: list[dict]
) -> dict:
    """Format response in A2A JSON-RPC format with A2UI extension."""
    task_id = str(uuid.uuid4())
    surface_id = "interview-surface"
    
    # Build response parts
    parts = []
    
    # Clean text (remove A2UI JSON if present)
    clean_text = text_response
    if "---a2ui_JSON---" in text_response:
        clean_text = text_response.split("---a2ui_JSON---")[0].strip()
    
    # Always add text as a regular part
    if clean_text:
        parts.append({
            "kind": "text",
            "text": clean_text
        })
    
    # Generate A2UI messages for rendering
    # Enhanced v5.0: Use Card components with proper styling
    if not a2ui_messages and clean_text:
        # Detect if response contains code blocks for special handling
        has_code = "```" in clean_text
        
        # Build rich A2UI component tree
        components = [
            {
                "id": "root-container",
                "componentProperties": {
                    "Column": {
                        "children": {
                            "explicitList": ["response-card"]
                        }
                    }
                }
            },
            {
                "id": "response-card",
                "componentProperties": {
                    "Card": {
                        "child": "card-content"
                    }
                }
            },
            {
                "id": "card-content",
                "componentProperties": {
                    "Column": {
                        "children": {
                            "explicitList": ["text-response"]
                        }
                    }
                }
            },
            {
                "id": "text-response",
                "componentProperties": {
                    "Text": {
                        "text": {
                            "literalString": clean_text
                        },
                        "usageHint": "body"
                    }
                }
            }
        ]
        
        a2ui_messages = [
            {
                "beginRendering": {
                    "surfaceId": surface_id,
                    "root": "root-container"
                }
            },
            {
                "surfaceUpdate": {
                    "surfaceId": surface_id,
                    "components": components
                }
            }
        ]
    
    # Add A2UI data parts
    for msg in a2ui_messages:
        parts.append({
            "kind": "data",
            "mimeType": "application/json+a2aui",
            "data": msg
        })
    
    # Get request id for JSON-RPC response
    request_id = request.get("id", 1)
    
    # Build JSON-RPC 2.0 compliant response
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "kind": "task",
            "id": task_id,
            "status": {
                "state": "completed",
                "message": {
                    "messageId": str(uuid.uuid4()),
                    "role": "agent",
                    "parts": parts,
                    "kind": "message"
                }
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("A2A-ADK Bridge Server")
    print("=" * 60)
    print(f"Bridge:   http://localhost:10002")
    print(f"ADK:      {ADK_BASE_URL}")
    print(f"A2UI:     http://localhost:3000/?app=interviewer")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=10002)
