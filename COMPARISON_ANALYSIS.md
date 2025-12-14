# Cross-Repository Comparison Analysis

Detailed comparison of update checker implementations across three HenriquesLab packages.

## Key Findings

### 1. Async/Threading Patterns

**folder2md4llms** (Most Sophisticated):
- `_run_async_in_thread()` with thread.join(timeout=30)
- Detects running event loop before choosing async strategy
- Exception propagation via nonlocal variables
- Both async (daemon, no join) and sync (with join) methods

**taskrepo/rxiv-maker** (Simpler):
- Daemon thread, no joining
- Silent failures
- No event loop detection

**✅ Best Practice**: Use folder2md4llms pattern for sync operations, simple daemon for async

### 2. Version Source Priority

**taskrepo/rxiv-maker** (Smart):
- Check Homebrew FIRST if installed via Homebrew
- Only fall back to PyPI if Homebrew fails

**folder2md4llms** (PyPI only):
- Always checks PyPI

**✅ Best Practice**: Implement Homebrew-first strategy

### 3. Version Comparison

**All three**:
- Use `packaging.version.parse()` when available
- Fall back to string comparison
- rxiv-maker handles `InvalidVersion` exception

**✅ Best Practice**: Use packaging with proper exception handling

### 4. Timeouts

- **folder2md4llms**: 10 seconds (PyPI)
- **taskrepo**: 2 seconds (PyPI)
- **rxiv-maker**: 5 seconds (PyPI)

**✅ Best Practice**: 5 seconds is reasonable balance

### 5. Changelog Integration

**rxiv-maker** (Unique Feature):
- Caches changelog summaries with key `changelog_{current}_{latest}`
- Avoids repeated fetches for same version pairs
- Graceful degradation if fetch fails

**✅ Best Practice**: Cache changelog per version pair

### 6. Singleton Pattern

**All three**: Use global instance with convenience functions

```python
_update_checker = None

def get_update_checker() -> UpdateChecker:
    global _update_checker
    if _update_checker is None:
        _update_checker = UpdateChecker()
    return _update_checker
```

**✅ Best Practice**: Provide both class-based and function-based APIs

### 7. Notification Formatting

**folder2md4llms**: Simple text with dashes
**taskrepo**: Smart command suggestions ("tsk upgrade" vs manual)
**rxiv-maker**: Rich Panel with colors, padding, gradients

**✅ Best Practice**: Use Rich Panel when available, with graceful fallback

### 8. Cache Management

**All similar**, but:
- **folder2md4llms**: `~/.cache/folder2md4llms/update_check.json`
- **taskrepo**: `~/.TaskRepo/update_check_cache.json` (with migration)
- **rxiv-maker**: Uses manuscript cache dir (project-specific)

**✅ Best Practice**: Use `~/.cache/{package}/updates/update_check.json` (XDG standard)

### 9. Error Handling

**All**: Silent failures to avoid disrupting application

**rxiv-maker** adds:
- Exception handling in notification display
- Fallback to safe_print for encoding issues

**✅ Best Practice**: Multiple fallback layers

### 10. Configuration Integration

**rxiv-maker** (Unique):
- Checks config file: `config.get("general.check_updates", True)`
- Allows per-project configuration

**✅ Best Practice**: Support optional config integration

## Implementation Improvements Needed

1. ✅ **Add Homebrew-first strategy** in UpdateChecker
2. ✅ **Add singleton pattern** with global convenience functions
3. ✅ **Improve async handling** with event loop detection
4. ✅ **Add changelog caching** per version pair
5. ✅ **Add sync check with timeout** for blocking operations
6. ✅ **Reduce PyPI timeout** to 5 seconds
7. ✅ **Add config support** (optional)
8. ✅ **Improve Rich Panel** with padding and styling
9. ✅ **Add safe_print fallback** for encoding issues
10. ✅ **Better exception handling** in version comparison

## Architecture Decision

**Source Priority**:
```
1. Detect installation method
2. If Homebrew → try HomebrewSource first
3. If Homebrew fails or not Homebrew → try PyPISource
4. Return first successful result
```

This matches taskrepo/rxiv-maker behavior and is smarter than always checking PyPI.
