"""Fix literal newlines inside double-quoted strings in lib/learn/content.ts."""
import pathlib

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")
f = ROOT / "lib/learn/content.ts"

text = f.read_bytes().decode("utf-8")

def fix_multiline_dq(s: str) -> str:
    result = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == '"':
            # Start of a double-quoted string — collect until closing "
            j = i + 1
            out = ['"']
            while j < n:
                c = s[j]
                if c == '\\':
                    # Escaped char — keep as-is
                    out.append(c)
                    j += 1
                    if j < n:
                        out.append(s[j])
                        j += 1
                elif c == '"':
                    out.append('"')
                    j += 1
                    break
                elif c == '\n':
                    # Literal newline inside double-quoted string — escape it
                    out.append('\\n')
                    j += 1
                elif c == '\r':
                    # Skip CR
                    j += 1
                else:
                    out.append(c)
                    j += 1
            result.append(''.join(out))
            i = j
        elif ch == '`':
            # Template literal — skip over, preserving as-is
            j = i + 1
            out = ['`']
            while j < n:
                c = s[j]
                if c == '\\':
                    out.append(c)
                    j += 1
                    if j < n:
                        out.append(s[j])
                        j += 1
                elif c == '`':
                    out.append('`')
                    j += 1
                    break
                else:
                    out.append(c)
                    j += 1
            result.append(''.join(out))
            i = j
        elif ch == "'":
            # Single-quoted string — also fix literal newlines
            j = i + 1
            out = ["'"]
            while j < n:
                c = s[j]
                if c == '\\':
                    out.append(c)
                    j += 1
                    if j < n:
                        out.append(s[j])
                        j += 1
                elif c == "'":
                    out.append("'")
                    j += 1
                    break
                elif c == '\n':
                    out.append('\\n')
                    j += 1
                elif c == '\r':
                    j += 1
                else:
                    out.append(c)
                    j += 1
            result.append(''.join(out))
            i = j
        elif ch == '/' and i + 1 < n and s[i + 1] == '/':
            # Line comment — copy to end of line
            j = i
            while j < n and s[j] != '\n':
                j += 1
            result.append(s[i:j])
            i = j
        else:
            result.append(ch)
            i += 1
    return ''.join(result)


fixed = fix_multiline_dq(text)
f.write_bytes(fixed.encode("utf-8"))

lines = fixed.split('\n')
print(f"Fixed content.ts — {len(lines)} lines written.")
