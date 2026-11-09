import type { AvaliacaoAgregada } from "@/lib/types/avaliacao";
import type { DisciplinaInstitucional, ProfessorInstitucional } from "@/lib/types/institucional";

// Fixtures exclusivamente visuais. Não representam pessoas, ofertas ou avaliações reais.
export const disciplinasDemo: DisciplinaInstitucional[] = [
  { id: "algoritmos-demo", codigo: "CIC-DEMO", nome: "Algoritmos (exemplo)", departamento: "Computação (exemplo)" },
  { id: "calculo-demo", codigo: "MAT-DEMO", nome: "Cálculo (exemplo)", departamento: "Matemática (exemplo)" },
  { id: "estruturas-demo", codigo: "CIC-DEMO-2", nome: "Estruturas de dados (exemplo)", departamento: "Computação (exemplo)" },
];

export const professoresDemo: ProfessorInstitucional[] = [
  { id: "ana-demo", nome: "Ana (exemplo)", departamento: "Computação (exemplo)" },
  { id: "bruno-demo", nome: "Bruno (exemplo)", departamento: "Computação (exemplo)" },
  { id: "carla-demo", nome: "Carla (exemplo)", departamento: "Computação (exemplo)" },
  { id: "daniel-demo", nome: "Daniel (exemplo)", departamento: "Computação (exemplo)" },
  { id: "elisa-demo", nome: "Elisa (exemplo)", departamento: "Matemática (exemplo)" },
  { id: "ana-matematica-demo", nome: "Ana (exemplo)", departamento: "Matemática (exemplo)" },
];

const [algoritmos, calculo, estruturas] = disciplinasDemo;
const [ana, bruno, carla, daniel, elisa, anaMatematica] = professoresDemo;

// Retratos agregados preparados, sem calcular média, moda ou percentual no frontend.
// Ordem de recomendação preparada segundo a seção 11 dos requisitos: 75%, 50%, insuficientes.
export const comparacoesDemo: Record<string, AvaliacaoAgregada[]> = {
  [algoritmos.id]: [
    { professorId: ana.id, disciplinaId: algoritmos.id, professor: ana, disciplina: algoritmos,
      totalAvaliacoes: 4, dadosSuficientes: true, didatica: 4.0, dificuldade: "MEDIO",
      chamada: true, disponibilizaMaterial: true, qualidadeMaterial: "BOM", recomenda: 75 },
    { professorId: bruno.id, disciplinaId: algoritmos.id, professor: bruno, disciplina: algoritmos,
      totalAvaliacoes: 4, dadosSuficientes: true, didatica: 3.5, dificuldade: "DIFICIL",
      chamada: "CONFLITANTE", disponibilizaMaterial: "CONFLITANTE", qualidadeMaterial: null, recomenda: 50 },
    { professorId: carla.id, disciplinaId: algoritmos.id, professor: carla, disciplina: algoritmos,
      totalAvaliacoes: 2, dadosSuficientes: false },
    { professorId: daniel.id, disciplinaId: algoritmos.id, professor: daniel, disciplina: algoritmos,
      totalAvaliacoes: 0, dadosSuficientes: false },
  ],
  [calculo.id]: [
    { professorId: elisa.id, disciplinaId: calculo.id, professor: elisa, disciplina: calculo,
      totalAvaliacoes: 0, dadosSuficientes: false },
    { professorId: anaMatematica.id, disciplinaId: calculo.id, professor: anaMatematica, disciplina: calculo,
      totalAvaliacoes: 0, dadosSuficientes: false },
  ],
  [estruturas.id]: [
    { professorId: ana.id, disciplinaId: estruturas.id, professor: ana, disciplina: estruturas,
      totalAvaliacoes: 0, dadosSuficientes: false },
  ],
};

// Ordem inicial da fixture; insuficientes continuam no final em ambas as apresentações.
export const apresentacoesDemo: Record<string, AvaliacaoAgregada[]> = {
  [algoritmos.id]: [comparacoesDemo[algoritmos.id][1], comparacoesDemo[algoritmos.id][0], ...comparacoesDemo[algoritmos.id].slice(2)],
  [calculo.id]: comparacoesDemo[calculo.id],
  [estruturas.id]: comparacoesDemo[estruturas.id],
};

export function correspondeBusca(texto: string, termo: string): boolean {
  const normalizar = (valor: string) => valor.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-BR");
  return normalizar(texto).includes(normalizar(termo.trim()));
}
