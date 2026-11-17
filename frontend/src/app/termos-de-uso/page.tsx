import { metadadosPagina } from "@/lib/seo";
import Link from "next/link";
import DocumentoPublico, { type SecaoDocumento } from "@/components/documento-publico";

export const metadata = metadadosPagina("Termos de Uso", "Participação, crítica acadêmica, moderação e limites do UnDb, projeto estudantil independente e sem fins lucrativos.", "/termos-de-uso");

const secoes: SecaoDocumento[] = [
  { id: "projeto", titulo: "1. Proposta e independência", conteudo: <>
    <p>O UnDb é um projeto acadêmico estudantil independente e sem fins lucrativos, desenvolvido no contexto da disciplina de Métodos de Desenvolvimento de Software. Seu objetivo é compartilhar experiências sobre professores e disciplinas para apoiar escolhas informadas.</p>
    <p>Não há vínculo oficial, autorização ou endosso institucional comprovado da Universidade de Brasília. O UnDb é complementar e não substitui o SIGAA, a matrícula ou os processos oficiais de avaliação da UnB. Ser sem fins lucrativos não elimina as responsabilidades com dados pessoais e com o conteúdo publicado.</p>
  </> },
  { id: "participacao", titulo: "2. Consulta, conta e participação", conteudo: <>
    <p>A consulta ao catálogo, aos resultados agregados e aos comentários publicados é pública. Para registrar avaliações e comentários, é necessário ter conta com endereço @aluno.unb.br confirmado. A confirmação comprova controle do e-mail, não comprova matrícula, frequência nem experiência na disciplina.</p>
    <p>Use sua própria conta, proteja sua senha e não se passe por outra pessoa. Contribua de boa-fé, com experiências acadêmicas pertinentes ao professor e à disciplina. Não use contas ou envios coordenados para fabricar opiniões ou distorcer os resultados.</p>
    <p>Ao criar uma conta, você deve marcar a ciência destes Termos. Registramos a versão e a data no servidor. Contas anteriores não recebem registro retroativo de ciência nem novo bloqueio de acesso nesta etapa. A ciência dos Termos não é autorização genérica para uso de dados: consulte a <Link href="/privacidade">Política de Privacidade</Link>.</p>
  </> },
  { id: "avaliacoes", titulo: "3. Avaliações e seus limites", conteudo: <>
    <p>Cada avaliação se refere a um professor em uma disciplina, com cinco critérios separados: didática, dificuldade, chamada, material e recomendação. Não há nota geral. Um novo envio da mesma conta para o mesmo professor e disciplina substitui o anterior.</p>
    <p>Os critérios agregados aparecem a partir de três avaliações; abaixo disso, são exibidas a contagem e a insuficiência de dados. Dificuldade e chamada são informações neutras. O mínimo de três não garante anonimato. Comentários publicados seguem seu próprio fluxo, inclusive abaixo desse mínimo.</p>
    <p>Opiniões são subjetivas, podem mudar e não garantem veracidade ou representatividade da turma. Consulte a <Link href="/sobre#metodologia">metodologia e os limites</Link> antes de comparar resultados. Votos de utilidade, quando disponíveis, não alteram notas, agregados, denúncias ou decisões de moderação, nem identificam publicamente quem votou.</p>
  </> },
  { id: "conteudo", titulo: "4. Crítica acadêmica e conteúdo proibido", conteudo: <>
    <p>Críticas acadêmicas negativas e respeitosas são permitidas. Por exemplo, “As explicações foram pouco claras para mim” e “O ritmo dificultou meu acompanhamento” expressam experiências que podem ser discutidas sem atacar pessoas.</p>
    <ul><li>Não publique ameaças, discriminação, ataques pessoais ou incentivo à violência.</li><li>Não exponha dados privados seus ou de terceiros, como telefone, endereço, documentos ou informações de saúde. Evite detalhes que identifiquem estudantes.</li><li>Não publique contribuição deliberadamente falsa, falsidade de identidade ou conteúdo sem relação com a experiência acadêmica.</li></ul>
    <p>Discordância do docente, nota negativa ou impopularidade não concedem veto nem causam remoção automática. Uma manifestação fundamentada pode ser analisada sem um número mínimo de pessoas reclamando.</p>
  </> },
  { id: "moderacao", titulo: "5. Moderação e revisão humana", conteudo: <>
    <p>O comentário é opcional. Sem triagem automática habilitada, a publicação depende de aprovação humana. Quando habilitada, a triagem combina filtro local e IA: textos sem sinais podem ser publicados automaticamente; sinais, possível exposição de dados, falhas ou limites mantêm o texto pendente para revisão humana. Não há rejeição automática pela IA. A triagem pode errar e não garante detectar toda violação.</p>
    <p>Denúncias são sobre o texto. O gatilho vigente de 50 contas autenticadas distintas com denúncias abertas sobre a mesma versão suspende o comentário para revisão; isso não é um mínimo para atendimento de um relato fundamentado. Votos de utilidade não são denúncias e não acionam moderação.</p>
    <p>A equipe autorizada pode aprovar ou remover texto conforme as regras, preservando confidencialidade e impedimentos em caso próprio. A moderação do texto não altera as notas. Para contestar uma decisão ou pedir análise, use <Link href="/contato">Contato e solicitações</Link>, indique a referência e a justificativa e acompanhe a resposta com seu protocolo e chave; um complemento permite solicitar revisão manual.</p>
  </> },
  { id: "contato", titulo: "6. Contato e solicitações sobre dados", conteudo: <>
    <p>O <Link href="/contato">canal de contato</Link> não exige conta estudantil. Quando o recebimento está habilitado, fornece protocolo e chave secreta para consulta e complementos. Guarde-os e não os publique. Notas internas do atendimento não são exibidas nessa consulta.</p>
    <p>O atendimento é manual e depende dos responsáveis disponíveis. A página informa eventual suspensão do recebimento; este documento não garante suporte permanente nem prazo novo de resposta. Não envie senhas, documentos completos ou dados desnecessários. A execução de pedidos exige verificação proporcional de identidade e análise do caso.</p>
    <p>Retirar um comentário e excluir uma conta são operações diferentes. A exclusão lógica da conta bloqueia o acesso, remove nome, senha, sessões, links e ciência dos Termos, preservando identificador, e-mail e datas. Avaliações e comentários excluídos ficam ocultos e têm purga após a janela padrão de sete dias; sua execução contínua na hospedagem ainda precisa ser verificada. Isso não significa eliminação integral de dados e cópias externas. Antes de reexpor uma restauração, é necessário considerar exclusões e revogações posteriores ao backup; o registro operacional dessas ações ainda não foi confirmado. Consulte a <Link href="/privacidade">Política de Privacidade</Link>. Não prometemos apagamento instantâneo de backups.</p>
  </> },
  { id: "continuidade", titulo: "7. Disponibilidade e atualizações", conteudo: <>
    <p>A equipe estudantil mantém o projeto conforme sua capacidade e os recursos de hospedagem. Pode haver indisponibilidade, manutenção e suspensão de novas contribuições quando faltarem condições de operação e proteção dos dados. Não há garantia de serviço ininterrupto ou de continuidade permanente.</p>
    <p>Alterações nestes Termos serão identificadas por versão e data nesta página. Esta entrega exige ciência para novos cadastros; não implementa reaceite obrigatório de contas anteriores. Dúvidas e problemas podem ser encaminhados pelo <Link href="/contato">canal de contato</Link>.</p>
  </> },
];

export default function TermosDeUso() {
  return <DocumentoPublico titulo="Termos de Uso" resumo="Regras de participação e limites de uma plataforma feita por estudantes para compartilhar experiências acadêmicas com respeito e contexto." secoes={secoes} />;
}
