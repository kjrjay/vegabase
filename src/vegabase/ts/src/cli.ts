import { watch } from "fs";
import path from "node:path";
import fs from "node:fs";
import { Glob } from "bun";
import { logRequest } from "./log";

// User's project directory (cwd)
const projectDir = process.cwd();
const vegabaseDir = path.join(projectDir, ".vegabase");

/**
 * Load a template file and replace placeholders with actual values
 */
function loadTemplate(name: string, replacements: Record<string, string> = {}): string {
  const templatePath = path.join((import.meta as any).dir, '../templates', name);
  let content = fs.readFileSync(templatePath, 'utf-8');

  for (const [key, value] of Object.entries(replacements)) {
    content = content.replace(new RegExp(key, 'g'), value);
  }

  return content;
}

// Types for route manifest
interface RouteConfig {
  path: string;
  component: string;
  cacheTime: number;
  preload: "intent" | "viewport" | "render";
}

interface RouteManifest {
  version: number;
  routes: RouteConfig[];
}



/**
 * Load route manifest from .vegabase/routes.json
 */
function loadRouteManifest(): RouteManifest {
  const manifestPath = path.join(vegabaseDir, "routes.json");
  if (!fs.existsSync(manifestPath)) {
    console.error("❌ Error: .vegabase/routes.json not found");
    console.error("   Run 'python routes.py' to generate the route manifest.");
    process.exit(1);
  }
  const content = fs.readFileSync(manifestPath, "utf-8");
  return JSON.parse(content) as RouteManifest;
}

/**
 * Generate route variable name from component path
 */
