const CAMPO =
  "w-full rounded border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none";

export function Campo({ id, rotulo, erro, children }) {
  return (
    <div>
      <label htmlFor={id} className="mb-1 block text-sm font-medium text-slate-700">
        {rotulo}
      </label>
      {children}
      {erro && (
        <p role="alert" className="mt-1 text-sm text-red-600">
          {erro}
        </p>
      )}
    </div>
  );
}

export { CAMPO };
