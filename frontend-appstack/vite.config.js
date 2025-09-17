import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import svgrPlugin from "vite-plugin-svgr";
import { ViteEjsPlugin } from "vite-plugin-ejs";
// import { nodePolyfills } from "vite-plugin-node-polyfills";
// import { ssr } from 'vite-plugin-ssr/plugin'

import { resolve } from "path";

const now = new Date();
const timestamp = now.getTime();
const version = timestamp;
// const version = makeid(8);

export default ({ mode }) => {
  process.env = Object.assign(process.env, loadEnv(mode, process.cwd(), ""));

  const generateScopedName = (mode === "production" ? "[hash:base64:2]" : "[local]___[hash:base64:2]");
  
  // console.log(process.env);
  // console.log(process.env.VITE_BASE_URL)
  // console.log(process.env.VITE_BASE)

  return defineConfig({
    define: {
      "import.meta.env.VITE_VERSION_JS": version.toString(),
    },
    resolve: {
      alias: {
        "@": resolve(__dirname, "src"),
      },
    },
    plugins: [
      react({
        // babel: {
        //   presets: [],
        //   // Your plugins run before any built-in transform (eg: Fast Refresh)
        //   plugins: [],
        //   // Use .babelrc files
        //   babelrc: false,
        //   // Use babel.config.js files
        //   configFile: true,
        // },
      }),
      svgrPlugin(),
      ViteEjsPlugin(),
      // nodePolyfills({
      //   protocolImports: true,
      // }),
      // splitVendorChunkPlugin(),
      // ssr({
      //   baseAssets: 'https://sateraito-aiboard-dev.appspot.com//static/frontend/',
      //   baseServer: '/v2/sateraitooffice.personal/'
      // })
    ],
    css: {
      // https://vitejs.dev/config/shared-options.html#css-modules
      modules: {
        generateScopedName,
        localsConvention: "camelCase",
      },
      postcss: {},
    },
    build: {
      // outDir: "../src/static/frontend",
      cssCodeSplit: true,
      chunkSizeWarningLimit: 3000,
      rollupOptions: {
        // globals: {
        //    jquery: 'window.jQuery',
        //    jquery: 'window.$'
        // },
        input: {
          main: resolve(__dirname, "index.html"),
          light: resolve(__dirname, "src/assets/scss/light.scss"),
          dark: resolve(__dirname, "src/assets/scss/dark.scss"),
          // mobile_light: resolve(__dirname, "src/assets/scss/mobile_light.scss"),
          // mobile_dark: resolve(__dirname, "src/assets/scss/mobile_dark.scss"),
        },
        output: {
          // assetFileNames: "assets/[name][extname]",
          assetFileNames: (asset) => {
            // if (parse(asset.name).name === "externalImage") {
            //   return "images/src/[name][extname]";
            // }
            // console.log(asset.name);
            if (
              [".jpg", ".png", ".svg", ".avif", ".webp"].some((ext) =>
                asset.name?.endsWith(ext)
              )
            ) {
              return "assets/img/[name]-[hash][extname]";
            }
            if (asset.name == "dark.css" || asset.name == "light.css" || asset.name == "mobile_dark.css" || asset.name == "mobile_light.css") {
              return "assets/[name]." + version.toString() + "[extname]";
            }
            return "assets/[name].[hash][extname]";
          },
          // manualChunks: {
          //   markdown: [
          //     "react-markdown",
          //     "remark-gfm",
          //     "rehype-raw",
          //     "remark-math",
          //     "rehype-katex",
          //   ],
          //   syntaxhighlighter: ["react-syntax-highlighter"],
          //   apexcharts: ["apexcharts"],
          //   chartjs: ["chart.js", "react-chartjs-2"],
          //   // googlemaps: ["google-map-react"],
          //   // vectormaps: [
          //   //   "jsvectormap",
          //   //   "src/vendor/us_aea_en.js",
          //   //   "src/vendor/world.js",
          //   // ],
          //   // fullcalendar: [
          //   //   "@fullcalendar/bootstrap",
          //   //   "@fullcalendar/daygrid",
          //   //   "@fullcalendar/react",
          //   //   "@fullcalendar/timegrid",
          //   // ],
          // },
        },
      },
    },
    base: process.env.VITE_BASE,
    // publicDir: process.env.VITE_PUBLIC_DIR
  });
};
