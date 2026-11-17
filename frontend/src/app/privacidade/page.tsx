import { metadadosPagina } from "@/lib/seo";
import Link from "next/link";
import DocumentoPublico, { type SecaoDocumento } from "@/components/documento-publico";

export const metadata = metadadosPagina("Política de Privacidade", "Dados, finalidades, fornecedores, autoria, atendimento e limites de privacidade do UnDb.", "/privacidade");

const secoes: SecaoDocumento[] = [
  { id: "responsabilidade", titulo: "1. Projeto e contato", conteudo: <>
    <p>O UnDb é um projeto acadêmico estudantil independente e sem fins lucrativos. Não há vínculo oficial ou endosso institucional comprovado da UnB. Nicolas Zanin acompanha a operação com apoio da equipe apresentada em <Link href="/sobre#equipe">Sobre o UnDb</Link>.</p>
    <p>Para dúvidas, correção de informações, contestação de conteúdo ou pedidos sobre dados pessoais, use <Link href="/contato">Contato e solicitações</Link>, sem necessidade de conta estudantil. A página informa a disponibilidade do recebimento. Não envie senhas nem dados pessoais além do necessário.</p>
  </> },
  { id: "dados", titulo: "2. Dados e finalidades", conteudo: <>
    <ul>
      <li><strong>Conta:</strong> nome, e-mail institucional, senha armazenada como hash, identificador interno, confirmação, papéis e datas são usados para cadastro, autenticação e permissões. Nos novos cadastros, registramos versão dos Termos e data da ciência. Não pedimos matrícula, CPF ou histórico acadêmico.</li>
      <li><strong>Acesso e e-mails:</strong> tokens de confirmação, recuperação e sessão, seus hashes e validades permitem confirmar endereço, recuperar acesso, manter e encerrar sessão. Links de confirmação e recuperação são enviados ao e-mail informado.</li>
      <li><strong>Catálogo:</strong> nomes de docentes, identificadores institucionais quando disponíveis, unidades, disciplinas e ofertas vêm de fontes públicas do SIGAA. Registros de importação e reconciliação ajudam a distinguir identidades, corrigir vínculos e preservar o contexto das ofertas.</li>
      <li><strong>Avaliações:</strong> cinco critérios, professor, disciplina, datas e vínculo interno com a conta permitem impedir duplicatas, substituir envios e calcular indicadores. Comentários opcionais possuem texto, versão e estado de publicação.</li>
      <li><strong>Moderação:</strong> denúncias, motivos, vínculos com contas quando existentes, decisões e datas apoiam a análise e a revisão. Texto livre pode conter informações pessoais de quem escreve ou de terceiros; evite incluí-las.</li>
      <li><strong>Contato:</strong> categoria, referência, descrição, evidência textual, protocolo, hash da chave, complementos, respostas e registros internos permitem atender e acompanhar solicitações. Não há upload de documentos, e-mail obrigatório ou envio desse canal à IA.</li>
      <li><strong>Operação e segurança:</strong> eventos técnicos e dados de conexão, como IP e metadados HTTP tratados pela infraestrutura, podem ser usados para funcionamento, diagnóstico e proteção contra abuso. Os destinos e a retenção dos logs dependem da configuração dos serviços.</li>
    </ul>
    <p>Votos de utilidade vinculam a conta à versão do comentário para controlar um voto por pessoa, troca e retirada. A exibição pública contém apenas contagens; a pessoa autenticada vê o próprio estado. Votos não alteram notas nem moderação e não são denúncias.</p>
  </> },
  { id: "autoria", titulo: "3. O que fica público e quem tem acesso", conteudo: <>
    <p>O catálogo institucional, contagens, critérios agregados a partir de três avaliações e comentários publicados ficam disponíveis publicamente. A consulta pública não divulga nome, e-mail ou identificador da conta avaliadora, nem suas notas individuais. Comentários seguem fluxo próprio e podem aparecer mesmo abaixo do mínimo dos indicadores.</p>
    <p>O vínculo entre conta e avaliação permanece internamente. Não prometemos anonimato absoluto: conteúdo, contexto ou fatos narrados podem permitir identificação. O mínimo de três avaliações também não garante anonimato.</p>
    <p>O acesso privado exige autorização para a função e o registro. Moderadores autorizados acessam informações necessárias à análise, inclusive identidades previstas no fluxo; reconciliadores têm função distinta para o catálogo. A equipe de atendimento tem permissões separadas de leitura e resposta. Acesso à infraestrutura depende das permissões concedidas aos operadores.</p>
    <p>No contato, quem possui protocolo e chave pode consultar respostas e complementos. Triagem e providências internas não são expostas ao solicitante. Não compartilhe a chave publicamente.</p>
  </> },
  { id: "fornecedores", titulo: "4. Serviços e moderação externa", conteudo: <>
    <p>A configuração de hospedagem documentada usa Vercel para o site, Render para a API, Neon para PostgreSQL, Resend para e-mails transacionais e Registro.br para domínio e DNS. Esses serviços participam da entrega ou armazenamento conforme sua função. O Resend recebe destinatário e conteúdo dos e-mails, incluindo os links de confirmação e recuperação.</p>
    <p>Quando a triagem externa está habilitada e o texto é elegível, o comentário é enviado à API de moderação da OpenAI para apoio à classificação. O envio usa o texto integral elegível; filtros locais não garantem remover todos os dados pessoais. Sinais locais de exposição ou outras condições podem impedir o envio e encaminhar o comentário à revisão humana.</p>
    <p>Não informamos uma região única de processamento, prazo de retenção dos provedores ou garantia contratual que não tenha sido confirmada. Os serviços podem envolver processamento fora do Brasil; regiões, suboperadores e condições efetivamente aplicáveis ainda precisam de confirmação operacional. A equipe não apresenta esta página como certificação de conformidade integral.</p>
  </> },
  { id: "sessao", titulo: "5. Cookie, sessão e proteção", conteudo: <>
    <p>A autenticação usa o cookie de sessão <code>undb_session</code>, necessário para reconhecer a conta. Ele é HttpOnly e SameSite=Lax, com Secure na configuração de produção. O banco guarda o hash do token; não usamos armazenamento local do navegador para guardar a sessão.</p>
    <p>A sessão expira após sete dias de inatividade válida; a atividade renova esse período. Sair remove a sessão. O link de confirmação vale 24 horas; o de recuperação, uma hora e uso único. Expirar um link não significa que todos os registros ou e-mails associados foram apagados.</p>
    <p>O controle de tentativas usa contadores compartilhados no PostgreSQL, por operação e conta quando autenticada, com capacidade global para visitantes. Não usa IP como chave. Na falha desse mecanismo, denúncias têm contenção local por processo. Isso não descreve nem elimina os logs dos provedores. Nenhuma medida garante risco zero.</p>
  </> },
  { id: "guarda", titulo: "6. Guarda, descarte e backups", conteudo: <>
    <p>Não há um prazo geral único de eliminação implementado para contas, catálogo, avaliações, histórico do contato e logs. A equipe deve informar o tratamento efetivamente realizado no atendimento de cada pedido, sem confundir retirada de publicação com exclusão completa.</p>
    <p>Na exclusão lógica da conta, nome, senha, papéis, sessões, tokens e ciência dos Termos são removidos; ID, e-mail reservado, datas e estado permanecem. Avaliações e comentários associados ficam ocultos dos agregados e da exibição pública imediatamente e são purgados após sete dias configuráveis, conforme a decisão B/#266. Comentário rejeitado antes de publicar perde o texto e mantém metadados da decisão. Registros privados de operações de acesso têm retenção padrão de seis meses corridos, sem senha, token ou texto de avaliação. Fundamentos e prazos das guardas e execução contínua na hospedagem permanecem pendentes de validação.</p>
    <p>Os ensaios isolados de backup e restauração usam dados sintéticos e não comprovam cobertura, período disponível ou recuperação da hospedagem. O responsável operacional informou fazer backups manuais quando necessário; cobertura e histórico recuperável ainda precisam ser verificados. Não prometemos cópias adicionais, recuperação garantida ou apagamento instantâneo de backups. Antes de reexpor uma restauração, é necessário reaplicar exclusões e revogações posteriores à cópia. O registro operacional para isso ainda não foi confirmado.</p>
  </> },
  { id: "direitos", titulo: "7. Solicitações e revisão", conteudo: <>
    <p>Você pode solicitar informações sobre o tratamento, confirmação e acesso a seus dados, correção, avaliação de eliminação e outros direitos aplicáveis previstos na <a href="https://www2.camara.leg.br/legin/fed/lei/2018/lei-13709-14-agosto-2018-787077-normaatualizada-pl.html" target="_blank" rel="noopener noreferrer">LGPD (abre em outra aba)</a>. Use <Link href="/contato">Contato e solicitações</Link> e descreva apenas o necessário. A equipe pode precisar verificar identidade e legitimidade de forma proporcional antes de transmitir dados privados ou executar o pedido.</p>
    <p>Quando o recebimento está ativo, a página fornece protocolo e chave para acompanhar a resposta e enviar complementos, inclusive pedido de revisão manual de decisão de moderação. O atendimento é manual, com acesso restrito; não há promessa de suporte permanente ou prazo novo nesta política. A indisponibilidade técnica do canal não elimina seus direitos.</p>
    <p>O atendimento do pedido é manual. A exclusão lógica já implementada remove credenciais e sessões, preserva uma conta mínima com e-mail reservado, oculta avaliações/comentários imediatamente e agenda a purga após sete dias configuráveis; não há automação completa do recebimento, verificação e resposta. Até a purga, as notas seguem vinculadas à conta mínima e não entram nos agregados públicos; não há desvinculação. A equipe deve explicar o que foi efetivamente realizado e os limites de cópias de segurança.</p>
    <p>A ciência dos Termos no cadastro registra que você teve conhecimento das condições de participação. Ela não constitui consentimento genérico para qualquer tratamento, nem consentimento em nome de docentes ou de terceiros.</p>
  </> },
  { id: "mudancas", titulo: "8. Atualizações e limites conhecidos", conteudo: <>
    <p>Esta política descreve o funcionamento e as limitações conhecidos na versão indicada. Mudanças serão identificadas por data e versão. Fornecedores, acessos, descarte e backups devem ser atualizados quando os fatos forem confirmados ou mudarem.</p>
    <p>A finalidade acadêmica e o caráter sem fins lucrativos não são garantia de anonimato nem dispensa de cuidado com dados pessoais. Consulte também os <Link href="/termos-de-uso">Termos de Uso</Link> e a <Link href="/sobre#metodologia">metodologia</Link>.</p>
  </> },
];

export default function Privacidade() {
  return <DocumentoPublico titulo="Política de Privacidade" resumo="Quais dados o UnDb usa, para quê, quem pode acessá-los e quais limites ainda existem na operação. Você pode consultar esta página sem criar uma conta." secoes={secoes} />;
}
