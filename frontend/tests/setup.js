// Com `globals: true` no vite.config.js, a Testing Library registra sozinha a
// limpeza do DOM entre os testes. Aqui só entram os matchers do jest-dom.
import "@testing-library/jest-dom/vitest";
