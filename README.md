# SSE Proxy Test Project

This project consists of three main components to test the behavior of Server-Sent Events (SSE) when using a FastAPI application as a proxy.

## Components

1. **Backend Server**: Emits a dummy SSE stream with the ability to end the stream prematurely to simulate server errors.

2. **FastAPI Proxy App**: Proxies the SSE stream from the backend server to clients. It includes both asynchronous and synchronous endpoints.

3. **Client**: Connects to the FastAPI proxy and consumes the SSE stream with the ability to disconnect prematurely.
