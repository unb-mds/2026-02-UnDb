import { Suspense, type ReactNode } from "react";
import { CabecalhoPrototipo, ContaDemoProvider } from "./conta-demo";

export default function PrototipoLayout({ children }: { children: ReactNode }) {
  return <ContaDemoProvider>
    <Suspense fallback={<div className="border-b border-foreground/10 px-4 py-3 text-sm">Carregando navegação do protótipo…</div>}>
      <CabecalhoPrototipo />
    </Suspense>
    {children}
  </ContaDemoProvider>;
}
