# Command Transformation Checklist

## La Factoria Command Standards

### ✅ KEEP - Commands that align with La Factoria principles:
- **Simple, focused purpose** (not "ultimate mega platform builder")
- **Educational content focus** (content generation, quality assessment)
- **TDD methodology** (test-first development patterns)
- **Railway deployment** (simple cloud platform)
- **PostgreSQL focus** (single database solution)
- **Quality over complexity** (no 100+ agent spawning)

### 🔄 TRANSFORM - Commands that can be adapted:
- **Generic patterns → La Factoria specific** (e.g., /auto → La Factoria content router)
- **Enterprise complexity → Simple TDD** (remove agent swarms, focus on atomic tasks)
- **Multi-cloud → Railway focused** (single platform deployment)
- **Complex orchestration → Step-by-step construction** (following implementation roadmap)

### ❌ DELETE - Commands that contradict La Factoria principles:
- **Mass agent spawning** ("50+ agents", "100+ agents", "unlimited agents")
- **Enterprise complexity** ("ultimate platform builder", "extreme scale")
- **Generic mega-platforms** (not educational content focused)
- **Over-engineering** (complex DAG orchestration for simple tasks)

## Transformation Process

### For Each Command File:
1. **Read header and description** - Check against standards above
2. **Assess content relevance** - Does it help build La Factoria?
3. **Decision pathway**:
   - KEEP: Verify it's already La Factoria focused
   - TRANSFORM: Remove generic bloat, add La Factoria context, focus on implementation roadmap tasks
   - DELETE: Remove completely if it contradicts simple approach

### Quality Gates for Transformed Commands:
- **Purpose clarity**: One specific La Factoria task (TASK-001 through TASK-007)
- **TDD integration**: References test-first development
- **Simplicity**: <200 lines, no enterprise complexity
- **Educational focus**: Helps build educational content platform
- **Railway integration**: Uses Railway as deployment target

## Commands to Delete (Identified)
- `/mega-platform-builder` - "100+ agents for enterprise platforms"
- `/mass-transformation` - "50+ agents for framework conversion"  
- `/swarm` - Generic multi-agent orchestration
- Any other "ultimate", "mega", "mass", "unlimited agent" commands

## Commands to Transform (Examples)
- `/auto` → `/la-factoria-router` (route to appropriate La Factoria task)
- `/db-admin` → `/la-factoria-postgres` (PostgreSQL setup for educational content)
- `/project-task` → Integration with TASK-001 through TASK-007

## Commands to Keep (If Any)
- Commands already focused on educational content generation
- Commands already following TDD methodology
- Commands already Railway/PostgreSQL focused