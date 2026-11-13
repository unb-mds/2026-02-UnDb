export type Integrante = {
  nome: string;
  github: string;
  linkedin: string | null;
  /** Caminho de imagem em public, por exemplo /equipe/nicolas.jpg. */
  foto: string | null;
  /** Apresentação aprovada pelo integrante, quando disponível. */
  apresentacao: string | null;
};

// Nomes e perfis conforme a seção Equipe do README do projeto.
export const equipe: Integrante[] = [
  { nome: "Nicolas", github: "nicolaszanin06", linkedin: "https://www.linkedin.com/in/nicolas-zanin/", foto: "/equipe/nicolaszanin06.png", apresentacao: null },
  { nome: "Yasmin", github: "ailoiol", linkedin: null, foto: "/equipe/ailoiol.png", apresentacao: null },
  { nome: "Vinicius", github: "ViniGvdo", linkedin: null, foto: "/equipe/ViniGvdo.png", apresentacao: null },
  { nome: "Gabriel", github: "gabrielrdaraujo", linkedin: "https://www.linkedin.com/in/gabriel-araujo-918910236/", foto: "/equipe/gabrielrdaraujo.png", apresentacao: null },
  { nome: "Tiago", github: "TiagoVieira-596", linkedin: null, foto: "/equipe/TiagoVieira-596.png", apresentacao: null },
  { nome: "Warlley", github: "warlleymedeiros", linkedin: "https://www.linkedin.com/in/warlley-dias-de-medeiros-0b1304354/", foto: "/equipe/warlleymedeiros.png", apresentacao: null },
];
