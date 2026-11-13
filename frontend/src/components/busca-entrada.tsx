import BuscaNavegacao from "./busca-navegacao";
import Icone from "./icone";

export default function BuscaEntrada() {
  return <div>
    <BuscaNavegacao id="entrada" segmentada />
    <p className="search-help"><Icone nome="shield" pequeno />Informe ao menos 2 caracteres. A consulta é pública em qualquer unidade acadêmica; entre na conta só para avaliar.</p>
  </div>;
}
