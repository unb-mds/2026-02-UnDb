import type { Metadata } from "next";

/** Arte e textos aprovados no complemento da PR #248, sem URL de rota herdável. */
export const metadadosCompartilhamento = {
  metadataBase: new URL("https://undb.app.br"),
  title: "UnDb | Avaliações de professores da UnB",
  description: "Veja o que outros estudantes acharam dos professores e disciplinas da UnB e escolha suas próximas matérias.",
  openGraph: {
    type: "website",
    siteName: "UnDb",
    locale: "pt_BR",
    title: "UnDb | Avaliações de professores da UnB",
    description: "Veja o que outros estudantes acharam dos professores e disciplinas da UnB e escolha suas próximas matérias.",
    images: [{
      url: "https://undb.app.br/undb-preview.png",
      width: 1200,
      height: 630,
      type: "image/png",
      alt: "UnDb — avaliações de professores e disciplinas da UnB",
    }],
  },
  twitter: {
    card: "summary_large_image",
    title: "UnDb | Avaliações de professores da UnB",
    description: "Veja o que outros estudantes acharam dos professores e disciplinas da UnB e escolha suas próximas matérias.",
    images: [{
      url: "https://undb.app.br/undb-preview.png",
      alt: "UnDb — avaliações de professores e disciplinas da UnB",
    }],
  },
} satisfies Metadata;
