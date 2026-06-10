export interface ParsedStateVar {
  name: string;
  type: string;
}

export interface ParsedFunction {
  name: string;
  decorator: "@gl.public.view" | "@gl.public.write" | "constructor";
  params: string[];
  docstring: string;
  returnsType: string;
}

export interface ParsedContract {
  name: string;
  stateVars: ParsedStateVar[];
  functions: ParsedFunction[];
  hasExecPrompt: boolean;
  writeCount: number;
  viewCount: number;
  errors: string[];
}

export function parseContract(code: string): ParsedContract {
  const errors: string[] = [];
  const lines = code.split("\n");

  // Contract name
  const nameMatch = code.match(/class\s+(\w+)\s*\(gl\.Contract\)/);
  const name = nameMatch ? nameMatch[1] : "";
  if (!name) errors.push("No class inheriting gl.Contract found");

  // State variables (typed class attributes before __init__)
  const stateVars: ParsedStateVar[] = [];
  const statePattern = /^\s{4}(\w+):\s*([^\s=][^\n]*?)(?:\s*$)/gm;
  let m: RegExpExecArray | null;
  while ((m = statePattern.exec(code)) !== null) {
    const vname = m[1];
    const vtype = m[2].trim();
    if (vname !== "def" && !vname.startsWith("@") && vname !== "return") {
      stateVars.push({ name: vname, type: vtype });
    }
  }

  // Functions
  const functions: ParsedFunction[] = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Constructor
    if (/^\s+def __init__/.test(line)) {
      const paramMatch = line.match(/def __init__\(self(?:,\s*([^)]*))?\)/);
      const params = paramMatch?.[1]
        ? paramMatch[1].split(",").map((p) => p.trim()).filter(Boolean)
        : [];
      let docstring = "";
      if (lines[i + 1]?.trim().startsWith('"""')) {
        docstring = lines[i + 1].trim().replace(/"""/g, "").trim();
      }
      functions.push({
        name: "__init__",
        decorator: "constructor",
        params,
        docstring,
        returnsType: "None",
      });
      continue;
    }

    // Public functions
    const decorLine = line.trim();
    if (decorLine === "@gl.public.view" || decorLine === "@gl.public.write") {
      const decorator = decorLine as "@gl.public.view" | "@gl.public.write";
      const defLine = lines[i + 1] ?? "";
      const defMatch = defLine.match(/def\s+(\w+)\(self(?:,\s*([^)]*))?\)(?:\s*->\s*([^:]+))?/);
      if (defMatch) {
        const fname = defMatch[1];
        const rawParams = defMatch[2] ?? "";
        const params = rawParams
          .split(",")
          .map((p) => p.trim())
          .filter(Boolean);
        const returnsType = defMatch[3]?.trim() ?? "None";
        let docstring = "";
        const docLine = lines[i + 2]?.trim() ?? "";
        if (docLine.startsWith('"""')) {
          docstring = docLine.replace(/"""/g, "").trim();
        }
        functions.push({ name: fname, decorator, params, docstring, returnsType });
      }
    }
  }

  const hasExecPrompt = code.includes("gl.exec_prompt(");
  const writeCount = functions.filter((f) => f.decorator === "@gl.public.write").length;
  const viewCount = functions.filter((f) => f.decorator === "@gl.public.view").length;

  if (!hasExecPrompt && writeCount > 0) {
    errors.push("Write function found but no gl.exec_prompt() call — validators have nothing to reason about");
  }

  return { name, stateVars, functions, hasExecPrompt, writeCount, viewCount, errors };
}
