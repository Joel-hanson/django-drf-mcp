# Complete MCP Conversation Flow: Request → Response

## 1. Claude starts connection

**Request:**

```http
POST /mcp/ HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json
Content-Length: 198

{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{"roots":{"listChanged":true},"sampling":{}},"clientInfo":{"name":"claude-desktop","version":"0.7.0"}}}
```

**Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 145

{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{"listChanged":false}},"serverInfo":{"name":"django-drf-mcp","version":"1.0.0"}}}
```

---

## 2. Claude discovers tools

**Request:**

```http
POST /mcp/ HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json
Content-Length: 59

{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
```

**Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 980

{"jsonrpc":"2.0","id":2,"result":{"tools":[{"name":"list_users_user","description":"List User in users","inputSchema":{"type":"object","properties":{},"additionalProperties":false}},{"name":"create_users_user","description":"Create User in users","inputSchema":{"type":"object","properties":{"username":{"type":"string","maxLength":150,"description":"Username"},"email":{"type":"string","format":"email","description":"Email"},"password":{"type":"string","description":"Password"}},"required":["username","email","password"],"additionalProperties":false}},{"name":"retrieve_users_user","description":"Retrieve User in users","inputSchema":{"type":"object","properties":{"id":{"type":"string","description":"ID of the object to retrieve"}},"required":["id"],"additionalProperties":false}},{"name":"update_users_user","description":"Update User in users","inputSchema":{"type":"object","properties":{"id":{"type":"string","description":"ID of the object to update"},"username":{"type":"string","maxLength":150},"email":{"type":"string","format":"email"},"password":{"type":"string"}},"required":["id"],"additionalProperties":false}},{"name":"destroy_users_user","description":"Destroy User in users","inputSchema":{"type":"object","properties":{"id":{"type":"string","description":"ID of the object to destroy"}},"required":["id"],"additionalProperties":false}},{"name":"activate_users_user","description":"Activate User in users","inputSchema":{"type":"object","properties":{"id":{"type":"string","description":"ID of the object to perform action on"}},"required":["id"],"additionalProperties":false}}]}}
```

---

## 3. User asks: "Show me all users"

**Request:**

```http
POST /mcp/ HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json
Content-Length: 108

{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"list_users_user","arguments":{}}}
```

**Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 245

{"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text","text":"Found 3 users:\n\n1. User ID: 1\n   - Username: admin\n   - Email: admin@example.com\n   - Active: True\n\n2. User ID: 2\n   - Username: johndoe\n   - Email: john@example.com\n   - Active: True\n\n3. User ID: 3\n   - Username: testuser\n   - Email: test@example.com\n   - Active: False"}]}}
```

---

## 4. User asks: "Create a user named bob with email bob@test.com"

**Request:**

```http
POST /mcp/ HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json
Content-Length: 150

{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"create_users_user","arguments":{"username":"bob","email":"bob@test.com","password":"password123"}}}
```

**Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 178

{"jsonrpc":"2.0","id":4,"result":{"content":[{"type":"text","text":"Successfully created user:\n\nUser ID: 4\n- Username: bob\n- Email: bob@test.com\n- Active: True\n- Created: 2025-08-04 15:30:22"}]}}
```

---

## 5. User asks: "Activate user with ID 3"

**Request:**

```http
POST /mcp/ HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json
Content-Length: 110

{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"activate_users_user","arguments":{"id":"3"}}}
```

**Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 145

{"jsonrpc":"2.0","id":5,"result":{"content":[{"type":"text","text":"Successfully executed activate action:\n\nResponse: {\"status\": \"user activated\"}\n\nUser ID 3 has been activated."}]}}
```

---

## 6. Error Example: Invalid Tool Call

**Request:**

```http
POST /mcp/ HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json
Content-Length: 105

{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"nonexistent_tool","arguments":{}}}
```

**Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 85

{"jsonrpc":"2.0","id":6,"error":{"code":-32601,"message":"Unknown tool: nonexistent_tool"}}
```

---

## 7. Error Example: Missing Required Fields

**Request:**

```http
POST /mcp/ HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json
Content-Length: 112

{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"create_users_user","arguments":{"username":"incomplete"}}}
```

**Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 210

{"jsonrpc":"2.0","id":7,"error":{"code":-32602,"message":"Tool execution failed: {'email': [ErrorDetail(string='This field is required.', code='required')], 'password': [ErrorDetail(string='This field is required.', code='required')]}"}}
```
