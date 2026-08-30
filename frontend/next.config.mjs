/** @type {import('next').NextConfig} */
const nextConfig = {
  // Keep framework configuration centralised so security headers and API
  // rewrites can be introduced clearly during the security phase.
  reactStrictMode: true,

  // standalone output bundles only the files Next.js needs to serve the app,
  // which is what the production Dockerfile copies into the final image.
  // See: https://nextjs.org/docs/app/api-reference/next-config-js/output
  output: "standalone",
};

export default nextConfig;
