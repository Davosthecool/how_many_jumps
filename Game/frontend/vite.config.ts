import { defineConfig, loadEnv } from 'vite';
import path from 'path';

export default defineConfig(({ mode }) => {
  const envDir = path.resolve(__dirname, '../');
  const env = loadEnv(mode, envDir);

  return {
    define: {
      'process.env': env
    },
    envDir
  };
});
