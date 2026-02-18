# Docker Container Memory Configuration

## Overview

The Agent Zero container now has memory and CPU limits configured in `docker-compose.yml`. This helps prevent the container from consuming excessive system resources.

## Current Configuration

### Memory Limits
- **Maximum Memory**: 8GB (`memory: 8G`)
- **Reserved Memory**: 2GB (`reservations.memory: 2G`)

### CPU Limits
- **Maximum CPU**: 4 cores (`cpus: '4.0'`)
- **Reserved CPU**: 1 core (`reservations.cpus: '1.0'`)

## Adjusting Memory Limits

### Method 1: Edit docker-compose.yml Directly

Edit the `deploy.resources.limits.memory` value in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 16G      # Change this value (e.g., 4G, 8G, 16G, 32G)
      cpus: '4.0'
    reservations:
      memory: 2G
      cpus: '1.0'
```

### Method 2: Use Environment Variable (Recommended)

Add to your `.env` file:

```bash
CONTAINER_MEMORY_LIMIT=16G
CONTAINER_CPU_LIMIT=4.0
```

Then update `docker-compose.yml` to use the variable:

```yaml
deploy:
  resources:
    limits:
      memory: ${CONTAINER_MEMORY_LIMIT:-8G}
      cpus: '${CONTAINER_CPU_LIMIT:-4.0}'
```

## Common Memory Values

| Use Case | Recommended Memory | CPU Cores |
|----------|-------------------|-----------|
| Light usage (testing) | 2-4GB | 1-2 cores |
| Standard usage | 4-8GB | 2-4 cores |
| Heavy usage (LLM inference) | 8-16GB | 4-8 cores |
| Maximum performance | 16-32GB+ | 8+ cores |

## Applying Changes

After modifying `docker-compose.yml`:

```bash
# Recreate the container with new limits
docker compose down
docker compose up -d

# Or restart the specific service
docker compose up -d --force-recreate agent-zero
```

## Verifying Memory Limits

### Check Current Limits

```bash
# View container resource limits
docker inspect agent-zero | grep -A 10 "Memory\|Cpu"

# Or use docker stats
docker stats agent-zero --no-stream
```

### Monitor Memory Usage

```bash
# Real-time memory usage
docker stats agent-zero

# Check memory usage over time
docker stats agent-zero --format "table {{.Container}}\t{{.MemUsage}}\t{{.MemPerc}}"
```

## Troubleshooting

### Container Running Out of Memory

If you see errors like:
- `OOMKilled` (Out of Memory)
- Container crashes during heavy operations
- Slow performance

**Solution**: Increase the memory limit:

```yaml
limits:
  memory: 16G  # Increase from 8G to 16G
```

### Memory Limit Not Applied

**Issue**: Changes to `docker-compose.yml` not taking effect.

**Solution**: 
1. Ensure you're using Docker Compose v2+ (`docker compose` not `docker-compose`)
2. Recreate the container: `docker compose up -d --force-recreate agent-zero`
3. Check Docker Desktop settings allow sufficient memory allocation

### Docker Desktop Memory Settings

On macOS/Windows with Docker Desktop:

1. Open Docker Desktop
2. Go to Settings → Resources → Advanced
3. Ensure "Memory" slider is set higher than your container limit
4. Click "Apply & Restart"

**Example**: If container limit is 16GB, Docker Desktop should have at least 20GB+ allocated.

## Notes

- **Reservations** are guaranteed resources the container will always have
- **Limits** are the maximum resources the container can use
- Memory limits prevent containers from consuming all system RAM
- CPU limits prevent containers from monopolizing CPU resources
- These limits apply per container, not system-wide

## Best Practices

1. **Start Conservative**: Begin with lower limits and increase as needed
2. **Monitor Usage**: Use `docker stats` to see actual usage
3. **Leave Headroom**: Don't set limits to 100% of available system resources
4. **Consider Host Resources**: Ensure your host system has enough RAM/CPU for the container + OS

## Example: High-Performance Configuration

For systems with 32GB+ RAM and 8+ CPU cores:

```yaml
deploy:
  resources:
    limits:
      memory: 24G
      cpus: '8.0'
    reservations:
      memory: 4G
      cpus: '2.0'
```

## Related Documentation

- [Docker Compose Resource Limits](https://docs.docker.com/compose/compose-file/deploy/#resources)
- [Docker Memory Management](https://docs.docker.com/config/containers/resource_constraints/#memory)
