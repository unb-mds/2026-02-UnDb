export type Integrante = {
  nome: string;
  github: string;
  linkedin: string | null;
  /** Caminho de imagem em public, por exemplo /equipe/nicolas.jpg. */
  foto: string | null;
  /** Apresentação aprovada pelo integrante, quando disponível. */
  apresentacao: string | null;
};

// Nomes de exibição informados pelo solicitante em 15/11/2026; perfis preservados.
export const equipe: Integrante[] = [
  { nome: "Nicolas Zanin", github: "nicolaszanin06", linkedin: "https://www.linkedin.com/in/nicolas-zanin/", foto: "/equipe/nicolaszanin06.png", apresentacao: null },
  { nome: "Yasmin Loiola", github: "ailoiol", linkedin: "https://www.linkedin.com/in/yasminloiola/", foto: "/equipe/ailoiol.png", apresentacao: null },
  { nome: "Vinicius Gavaldao", github: "ViniGvdo", linkedin: "https://www.linkedin.com/in/vinicius-gavald%C3%A3o-franco-74950a44b/", foto: "/equipe/ViniGvdo.png", apresentacao: null },
  { nome: "Gabriel Araujo", github: "gabrielrdaraujo", linkedin: "https://www.linkedin.com/in/gabriel-araujo-918910236/", foto: "/equipe/gabrielrdaraujo.png", apresentacao: null },
  { nome: "Tiago Vieira", github: "TiagoVieira-596", linkedin: "https://www.linkedin.com/in/tiago-vieira-85a721325/", foto: "/equipe/TiagoVieira-596.jpg", apresentacao: null },
  { nome: "Warlley Medeiros", github: "warlleymedeiros", linkedin: "https://www.linkedin.com/in/warlley-dias-de-medeiros-0b1304354/", foto: "/equipe/warlleymedeiros.png", apresentacao: null },
];
