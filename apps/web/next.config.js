/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ["@protea/types", "@protea/ui"],
  reactStrictMode: true,
};

module.exports = nextConfig;
