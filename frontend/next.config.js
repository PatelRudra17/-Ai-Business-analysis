/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "maps.googleapis.com" },
    ],
  },
};

module.exports = nextConfig;
