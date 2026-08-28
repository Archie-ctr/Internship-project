/** @type {import('next').NextConfig} */
const nextConfig = {
  // Keep framework configuration centralised so security headers and API
  // rewrites can be introduced clearly during the security phase.
  reactStrictMode: true,
};

export default nextConfig;
