# Monorepo Migration Plan

## Goal
Consolidate `random-toolbox` (API) and `random-toolbox-ui` (UI) into a single monorepo while maintaining microservice architecture principles.

## Proposed Structure

```
random-toolbox-monorepo/
├── apps/
│   ├── api/                    # Flask API microservice
│   │   ├── src/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── README.md
│   └── ui/                     # Next.js UI application
│       ├── src/
│       ├── public/
│       ├── package.json
│       ├── Dockerfile
│       └── README.md
├── packages/                   # Shared code
│   ├── types/                  # TypeScript definitions
│   │   ├── api.ts             # API response types
│   │   └── common.ts          # Common types
│   ├── utils/                  # Shared utilities
│   │   ├── constants.ts       # Shared constants
│   │   └── helpers.ts         # Common functions
│   └── config/                # Shared configurations
│       ├── ports.ts           # Port configuration
│       └── environments.ts    # Environment settings
├── tools/                      # Development tools
│   ├── scripts/
│   │   ├── dev-stack.sh       # Start full development stack
│   │   ├── build-all.sh       # Build all applications
│   │   └── test-all.sh        # Run all tests
│   ├── docker/
│   │   ├── docker-compose.dev.yml
│   │   ├── docker-compose.int.yml
│   │   └── docker-compose.prod.yml
│   └── configs/               # Shared tooling configs
│       ├── eslint.config.js
│       ├── prettier.config.js
│       └── tsconfig.base.json
├── docs/                       # Documentation
│   ├── api/                   # API documentation
│   ├── ui/                    # UI documentation
│   └── deployment/            # Deployment guides
├── package.json               # Root workspace configuration
├── nx.json                    # Nx workspace configuration (optional)
└── README.md                  # Monorepo documentation
```

## Migration Benefits

### ✅ Maintains Microservice Principles
- **Independent Deployment** - Each app can still be deployed separately
- **Technology Independence** - Flask and Next.js remain separate
- **Service Boundaries** - Clear app separation under `apps/`
- **Fault Isolation** - Apps can fail independently

### ✅ Improves Development Experience
- **Unified Tooling** - Single linting, testing, CI/CD pipeline
- **Shared Code** - Types, utilities, constants in `packages/`
- **Atomic Changes** - Frontend/backend changes in single commit
- **Simplified Scripts** - One command to start full stack

### ✅ Better Configuration Management
- **Centralized Ports** - Single source of truth for port configuration
- **Environment Consistency** - Shared environment management
- **Docker Orchestration** - Unified docker-compose files

## Migration Strategy

### Phase 1: Preparation
1. **Create new monorepo structure**
2. **Set up workspace tooling** (Nx/Turborepo or vanilla workspace)
3. **Create shared packages** (types, utils, config)

### Phase 2: Code Migration
1. **Move API code** to `apps/api/`
2. **Move UI code** to `apps/ui/`
3. **Extract shared code** to `packages/`
4. **Update imports and references**

### Phase 3: Tooling Migration
1. **Migrate development scripts** to `tools/scripts/`
2. **Consolidate Docker configurations**
3. **Set up unified CI/CD pipeline**
4. **Update documentation**

### Phase 4: Testing & Validation
1. **Test all environments** (DEV, INT, PROD)
2. **Validate microservice independence**
3. **Performance testing**
4. **Documentation review**

## Recommended Tools

### Option 1: Nx (Recommended)
- **Enterprise-grade** monorepo tooling
- **Built-in caching** and dependency graph
- **Plugin ecosystem** for Flask, Next.js
- **Excellent TypeScript support**

### Option 2: Turborepo
- **Lightweight** and fast
- **Great for JavaScript/TypeScript** projects
- **Simple configuration**
- **Good caching system**

### Option 3: Vanilla Workspace
- **Minimal setup** using npm/yarn workspaces
- **Full control** over tooling
- **No additional dependencies**
- **Custom scripts for orchestration**

## Port Configuration (Post-Migration)

```typescript
// packages/config/ports.ts
export const PORTS = {
  DEV: {
    API: 8001,
    UI: 3001
  },
  INT: {
    API: 8002,
    UI: 3002
  },
  PROD: {
    API: 8000,
    UI: 3000
  }
} as const;
```

## Docker Orchestration Example

```yaml
# tools/docker/docker-compose.dev.yml
version: '3.8'
services:
  api:
    build:
      context: ../../
      dockerfile: apps/api/Dockerfile
    ports:
      - "8001:8001"
    environment:
      - PORT=8001
      - NODE_ENV=development
    
  ui:
    build:
      context: ../../
      dockerfile: apps/ui/Dockerfile
    ports:
      - "3001:3000"
    environment:
      - NEXT_PUBLIC_API_BASE_URL=http://localhost:8001/api/v1
    depends_on:
      - api
```

## Implementation Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| Phase 1 | 1-2 days | Structure setup, tooling selection |
| Phase 2 | 2-3 days | Code migration, shared packages |
| Phase 3 | 1-2 days | Script migration, Docker setup |
| Phase 4 | 1-2 days | Testing, documentation |

**Total Estimated Time: 5-9 days**

## Risk Mitigation

- **Backup current repositories** before migration
- **Maintain separate branches** during transition
- **Gradual migration** with frequent testing
- **Rollback plan** if issues arise

## Success Criteria

- [ ] Both applications build and run successfully
- [ ] All existing functionality preserved
- [ ] Development workflow improved
- [ ] Port configuration centralized
- [ ] Shared code properly extracted
- [ ] Docker orchestration working
- [ ] CI/CD pipeline functional
- [ ] Documentation updated

## Next Steps

1. **Decision on tooling** (Nx vs Turborepo vs Vanilla)
2. **Create migration branch**
3. **Set up monorepo structure**
4. **Begin Phase 1 implementation**

---

*Created: September 2024*
*Status: Planning Phase*