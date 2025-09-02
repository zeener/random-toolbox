# Random Toolbox - Project Structure Documentation

## Current Architecture

### Two-Repository Structure
- **Backend API**: `random-toolbox` (Flask/Python)
- **Frontend UI**: `random-toolbox-ui` (Next.js/React)

### Port Configuration

#### DEV Environment (Direct/Local)
| Service | Port | Access | Command |
|---------|------|--------|---------|
| API | 8001 | http://localhost:8001 | `./start-dev-api.sh` |
| UI | 3001 | http://localhost:3001 | `./start-dev.sh` |

#### INT Environment (Docker)
| Service | External | Internal | Access | Command |
|---------|----------|----------|--------|---------|
| API | 8002 | 8002 | http://localhost:8002 | `./start-int-api.sh` |
| UI | 3002 | 3000 | http://localhost:3002 | `./start-int.sh` |

### Environment Management Scripts

#### API Scripts (random-toolbox)
- `start-dev-api.sh` - Start DEV API server (Flask direct)
- `stop-dev-api.sh` - Stop DEV API server
- `start-int-api.sh` - Start INT API server (Docker)
- `stop-int-api.sh` - Stop INT API server

#### UI Scripts (random-toolbox-ui)
- `start-dev.sh` - Start DEV UI server (Next.js direct)
- `stop-dev.sh` - Stop DEV UI server
- `start-int.sh` - Start INT UI server (Docker)
- `stop-int.sh` - Stop INT UI server

### Key Configuration Files

#### Backend API (random-toolbox)
```python
# src/api/app.py
port = int(os.environ.get('PORT', 8001))
app.run(debug=True, host='0.0.0.0', port=port)
```

#### Frontend UI (random-toolbox-ui)
```bash
# .env.local
NEXT_PUBLIC_API_BASE_URL=/api/proxy
BACKEND_API_URL=http://localhost:8001/api/v1
```

```json
// package.json
"scripts": {
  "dev": "next dev --turbopack --port 3001"
}
```

### Docker Configuration

#### API Docker Compose
```yaml
services:
  random-toolbox-api:
    ports:
      - "8002:8002"
    environment:
      - PORT=8002
```

#### UI Docker Compose
```yaml
services:
  random-toolbox-ui:
    ports:
      - "3002:3000"
    environment:
      - BACKEND_API_URL=http://host.docker.internal:8002/api/v1
```

## Microservice Architecture Principles

### ✅ Currently Maintained
- **Independent Deployment** - Separate containers and processes
- **Technology Independence** - Flask (Python) vs Next.js (Node.js)
- **Service Boundaries** - Clear API/UI separation
- **Fault Isolation** - Services can fail independently

### ⚠️ Areas for Improvement
- **Shared Configuration** - Port management across projects
- **Development Workflow** - Multiple repositories to manage
- **Code Sharing** - Types, utilities, constants duplicated

## Current Challenges

1. **Configuration Sync** - Port changes must be updated in both projects
2. **Development Setup** - Multiple commands to start full stack
3. **Dependency Management** - Separate package management
4. **Type Safety** - No shared TypeScript definitions

## Future Considerations

See `MONOREPO_MIGRATION.md` for consolidation planning.