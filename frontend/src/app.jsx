import ItemsPage from "./pages/ItemsPage.jsx";

export default function App() {
  return (
    <div className="flex min-h-screen flex-col bg-slate-100">
      <header className="bg-slate-900 text-white shadow">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-4">
          <span className="text-lg font-bold tracking-tight">
            C216 <span className="text-sky-400">Store</span>
          </span>
          <nav aria-label="Principal" className="text-sm text-slate-300">
            Catálogo
          </nav>
        </div>
      </header>

      <div className="flex-1">
        <ItemsPage />
      </div>

      <footer className="bg-slate-900 py-4 text-center text-xs text-slate-400">
        C216 L1 — Prática 6
      </footer>
    </div>
  );
}
