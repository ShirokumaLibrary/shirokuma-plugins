# shirokuma-docs CLI Invocation

## Direct Call (No npx)

`shirokuma-docs` is installed globally. Always call it directly:

```bash
# Correct
shirokuma-docs session start
shirokuma-docs issues list
shirokuma-docs lint tests -p .

# Wrong - unnecessary overhead
npx shirokuma-docs session start
```

## Verbose Option

Default output is minimal (errors, warnings, success messages only). Progress logs and detailed info are suppressed.

- **Do not** use `--verbose` in AI workflows — it increases context window consumption
- `--verbose` is for human debugging only