function toRouteVarName(component: string): string {
  // "Tasks/Index" -> "tasksIndexRoute"
  return (
    component
      .replace(/\//g, "_")
      .replace(/([A-Z])/g, (_, c, i) => (i === 0 ? c.toLowerCase() : c))
      .replace(/_([a-z])/g, (_, c) => c.toUpperCase()) + "Route"
  );
}

/**
 * Generate TanStack Router route tree from manifest
 */
function generateRouteTree(manifest: RouteManifest): string {
  const routes = manifest.routes;

  // Generate direct component imports (not lazy for SSR compatibility)
  const componentImports = routes
    .map((route) => {
      const varName = route.component.replace(/\//g, "_");
      return `import ${varName} from '../frontend/pages/${route.component}';`;
    })
    .join("\n");

  // Generate route factory functions (they need a parent route reference)
  const routeFactories = routes
    .map((route) => {
      const varName = toRouteVarName(route.component);
      const factoryName = `create${varName.charAt(0).toUpperCase() + varName.slice(1)}`;
      const componentVar = route.component.replace(/\//g, "_");
      const staleTime = route.cacheTime > 0 ? route.cacheTime * 1000 : 0;

      // Handle path parameters for fetch URL
      const fetchPath = route.path.includes("$")
        ? `\`${route.path.replace(/\$(\w+)/g, "${params.$1}")}\``
        : `'${route.path}'`;

      return loadTemplate('route.template.tsx', {
        '__FACTORY_NAME__': factoryName,
        '__ROUTE_PATH__': route.path,
        '__COMPONENT_VAR__': componentVar,
        '__FETCH_PATH__': fetchPath,
        '__STALE_TIME__': staleTime > 0 ? `staleTime: ${staleTime},` : "",
      }).trim();
    })
    .join("\n\n");

  // Generate route factory names for building trees
  const routeFactoryNames = routes.map((r) => {
    const varName = toRouteVarName(r.component);
    return `create${varName.charAt(0).toUpperCase() + varName.slice(1)}`;
  });
  const routeFactoryCalls = (parentVar: string) =>
    routeFactoryNames.map((fn) => `  ${fn}(${parentVar})`).join(",\n");

  const defaultPreload = routes[0]?.preload || "intent";

  // Load template and replace placeholders
  return loadTemplate('routeTree.template.tsx', {
    '__COMPONENT_IMPORTS__': componentImports,
    '__ROUTE_FACTORIES__': routeFactories,
    '__SSR_ROUTE_TREE__': routeFactoryCalls("ssrRootRoute"),
    '__CLIENT_ROUTE_TREE__': routeFactoryCalls("clientRootRoute"),
    '__DEFAULT_PRELOAD__': defaultPreload,
  });
}

function generateTanStackClientEntry(): string {
  return loadTemplate('client.template.tsx', {
    '__WS_PORT__': String(process.env.PORT || 3001),
  });
}

/**
 * Generate TanStack Router SSR entry
 */
function generateTanStackSSREntry(): string {
  return loadTemplate('ssr.template.tsx');
}

/**
 * Generate TanStack Router SSR server entry
 */
function generateTanStackSSRServerEntry(): string {
  // Get the path to log.ts relative to where this cli is running
  const logPath = path.join((import.meta as any).dir, 'log');
  return loadTemplate('ssr-server.template.tsx', {
    '__DEFAULT_PORT__': '13714',
    '__LOG_PATH__': logPath,
  });
}



/**
 * Generate all entry files in the user's project
 */
async function generateEntryFiles() {
  // Ensure .vegabase directory exists
  if (!fs.existsSync(vegabaseDir)) {
    fs.mkdirSync(vegabaseDir, { recursive: true });
  }

  const manifest = loadRouteManifest();

  console.log("📦 Using TanStack Router");

  const routeTreeCode = generateRouteTree(manifest);
  const clientEntry = generateTanStackClientEntry();
  const ssrEntry = generateTanStackSSREntry();
  const ssrServerEntry = generateTanStackSSRServerEntry();

  fs.writeFileSync(path.join(vegabaseDir, "routeTree.gen.tsx"), routeTreeCode);
  fs.writeFileSync(path.join(vegabaseDir, "client.tsx"), clientEntry);
  fs.writeFileSync(path.join(vegabaseDir, "ssr.tsx"), ssrEntry);
  fs.writeFileSync(path.join(vegabaseDir, "ssr-server.tsx"), ssrServerEntry);

  console.log("📝 Generated TanStack Router files in .vegabase/");
}

// Entry points for TanStack Router
function getEntryPoints() {
  return {
    client: path.join(vegabaseDir, "client.tsx"),
    ssr: path.join(vegabaseDir, "ssr.tsx"),
    ssrServer: path.join(vegabaseDir, "ssr-server.tsx"),
    external: ["react", "react-dom", "@tanstack/react-router"],
  };
}

// ==================== DEV COMMAND ====================
async function dev() {
  await generateEntryFiles();

  const entries = getEntryPoints();

  // Import tailwind plugin from user's project
  const { default: tailwindcss } = await import(
    path.join(projectDir, "node_modules", "bun-plugin-tailwind")
  );

  async function build() {
    // Regenerate files on each build
    await generateEntryFiles();

    console.log("⚡ Building...");

    // Build CSS separately (prevents runtime CSS injection in client.js)
    await Bun.build({
      entrypoints: [`${projectDir}/frontend/styles.css`],
      outdir: "./static/dist",
      naming: "client.[ext]",
      plugins: [tailwindcss],
    });

    // Bundle Client (no CSS import - uses <link> tag)
    await Bun.build({
      entrypoints: [entries.client],
      outdir: "./static/dist",
      naming: "client.[ext]",
      target: "browser",
      splitting: true,
    });

    // Bundle SSR (Library for Dev Server)
    await Bun.build({
      entrypoints: [entries.ssr],
      outdir: "./.vegabase",
      naming: { entry: "ssr_dev.js" },
      target: "bun",
      external: entries.external,
    });

    console.log("✅ Build complete.");
  }

  await build();

  const server = Bun.serve({
    port: process.env.PORT || 3001,
    async fetch(req, server) {
      const url = new URL(req.url);

      // SSR Render Endpoint
      if (req.method === "POST" && url.pathname === "/render") {
        const startTime = Date.now();
        try {
          const buildPath = `${vegabaseDir}/ssr_dev.js`;
          const { default: render } = await import(buildPath + `?t=${Date.now()}`);
          const page = await req.json();
          const result = await render(page);
          const duration = Date.now() - startTime;
          logRequest(req.method, page.url, page.component, 200, duration);
          return Response.json(result);
        } catch (error: any) {
          const duration = Date.now() - startTime;
          logRequest(req.method, "/render", null, 500, duration);
          console.error("SSR Error:", error);
          return new Response(JSON.stringify({ error: error.message }), { status: 500 });
        }
      }

      const corsHeaders = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      };

      if (req.method === "OPTIONS") {
        return new Response(null, { headers: corsHeaders });
      }

      if (url.pathname === "/ws") {
        if (server.upgrade(req)) return;
        return new Response("Upgrade failed", { status: 500 });
      }

      if (url.pathname.endsWith(".js")) {
        const filePath = `./static/dist${url.pathname}`;
        const file = Bun.file(filePath);
        if (await file.exists()) {
          return new Response(file, {
            headers: { ...corsHeaders, "Content-Type": "application/javascript" },
          });
        }
      }

      if (url.pathname === "/client.css") {
        return new Response(Bun.file("./static/dist/client.css"), {
          headers: { ...corsHeaders, "Content-Type": "text/css" },
        });
      }

      return new Response("Not Found", { status: 404, headers: corsHeaders });
    },
    websocket: {
      message() { },
      open(_ws) {
        console.log("Browser connected to Hot Reload");
      },
    },
  });

  console.log(`👀 Watcher & Asset Server running on http://localhost:${server.port}`);

  const _watcher = watch("./frontend", { recursive: true }, async (event, filename) => {
    if (filename) {
      await build();
      server.publish("reload", "reload");
    }
  });
}

// ==================== BUILD COMMAND ====================
async function build() {
  await generateEntryFiles();

  const entries = getEntryPoints();

  // Import tailwind plugin from user's project
  const { default: tailwindcss } = await import(
    path.join(projectDir, "node_modules", "bun-plugin-tailwind")
  );

  // Build CSS separately (prevents runtime CSS injection in client.js)
  await Bun.build({
    entrypoints: [`${projectDir}/frontend/styles.css`],
    outdir: "./static/dist",
    naming: "client.[ext]",
    plugins: [tailwindcss],
  });
  console.log("✅ CSS Built");

  // Bundle the Client (no CSS import - uses <link> tag)
  await Bun.build({
    entrypoints: [entries.client],
    outdir: "./static/dist",
    naming: "client.[ext]",
    target: "browser",
    splitting: true,
    minify: true,
    define: {
      'process.env.NODE_ENV': '"production"',
    },
  });
  console.log("✅ Client Bundle Built");

  // Bundle the Server (for SSR)
  await Bun.build({
    entrypoints: [entries.ssrServer],
    outdir: "./.vegabase",
    naming: { entry: "ssr.js" },
    target: "bun",
    external: entries.external,
    plugins: [tailwindcss],
  });
  console.log("✅ SSR Bundles Built");
}

// ==================== START COMMAND ====================
async function start() {
  const ssrPath = path.join(vegabaseDir, "ssr.js");

  if (!fs.existsSync(ssrPath)) {
    console.error("❌ Error: SSR server bundle not found at .vegabase/ssr.js");
    console.error("   Run 'vegabase build' first to create the production bundle.");
    process.exit(1);
  }

  const port = Number(process.env.PORT) || 13714;

  console.log(`🚀 Starting production server on port ${port}...`);
  console.log(`   Bundle: ${ssrPath}`);
  console.log(`   Press Ctrl+C to stop`);
  console.log("");

  try {
    await import(ssrPath);
  } catch (error: any) {
    console.error("❌ Error starting production server:");
    console.error(error.message);
    process.exit(1);
  }
}

// ==================== CLI ROUTER ====================
const command = process.argv[2];

switch (command) {
  case "dev":
    await dev();
    break;
  case "build":
    await build();
    break;
  case "start":
    await start();
    break;
  default:
    console.error("Unknown command. Available commands: dev, build, start");
    process.exit(1);
}
